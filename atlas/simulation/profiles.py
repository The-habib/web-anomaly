"""Synthetic test profile fixtures for unit testing and offline regression.
NOTE: These profiles are NOT empirical observations.
"""

from typing import Dict, Any

KNOWN_TEST_PROFILES: Dict[str, Dict[str, Any]] = {
    "spacejam_fixture": {
        "domain": "spacejam.com",
        "has_tables": True,
        "has_inline": True,
        "has_frameset": True,
        "has_retro": True,
        "earliest_year": 1996,
        "similarity_score": 0.94,
        "cdx_count": 12500,
        "page_title": "Space Jam Official 1996 Preserved Warner Bros Archive"
    },
    "stallman_fixture": {
        "domain": "stallman.org",
        "has_tables": False,
        "has_inline": True,
        "has_frameset": False,
        "has_retro": True,
        "earliest_year": 1996,
        "similarity_score": 0.96,
        "cdx_count": 8500,
        "page_title": "Richard Stallman's Personal Page"
    },
    "modern_portal_fixture": {
        "domain": "example-modern.edu",
        "has_tables": False,
        "has_inline": False,
        "has_frameset": False,
        "has_retro": False,
        "earliest_year": 2010,
        "similarity_score": 0.15,
        "cdx_count": 45000,
        "page_title": "Modern University Portal",
        "frameworks": ["React", "Next.js"]
    }
}
