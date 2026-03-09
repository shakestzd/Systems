#!/usr/bin/env python3
"""Data loader: US states TopoJSON for choropleth maps.

Downloads us-atlas states-10m.json (~35KB) from jsDelivr CDN.
"""
import json
import urllib.request

url = "https://cdn.jsdelivr.net/npm/us-atlas@3/states-10m.json"
with urllib.request.urlopen(url) as r:
    print(r.read().decode())
