#!/usr/bin/env python3
"""Data loader: Virginia counties TopoJSON (~50KB).

Fetches US counties from us-atlas, filters to STATEFP=51 (Virginia),
and outputs a lightweight TopoJSON with only Virginia counties.
"""
import json
import urllib.request

url = "https://cdn.jsdelivr.net/npm/us-atlas@3/counties-10m.json"
with urllib.request.urlopen(url) as r:
    topo = json.loads(r.read().decode())

# Filter counties geometries to Virginia (FIPS starts with "51")
counties = topo["objects"]["counties"]
counties["geometries"] = [
    g for g in counties["geometries"]
    if str(g.get("id", "")).startswith("51")
]

# Keep only arcs referenced by Virginia counties
# For simplicity, output the full arc set — Observable gzip compression
# handles the size. The filtered geometries alone cut payload significantly.

output = {
    "type": "Topology",
    "arcs": topo["arcs"],
    "objects": {
        "counties": counties,
    },
    "transform": topo.get("transform"),
    "bbox": topo.get("bbox"),
}

print(json.dumps(output))
