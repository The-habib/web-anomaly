"""HTML extraction, metadata parsing, and text extraction module."""

import hashlib
import time
import requests
from bs4 import BeautifulSoup
import trafilatura
from readability import Document

from atlas.core.config import HTML_DIR, METADATA_DIR, DEFAULT_USER_AGENT, REQUEST_TIMEOUT_SECONDS
from atlas.core.logger import logger
from atlas.core.models import ArtifactType, EvidenceArtifact

def fetch_and_extract_html(url: str, output_prefix: str) -> dict:
    """
    Fetch live URL, save raw/rendered HTML, extract metadata, links, headers, and clean text.
    """
    start_time = time.time()
    result = {
        "status_code": 0,
        "headers": {},
        "html_content": "",
        "clean_text": "",
        "readability_title": "",
        "metadata": {},
        "html_artifact": None,
        "metadata_artifact": None,
        "error": None
    }

    try:
        resp = requests.get(
            url,
            headers={"User-Agent": DEFAULT_USER_AGENT},
            timeout=REQUEST_TIMEOUT_SECONDS,
            allow_redirects=True
        )
        result["status_code"] = resp.status_code
        result["headers"] = dict(resp.headers)
        result["html_content"] = resp.text

        # 1. Save HTML Artifact
        html_filename = f"{output_prefix}_rendered.html"
        html_path = HTML_DIR / html_filename
        with open(html_path, "w", encoding="utf-8", errors="replace") as f:
            f.write(resp.text)

        html_bytes = resp.text.encode("utf-8")
        html_sha256 = hashlib.sha256(html_bytes).hexdigest()
        result["html_artifact"] = EvidenceArtifact(
            artifact_id=f"art_html_{output_prefix}",
            artifact_type=ArtifactType.HTML,
            relative_path=str(html_path.relative_to(HTML_DIR.parent.parent)),
            file_name=html_filename,
            sha256=html_sha256,
            size_bytes=len(html_bytes),
            metadata={"status_code": resp.status_code, "final_url": resp.url}
        )

        # 2. Extract Clean Text via Trafilatura
        extracted_text = trafilatura.extract(resp.text) or ""
        result["clean_text"] = extracted_text

        # 3. Readability Analysis
        try:
            doc = Document(resp.text)
            result["readability_title"] = doc.title()
        except Exception:
            result["readability_title"] = ""

        # 4. Parse Metadata with BeautifulSoup
        soup = BeautifulSoup(resp.text, "html.parser")
        title_tag = soup.find("title")
        meta_generator = soup.find("meta", attrs={"name": lambda x: x and x.lower() == "generator"})
        meta_description = soup.find("meta", attrs={"name": lambda x: x and x.lower() == "description"})

        links = [a.get("href") for a in soup.find_all("a", href=True)]
        scripts = [s.get("src") for s in soup.find_all("script", src=True)]
        images = [img.get("src") for img in soup.find_all("img", src=True)]

        metadata_dict = {
            "title": title_tag.get_text(strip=True) if title_tag else "",
            "generator": meta_generator.get("content", "") if meta_generator else "",
            "description": meta_description.get("content", "") if meta_description else "",
            "links_count": len(links),
            "scripts_count": len(scripts),
            "images_count": len(images),
            "doctype": str(soup.contents[0]) if soup.contents and "DOCTYPE" in str(soup.contents[0]) else "",
            "headers": dict(resp.headers)
        }
        result["metadata"] = metadata_dict

        # Save metadata artifact
        meta_filename = f"{output_prefix}_metadata.json"
        meta_path = METADATA_DIR / meta_filename
        import json
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata_dict, f, indent=2)

        with open(meta_path, "rb") as f:
            meta_bytes = f.read()

        result["metadata_artifact"] = EvidenceArtifact(
            artifact_id=f"art_meta_{output_prefix}",
            artifact_type=ArtifactType.METADATA,
            relative_path=str(meta_path.relative_to(METADATA_DIR.parent.parent)),
            file_name=meta_filename,
            sha256=hashlib.sha256(meta_bytes).hexdigest(),
            size_bytes=len(meta_bytes),
            metadata={"fields_extracted": list(metadata_dict.keys())}
        )

        duration_ms = (time.time() - start_time) * 1000
        logger.log_action("fetch_and_extract_html", url, duration_ms, True, extra={"status": resp.status_code})

    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        result["error"] = str(e)
        logger.log_action("fetch_and_extract_html", url, duration_ms, False, error=str(e))

    return result
