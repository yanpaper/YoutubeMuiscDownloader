#!/usr/bin/env python3
"""Validate a YouTube URL (called by download_playlist.bat).

Usage: _validate_url.py <url>
Exit code 0 if URL looks valid, 1 otherwise.
"""
import sys

if len(sys.argv) < 2:
    sys.exit(1)

url = sys.argv[1]
valid_markers = ("list=", "youtu.be/", "watch?v=")
if any(marker in url for marker in valid_markers):
    sys.exit(0)
sys.exit(1)
