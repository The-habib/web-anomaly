"""Internet Archive Wayback Machine CDX client for temporal analysis."""

import time
import requests
from typing import List, Tuple
from atlas.core.config import DEFAULT_USER_AGENT, REQUEST_TIMEOUT_SECONDS
from atlas.core.logger import logger
from atlas.core.models import TimelineEvent

def query_wayback_timeline(url: str, limit: int = 100) -> Tuple[List[TimelineEvent], dict]:
    """
    Query the Wayback Machine CDX API to retrieve historical snapshots for a URL.
    Returns (List[TimelineEvent], summary_stats).
    """
    start_time = time.time()
    events: List[TimelineEvent] = []
    summary = {
        "total_snapshots": 0,
        "first_seen": None,
        "last_seen": None,
        "status_counts": {}
    }

    # Normalize url for CDX
    clean_url = url.split("://")[-1]
    cdx_url = (
        f"http://web.archive.org/cdx/search/cdx?"
        f"url={clean_url}&output=json&fl=timestamp,original,mimetype,statuscode,digest,length&limit={limit}"
    )

    try:
        resp = requests.get(
            cdx_url,
            headers={"User-Agent": DEFAULT_USER_AGENT},
            timeout=REQUEST_TIMEOUT_SECONDS
        )
        if resp.status_code == 200:
            data = resp.json()
            if len(data) > 1:
                # Row 0 is header: ["timestamp","original","mimetype","statuscode","digest","length"]
                rows = data[1:]
                summary["total_snapshots"] = len(rows)
                
                for row in rows:
                    if len(row) >= 6:
                        ts, orig, mime, status_str, digest, length_str = row[:6]
                        try:
                            status_code = int(status_str) if status_str.isdigit() else 200
                        except ValueError:
                            status_code = 200

                        try:
                            content_len = int(length_str) if length_str.isdigit() else None
                        except ValueError:
                            content_len = None

                        # Convert YYYYMMDDhhmmss to ISO
                        dt_iso = ""
                        if len(ts) >= 8:
                            dt_iso = f"{ts[0:4]}-{ts[4:6]}-{ts[6:8]}"
                            if len(ts) >= 14:
                                dt_iso += f"T{ts[8:10]}:{ts[10:12]}:{ts[12:14]}Z"

                        snapshot_url = f"https://web.archive.org/web/{ts}/{orig}"

                        event = TimelineEvent(
                            timestamp=ts,
                            datetime_iso=dt_iso,
                            source="wayback",
                            status_code=status_code,
                            content_length=content_len,
                            mime_type=mime,
                            digest=digest,
                            snapshot_url=snapshot_url
                        )
                        events.append(event)

                        # Update summary stats
                        summary["status_counts"][str(status_code)] = summary["status_counts"].get(str(status_code), 0) + 1

                if events:
                    summary["first_seen"] = events[0].timestamp
                    summary["last_seen"] = events[-1].timestamp

        duration_ms = (time.time() - start_time) * 1000
        logger.log_action("query_wayback_timeline", url, duration_ms, True, extra={"snapshots_found": len(events)})

    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.log_action("query_wayback_timeline", url, duration_ms, False, error=str(e))

    return events, summary
