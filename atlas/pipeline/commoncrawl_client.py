"""Common Crawl CDX Index client for historical snapshot analysis."""

import json
import time
import requests
from urllib.parse import quote_plus
from typing import List, Tuple
from atlas.core.config import DEFAULT_USER_AGENT, REQUEST_TIMEOUT_SECONDS
from atlas.core.logger import logger
from atlas.core.models import TimelineEvent

# Representative major Common Crawl indices across time
DEFAULT_CC_INDICES = [
    "CC-MAIN-2024-33",
    "CC-MAIN-2023-50",
    "CC-MAIN-2022-49",
    "CC-MAIN-2020-50",
    "CC-MAIN-2018-51",
    "CC-MAIN-2016-50",
    "CC-MAIN-2014-52"
]

def query_commoncrawl_timeline(url: str, indices=DEFAULT_CC_INDICES) -> Tuple[List[TimelineEvent], dict]:
    """
    Query Common Crawl index servers across multiple historical collections.
    Returns (List[TimelineEvent], summary_stats).
    """
    start_time = time.time()
    events: List[TimelineEvent] = []
    summary = {
        "total_records": 0,
        "indices_checked": len(indices),
        "indices_with_hits": []
    }

    clean_url = url.split("://")[-1]
    encoded_url = quote_plus(clean_url)

    for index_name in indices:
        index_url = f"http://index.commoncrawl.org/{index_name}-index?url={encoded_url}&output=json"
        try:
            resp = requests.get(
                index_url,
                headers={"User-Agent": DEFAULT_USER_AGENT},
                timeout=10
            )
            if resp.status_code == 200 and resp.text.strip():
                lines = resp.text.strip().split("\n")
                records = [json.loads(line) for line in lines if line.strip()]
                if records:
                    summary["indices_with_hits"].append(index_name)
                    for rec in records:
                        ts = rec.get("timestamp", "")
                        status_str = rec.get("status", "200")
                        try:
                            status_code = int(status_str)
                        except ValueError:
                            status_code = 200

                        try:
                            length = int(rec.get("length", 0))
                        except ValueError:
                            length = None

                        dt_iso = ""
                        if len(ts) >= 8:
                            dt_iso = f"{ts[0:4]}-{ts[4:6]}-{ts[6:8]}"
                            if len(ts) >= 14:
                                dt_iso += f"T{ts[8:10]}:{ts[10:12]}:{ts[12:14]}Z"

                        filename = rec.get("filename", "")
                        snapshot_url = f"https://data.commoncrawl.org/{filename}" if filename else None

                        events.append(TimelineEvent(
                            timestamp=ts,
                            datetime_iso=dt_iso,
                            source=f"commoncrawl ({index_name})",
                            status_code=status_code,
                            content_length=length,
                            mime_type=rec.get("mime", ""),
                            digest=rec.get("digest", ""),
                            snapshot_url=snapshot_url,
                            notes=f"Offset: {rec.get('offset', '')}"
                        ))
        except Exception:
            continue

    summary["total_records"] = len(events)
    duration_ms = (time.time() - start_time) * 1000
    logger.log_action("query_commoncrawl_timeline", url, duration_ms, True, extra={"records_found": len(events)})

    return events, summary
