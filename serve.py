from flask import Flask, request, jsonify, render_template, Response, send_from_directory
import requests
import json
from urllib.parse import quote_plus, urljoin, urlparse, urlunparse
from warcio.archiveiterator import ArchiveIterator
from bs4 import BeautifulSoup
import re
import time
from datetime import datetime
import os

app = Flask(__name__)

# Cache for Common Crawl records to avoid repeated index lookups
cc_record_cache = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/get-indexes', methods=['GET'])
def get_indexes():
    try:
        # Fetch the Common Crawl index page
        response = requests.get('https://data.commoncrawl.org/crawl-data/index.html')
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all index links in the table
            indexes = []
            table = soup.find('table')
            if table:
                for row in table.find_all('tr')[1:]:  # Skip header row
                    cols = row.find_all('td')
                    if cols:
                        link = cols[0].find('a')
                        if link and link.text.startswith('CC-MAIN-'):
                            indexes.append(link.text.strip('/'))
            
            # Sort indexes in reverse chronological order (newest first)
            indexes.sort(reverse=True)
            
            return jsonify({
                'success': True,
                'indexes': indexes
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Failed to fetch indexes: {response.status_code}'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/fetch-commoncrawl', methods=['POST'])
def fetch_commoncrawl():
    data = request.json
    index_name = data.get('indexName', 'CC-MAIN-2024-33')
    target_url = data.get('targetUrl', 'commoncrawl.org/faq')
    user_agent = data.get('userAgent', 'cc-get-started/1.0 (Example data retrieval script; yourname@example.com)')
    
    # Ensure the URL has a scheme for proper parsing
    if not target_url.startswith(('http://', 'https://')):
        target_url = 'https://' + target_url
    
    server = 'http://index.commoncrawl.org/'
    
    try:
        # Search the Common Crawl Index
        encoded_url = quote_plus(target_url)
        index_url = f'{server}{index_name}-index?url={encoded_url}&output=json'
        response = requests.get(index_url, headers={'user-agent': user_agent})
        
        if response.status_code == 200:
            records = response.text.strip().split('\n')
            records_list = [json.loads(record) for record in records if record.strip()]
            
            if records_list:
                # Fetch the page content from the first record
                content, base_url, record_info = fetch_page_from_cc(records_list, user_agent, target_url)
                
                if content:
                    # Store records in cache for future navigation
                    cache_key = f"{index_name}:{base_url}"
                    cc_record_cache[cache_key] = {
                        'records': records_list,
                        'timestamp': time.time(),
                        'index_name': index_name
                    }
                    
                    # Modify the HTML to route ALL requests through our proxy
                    modified_content = modify_html_for_complete_proxy(
                        content.decode('utf-8', errors='ignore'), 
                        base_url,
                        index_name
                    )
                    
                    return jsonify({
                        'success': True,
                        'recordsFound': len(records_list),
                        'content': modified_content,
                        'baseUrl': base_url,
                        'indexName': index_name
                    })
                else:
                    return jsonify({
                        'success': True,
                        'recordsFound': len(records_list),
                        'content': None,
                        'message': 'No content could be extracted from the records'
                    })
            else:
                return jsonify({
                    'success': True,
                    'recordsFound': 0,
                    'content': None,
                    'message': 'No records found for the specified URL'
                })
        else:
            return jsonify({
                'success': False,
                'error': f'Index server returned status code: {response.status_code}'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

def fetch_page_from_cc(records, user_agent, original_url=None):
    for record in records:
        offset, length = int(record['offset']), int(record['length'])
        s3_url = f'https://data.commoncrawl.org/{record["filename"]}'
        byte_range = f'bytes={offset}-{offset+length-1}'
        
        response = requests.get(
            s3_url,
            headers={'user-agent': user_agent, 'Range': byte_range},
            stream=True
        )
        
        if response.status_code == 206:
            stream = ArchiveIterator(response.raw)
            for warc_record in stream:
                if warc_record.rec_type == 'response':
                    content = warc_record.content_stream().read()
                    # Extract base URL from WARC record
                    target_uri = warc_record.rec_headers.get_header('WARC-Target-URI')
                    record_info = {
                        'filename': record['filename'],
                        'offset': offset,
                        'length': length
                    }
                    return content, target_uri, record_info
        else:
            print(f"Failed to fetch data: {response.status_code}")
    
    return None, None, None

def modify_html_for_complete_proxy(html_content, base_url, index_name):
    """Modify HTML to route ALL resource requests and navigation through our proxy"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Modify all links (navigation) - only process actual Tag objects
    for tag in soup.find_all('a'):
        if hasattr(tag, 'attrs') and tag.get('href'):
            href = tag['href']
            if not href.startswith(('http://', 'https://', '//', '#')):
                # Convert relative URL to absolute
                href = urljoin(base_url, href)
            if href.startswith(('http://', 'https://')):
                # Route through our navigation proxy
                tag['href'] = "javascript:void(0);"  # Remove actual href
                tag['onclick'] = f"navigateToCC('{href}', '{index_name}')"
                if hasattr(tag, 'attrs'):
                    tag['style'] = 'cursor: pointer;'
    
    # Modify all forms (submissions) - only process actual Tag objects
    for form in soup.find_all('form'):
        if hasattr(form, 'attrs') and form.get('action'):
            action = form['action']
            if not action.startswith(('http://', 'https://', '//')):
                action = urljoin(base_url, action)
            if action.startswith(('http://', 'https://')):
                form['action'] = f"/proxy-navigate?index={index_name}&url={quote_plus(action)}"
                form['method'] = 'get'  # Simplify to GET for proxy
        # Add hidden field to preserve index - only if it's a Tag
        if hasattr(form, 'attrs'):
            index_input = soup.new_tag('input')
            index_input['type'] = 'hidden'
            index_input['name'] = 'cc_index'
            index_input['value'] = index_name
            form.append(index_input)
    
    # Modify all resources (images, CSS, JS) - only process actual Tag objects
    for tag in soup.find_all(['img', 'script', 'link']):
        if hasattr(tag, 'attrs'):
            if tag.get('src'):
                src = tag['src']
                if not src.startswith(('http://', 'https://', '//', 'data:')):
                    src = urljoin(base_url, src)
                if src.startswith(('http://', 'https://')):
                    tag['src'] = f"/proxy-resource?index={index_name}&url={quote_plus(src)}"
            
            if tag.get('href') and tag.name == 'link':
                href = tag['href']
                if not href.startswith(('http://', 'https://', '//')):
                    href = urljoin(base_url, href)
                if href.startswith(('http://', 'https://')):
                    tag['href'] = f"/proxy-resource?index={index_name}&url={quote_plus(href)}"
    
    # Modify CSS background images and other resources in style attributes
    for tag in soup.find_all(style=True):
        if hasattr(tag, 'attrs'):
            style = tag['style']
            url_pattern = r'url\([\'"]?([^\)\'"]+)[\'"]?\)'
            def replace_url(match):
                url = match.group(1)
                if not url.startswith(('http://', 'https://', '//', 'data:')):
                    url = urljoin(base_url, url)
                if url.startswith(('http://', 'https://')):
                    return f'url("/proxy-resource?index={index_name}&url={quote_plus(url)}")'
                return match.group(0)
            
            new_style = re.sub(url_pattern, replace_url, style)
            tag['style'] = new_style
    
    # Add JavaScript to handle dynamic navigation and AJAX
    if soup.head:
        script_tag = soup.new_tag('script')
        script_tag.string = f"""
    // Override XMLHttpRequest to proxy AJAX calls
    (function() {{
        var originalXHR = window.XMLHttpRequest;
        function CustomXHR() {{
            var xhr = new originalXHR();
            var originalOpen = xhr.open;
            
            xhr.open = function(method, url, async, user, password) {{
                if (url && url.startsWith('http')) {{
                    // Proxy through Common Crawl
                    url = '/proxy-ajax?url=' + encodeURIComponent(url) + '&index={index_name}';
                }}
                return originalOpen.call(this, method, url, async, user, password);
            }};
            return xhr;
        }}
        window.XMLHttpRequest = CustomXHR;
    }})();

    // Override fetch API
    (function() {{
        var originalFetch = window.fetch;
        window.fetch = function(resource, init) {{
            if (typeof resource === 'string' && resource.startsWith('http')) {{
                resource = '/proxy-ajax?url=' + encodeURIComponent(resource) + '&index={index_name}';
            }}
            return originalFetch(resource, init);
        }};
    }})();

    // Global navigation function
    window.navigateToCC = function(url, index) {{
        parent.postMessage({{
            type: 'CC_NAVIGATE',
            url: url,
            index: index
        }}, '*');
    }};

    // Intercept window.location changes
    (function() {{
        var originalLocation = window.location;
        Object.defineProperty(window, 'location', {{
            get: function() {{
                return originalLocation;
            }},
            set: function(value) {{
                if (value && value.href) {{
                    window.navigateToCC(value.href, '{index_name}');
                }}
            }}
        }});
    }})();
    """
        soup.head.append(script_tag)
    
    return str(soup)

@app.route('/proxy-resource', methods=['GET'])
def proxy_resource():
    """Proxy resource requests from the rendered iframe"""
    resource_url = request.args.get('url')
    index_name = request.args.get('index')
    
    if not resource_url:
        return jsonify({'error': 'No URL provided'}), 400
    
    try:
        # Decode the URL
        resource_url = requests.utils.unquote(resource_url)
        
        # Try to fetch from Common Crawl first
        cc_content = fetch_from_common_crawl(resource_url, index_name)
        if cc_content:
            return cc_content
        
        # Fallback: fetch from live web (with warning)
        print(f"WARNING: Resource not found in Common Crawl, falling back to live: {resource_url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; Chrono-Crawl-Explorer/1.0)'
        }
        
        response = requests.get(resource_url, headers=headers, stream=True)
        
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', 'application/octet-stream')
            
            def generate():
                for chunk in response.iter_content(chunk_size=8192):
                    yield chunk
            
            return Response(
                generate(),
                content_type=content_type,
                headers={
                    'Access-Control-Allow-Origin': '*',
                    'Cache-Control': 'public, max-age=3600',
                    'X-CC-Proxy': 'fallback-live'
                }
            )
        else:
            return jsonify({'error': f'Failed to fetch resource: {response.status_code}'}), response.status_code
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/proxy-navigate', methods=['GET', 'POST'])
def proxy_navigate():
    """Handle form submissions and navigation from iframe"""
    target_url = request.args.get('url') or request.form.get('url')
    index_name = request.args.get('index') or request.form.get('cc_index')
    
    if not target_url:
        return jsonify({'error': 'No URL provided'}), 400
    
    try:
        # Fetch the target page from Common Crawl
        content, base_url, _ = fetch_url_from_cc(target_url, index_name)
        
        if content:
            # Modify the HTML for complete proxying
            modified_content = modify_html_for_complete_proxy(
                content.decode('utf-8', errors='ignore'),
                base_url,
                index_name
            )
            
            return modified_content
        else:
            return jsonify({'error': 'Page not found in Common Crawl archive'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/proxy-ajax', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy_ajax():
    """Proxy AJAX/fetch requests from iframe"""
    target_url = request.args.get('url')
    index_name = request.args.get('index')
    
    if not target_url:
        return jsonify({'error': 'No URL provided'}), 400
    
    try:
        # For AJAX requests, try to fetch from Common Crawl
        content = fetch_from_common_crawl(target_url, index_name)
        if content:
            return content
        
        # If not found in CC, return empty response
        return jsonify({'error': 'Resource not found in Common Crawl archive'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def fetch_url_from_cc(url, index_name, user_agent='chrono-explorer/1.0'):
    """Fetch a URL from Common Crawl"""
    server = 'http://index.commoncrawl.org/'
    encoded_url = quote_plus(url)
    index_url = f'{server}{index_name}-index?url={encoded_url}&output=json'
    
    response = requests.get(index_url, headers={'user-agent': user_agent})
    
    if response.status_code == 200:
        records = response.text.strip().split('\n')
        records_list = [json.loads(record) for record in records if record.strip()]
        
        if records_list:
            content, base_url, record_info = fetch_page_from_cc(records_list, user_agent, url)
            return content, base_url, record_info
    
    return None, None, None

def fetch_from_common_crawl(url, index_name, user_agent='chrono-explorer/1.0'):
    """Fetch any resource from Common Crawl"""
    content, base_url, _ = fetch_url_from_cc(url, index_name, user_agent)
    if content:
        # Determine content type from URL extension or headers
        content_type = 'application/octet-stream'
        if url.endswith(('.css', '.CSS')):
            content_type = 'text/css'
        elif url.endswith(('.js', '.JS')):
            content_type = 'application/javascript'
        elif url.endswith(('.png', '.PNG')):
            content_type = 'image/png'
        elif url.endswith(('.jpg', '.jpeg', '.JPG', '.JPEG')):
            content_type = 'image/jpeg'
        elif url.endswith(('.gif', '.GIF')):
            content_type = 'image/gif'
        elif url.endswith(('.html', '.htm', '.HTML', '.HTM')):
            content_type = 'text/html'
        
        return Response(
            content,
            content_type=content_type,
            headers={
                'Access-Control-Allow-Origin': '*',
                'Cache-Control': 'public, max-age=3600',
                'X-CC-Proxy': 'common-crawl'
            }
        )
    return None

@app.route('/navigate', methods=['POST'])
def navigate():
    """Handle navigation requests from iframe (via postMessage)"""
    data = request.json
    target_url = data.get('url')
    index_name = data.get('index')
    
    if not target_url or not index_name:
        return jsonify({'success': False, 'error': 'Missing URL or index'})
    
    try:
        # Fetch from Common Crawl
        content, base_url, _ = fetch_url_from_cc(target_url, index_name)
        
        if content:
            modified_content = modify_html_for_complete_proxy(
                content.decode('utf-8', errors='ignore'),
                base_url,
                index_name
            )
            
            return jsonify({
                'success': True,
                'content': modified_content,
                'baseUrl': base_url
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Page not found in Common Crawl archive'
            })
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
