#!/usr/bin/env python3
"""Data loader: US states TopoJSON from us-atlas CDN."""
import urllib.request

url = "https://cdn.jsdelivr.net/npm/us-atlas@3/states-10m.json"
with urllib.request.urlopen(url) as r:
    print(r.read().decode())
