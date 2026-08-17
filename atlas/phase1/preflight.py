"""Lightweight preflight verification engine for Project Atlas Phase 1."""

import time
import socket
import requests
from typing import Dict, Any, List
from urllib.parse import urlparse

from atlas.core.config import DEFAULT_USER_AGENT
from atlas.phase1.config import PREFLIGHT_TIMEOUT

def run_preflight_check(domain: str, timeout: int = PREFLIGHT_TIMEOUT) -> Dict[str, Any]:
    """
    Perform non-intrusive preflight checks on a target domain:
    DNS resolution, HTTP/HTTPS redirect tracking, response code, and robots/sitemap detection.
    """
    start_time = time.time()
    res = {
        "domain": domain,
        "dns_resolved": False,
        "dns_ip": None,
        "status": "UNKNOWN",
        "final_url": f"https://{domain}",
        "redirect_count": 0,
        "redirect_chain": [],
        "status_code": None,
        "latency_ms": 0.0,
        "content_type": None,
        "has_robots": False,
        "has_sitemap": False,
        "error": None
    }

    # 1. DNS Resolution
    clean_host = domain.strip().lower()
    try:
        addr_info = socket.getaddrinfo(clean_host, None)
        if addr_info:
            res["dns_resolved"] = True
            res["dns_ip"] = addr_info[0][4][0]
    except socket.gaierror as e:
        res["status"] = "DNS_FAILURE"
        res["error"] = str(e)
        res["latency_ms"] = round((time.time() - start_time) * 1000, 2)
        return res
    except Exception as e:
        res["status"] = "DNS_FAILURE"
        res["error"] = str(e)
        res["latency_ms"] = round((time.time() - start_time) * 1000, 2)
        return res

    # 2. HTTP/HTTPS Availability & Redirect Tracking
    session = requests.Session()
    session.headers.update({"User-Agent": DEFAULT_USER_AGENT})

    target_url = f"https://{clean_host}"
    try:
        resp = session.get(target_url, timeout=timeout, allow_redirects=True, stream=True)
        res["status_code"] = resp.status_code
        res["final_url"] = resp.url
        res["content_type"] = resp.headers.get("content-type", "")

        # Redirect history
        if resp.history:
            res["redirect_count"] = len(resp.history)
            res["redirect_chain"] = [h.url for h in resp.history] + [resp.url]

        res["status"] = "SUCCESS" if resp.status_code < 400 else "HTTP_FAILURE"

    except requests.exceptions.SSLError:
        # Fallback to HTTP
        try:
            target_url = f"http://{clean_host}"
            resp = session.get(target_url, timeout=timeout, allow_redirects=True, stream=True)
            res["status_code"] = resp.status_code
            res["final_url"] = resp.url
            res["content_type"] = resp.headers.get("content-type", "")
            res["status"] = "SUCCESS" if resp.status_code < 400 else "HTTP_FAILURE"
        except Exception as e:
            res["status"] = "CONNECTION_ERROR"
            res["error"] = str(e)
    except requests.exceptions.Timeout:
        res["status"] = "TIMEOUT"
        res["error"] = f"Preflight timeout ({timeout}s exceeded)"
    except Exception as e:
        res["status"] = "CONNECTION_ERROR"
        res["error"] = str(e)

    # 3. Observational Robots.txt & Sitemap check (lightweight HEAD/GET)
    if res["status"] == "SUCCESS":
        parsed_final = urlparse(res["final_url"])
        base_origin = f"{parsed_final.scheme}://{parsed_final.netloc}"
        try:
            r_robots = session.get(f"{base_origin}/robots.txt", timeout=3, stream=True)
            res["has_robots"] = (r_robots.status_code == 200 and "text" in r_robots.headers.get("content-type", ""))
        except Exception:
            pass

        try:
            r_sitemap = session.get(f"{base_origin}/sitemap.xml", timeout=3, stream=True)
            res["has_sitemap"] = (r_sitemap.status_code == 200 and ("xml" in r_sitemap.headers.get("content-type", "") or "text" in r_sitemap.headers.get("content-type", "")))
        except Exception:
            pass

    res["latency_ms"] = round((time.time() - start_time) * 1000, 2)
    return res
