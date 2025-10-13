# Chrono-Crawl Archive Explorer

A temporal web archive explorer that journeys through Common Crawl's historical snapshots with a futuristic interface.

![Chrono-Crawl](https://img.shields.io/badge/Chrono--Crawl-Temporal%20Explorer-blue)
![Python](https://img.shields.io/badge/Python-Flask-green)
![Common Crawl](https://img.shields.io/badge/Data-Common%20Crawl-orange)

## 🌟 Overview

Chrono-Crawl is a web application that allows you to explore historical versions of websites through Common Crawl's extensive archive. With a sleek, futuristic interface reminiscent of a time machine control panel, you can navigate through web history as if traveling through time.

## ✨ Features

- **Temporal Navigation**: Browse historical versions of websites from Common Crawl archives
- **Complete Proxy System**: All resources (CSS, JS, images) are routed through the archive
- **Interactive Rendering**: View websites in an isolated iframe with full functionality
- **Modern UI**: Futuristic design with glowing effects and smooth animations
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Data Redundancy**: Automatically attemps retrieval from live for data missing in Common Crawl archive

## 🛠️ Tech Stack

- **Backend**: Python Flask
- **Frontend**: Pure HTML/CSS/JavaScript
- **Archive Access**: Common Crawl API
- **HTML Processing**: BeautifulSoup4
- **Data Handling**: WARCIterator for archive processing

## 🚀 Quick Start

### Prerequisites

```bash
pip install flask requests beautifulsoup4 warcio
```

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd chrono-crawl-explorer
```

2. Run the application:
```bash
python serve.py
```

3. Open your browser to `http://localhost:5000`

## 🎮 Usage

### 1. Temporal Coordinates
- Select a Common Crawl index (timeline)
- Enter the target URL to explore
- Set your user agent identifier
- Click "Initiate Time Jump"

### 2. Temporal Viewer
- View raw HTML content from the archive
- See metadata about the fetched records
- Monitor fetch status with visual indicators

### 3. Temporal Renderer
- Render the archived website in an interactive iframe
- Navigate through links (all routed through Common Crawl)
- View the site as it appeared historically

## 🔧 How It Works

### Archive Processing
1. **Index Lookup**: Queries Common Crawl for URL matches in selected time index
2. **Content Fetching**: Retrieves WARC records from Common Crawl storage
3. **HTML Modification**: Rewrites all resource URLs to proxy through the application
4. **Safe Rendering**: Displays content in sandboxed iframe

### Proxy System
- **Resource Proxy**: Routes CSS, JavaScript, and images through Common Crawl
- **Navigation Proxy**: Handles link clicks and form submissions
- **AJAX Proxy**: Intercepts and proxies dynamic requests

## 🎨 Interface Features

- **Animated Elements**: Pulsing time dials and scanning effects
- **Status Indicators**: Real-time feedback for all operations
- **Tab Navigation**: Organized workflow between coordinates, viewer, and renderer
- **Responsive Design**: Adapts to different screen sizes
- **Dark Theme**: Easy-on-the-eyes futuristic aesthetic

## 📁 Project Structure

```
chrono-crawl-explorer/
|-- serve.py             # Flask backend server
|-- static               # Flask static content directory
|   |-- favicon.ico      # Favicon
|   `-- style.css        # Futuristic styling
`-- templates            # Flask templates directory
    |-- index.html       # Main application interface

```

## 🌐 Common Crawl Integration

The application automatically:
- Fetches available crawl indexes from Common Crawl
- Handles byte-range requests for WARC files
- Processes WARC records to extract HTML content
- Manages cache for efficient repeated access

## 🐛 Troubleshooting

### Common Issues

1. **No Records Found**
   - Try different Common Crawl indexes
   - Check if the site was crawled during the selected timeframe

2. **Rendering Issues**
   - Some modern JavaScript may not execute in archive context
   - Complex CSS might not load correctly from archives
   - Dynamic content dependent on live APIs won't work

3. **Performance**
   - Large sites may take longer to fetch and render
   - Some archives have limited resource availability

## 📄 License

This project is open source and available under the MIT License.

### Third-party components and data:

- Common Crawl data: Used under Common Crawl's terms of use
- Flask: BSD 3-Clause License
- BeautifulSoup4: MIT License  
- warcio: Apache 2.0 License
- Common Crawl API: Respect their terms of service

### Data Usage

This tool accesses Common Crawl archives. Users are responsible for:
- Respecting website terms found in the archives
- Complying with robots.txt directives
- Using data in accordance with applicable laws
- Providing proper attribution to source websites

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

---

**⚡ Powered by Flask & Common Crawl**
