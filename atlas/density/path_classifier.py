"""
Deterministic 14-Category Path-Type Classifier for Phase 1.7.
"""

import re
import urllib.parse
from atlas.density.models import PathCategory14

PATH_TYPE_PATTERNS = [
    (PathCategory14.USER_SPACE, re.compile(r"(/~|/~[a-zA-Z0-9_\-\.]+|/(users|faculty|staff|students|members|alumni)/)", re.IGNORECASE)),
    (PathCategory14.LEGACY, re.compile(r"/(legacy|retro|classic|oldversions)/", re.IGNORECASE)),
    (PathCategory14.ARCHIVE, re.compile(r"/(old|archive|archives|history|bak|backup)/", re.IGNORECASE)),
    (PathCategory14.DOCS, re.compile(r"/(doc|docs|documentation|man|rfc|manual|faq|handbook|guide)/", re.IGNORECASE)),
    (PathCategory14.RESEARCH, re.compile(r"/(research|papers|techreports|publications|theses|dissertations)/", re.IGNORECASE)),
    (PathCategory14.SOFTWARE, re.compile(r"/(software|code|src|git|repo|tarballs|cvs|svn)/", re.IGNORECASE)),
    (PathCategory14.PROJECT, re.compile(r"/(project|projects|lab|center|group|initiative)/", re.IGNORECASE)),
    (PathCategory14.FILES, re.compile(r"/(pub|public|files|download|downloads|releases|dist|ftp)/", re.IGNORECASE)),
    (PathCategory14.MEDIA, re.compile(r"/(media|audio|video|sounds|clips|swf|midi|mod|wav)/", re.IGNORECASE)),
    (PathCategory14.BLOG, re.compile(r"/(blog|weblog|posts|post|journal|entry|entries)/", re.IGNORECASE)),
    (PathCategory14.PERSONAL, re.compile(r"/(personal|people|homepages|mysite)/", re.IGNORECASE)),
    (PathCategory14.DIRECTORY, re.compile(r"/(dir|directory|catalog|index|table)/", re.IGNORECASE))
]

def normalize_path(path: str) -> str:
    """Normalize path string while preserving document identity."""
    if not path:
        return "/"
    # Unquote url encoding
    unquoted = urllib.parse.unquote(path)
    # Remove redundant trailing slashes if not root
    if len(unquoted) > 1 and unquoted.endswith("/"):
        unquoted = unquoted.rstrip("/")
    return unquoted

def classify_path_14(path: str) -> PathCategory14:
    """Classify normalized path into exactly one primary category."""
    norm = normalize_path(path)
    if norm in ("/", "/index.html", "/index.htm", "/default.asp", "/default.htm", "/index.php"):
        return PathCategory14.ROOT

    norm_with_slash = norm if norm.endswith("/") else norm + "/"
    if not norm_with_slash.startswith("/"):
        norm_with_slash = "/" + norm_with_slash

    for cat, pattern in PATH_TYPE_PATTERNS:
        if pattern.search(norm_with_slash):
            return cat

    if "/" in norm.strip("/"):
        return PathCategory14.DIRECTORY

    return PathCategory14.OTHER
