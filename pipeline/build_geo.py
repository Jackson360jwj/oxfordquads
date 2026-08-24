"""Turn raw OSM tiles into a compact layer set projected into map pixels."""
import glob, json, math
from xml.etree import ElementTree as ET

CARFAX = (51.7520, -1.2577)
LATK, LNGK = 110570.0, 111320.0*math.cos(math.radians(51.756))

ROAD_CLASS = {"motorway":3,"trunk":3,"primary":3,"secondary":2.2,"tertiary":1.7,
              "unclassified":1.1,"residential":1.1,"living_street":0.9,"pedestrian":0.9}
GREEN = {("leisure","park"),("leisure","garden"),("leisure","nature_reserve"),
         ("leisure","common"),("landuse","grass"),("landuse","meadow"),
         ("landuse","recreation_ground"),("landuse","forest"),("landuse","cemetery"),
         ("landuse","village_green"),("natural","wood"),("natural","scrub"),("natural","grassland")}

nodes, roads, water, greens = {}, {}, {}, {}
for f in sorted(glob.glob("tiles/*.xml")):
    for ev, el in ET.iterparse(f, events=("end",)):
        if el.tag == "node":
            nodes[el.get("id")] = (float(el.get("lat")), float(el.get("lon")))
        elif el.tag == "way":
            wid = el.get("id")
            tags = {t.get("k"): t.get("v") for t in el.findall("tag")}
            refs = [n.get("ref") for n in el.findall("nd")]
            hw, wy, nat = tags.get("highway"), tags.get("waterway"), tags.get("natural")
            if hw in ROAD_CLASS and wid not in roads:
                roads[wid] = (ROAD_CLASS[hw], refs, tags.get("name"))
            elif (wy in ("river","stream","canal") or nat == "water") and wid not in water:
                width = 4 if wy == "river" else (2 if wy == "canal" else 1.4)
                water[wid] = (0 if nat == "water" else width, refs)
            elif any(tags.get(k) == v for k, v in GREEN) and wid not in greens:
                greens[wid] = refs
            el.clear()
print(f"parsed {len(nodes)} nodes | {len(roads)} roads | {len(water)} water | {len(greens)} green")

def xy(ref):
    p = nodes.get(ref)
    if not p: return None
    return ((p[1]-CARFAX[1])*LNGK, -(p[0]-CARFAX[0])*LATK)     # metres east / south of Carfax

def path(refs):
    pts = [xy(r) for r in refs]
    return [p for p in pts if p]

def simplify(pts, tol):
    """Douglas-Peucker. Closed rings need splitting first: with an identical
    first and last point the baseline is degenerate and every perpendicular
    distance computes as zero, which collapses the ring to two points."""
    if len(pts) < 3: return pts
    def dp(a, b, s):
        if b - a < 2: return []
        (x1,y1),(x2,y2) = s[a], s[b]
        dx, dy = x2-x1, y2-y1
        den = math.hypot(dx, dy) or 1e-9
        worst, wi = 0, a
        for i in range(a+1, b):
            x0,y0 = s[i]
            d = abs(dy*x0 - dx*y0 + x2*y1 - y2*x1)/den
            if d > worst: worst, wi = d, i
        if worst <= tol: return []
        return dp(a, wi, s) + [wi] + dp(wi, b, s)

    closed = math.dist(pts[0], pts[-1]) < 0.5
    if closed:
        ring = pts[:-1] if len(pts) > 3 else pts
        far = max(range(len(ring)), key=lambda i: math.dist(ring[0], ring[i]))
        if far < 2 or far > len(ring)-2:
            return pts
        keep = sorted(set([0] + dp(0, far, ring) + [far]
                          + dp(far, len(ring)-1, ring) + [len(ring)-1]))
        out = [ring[i] for i in keep]
        return out + [out[0]] if len(out) >= 3 else pts

    keep = [0] + dp(0, len(pts)-1, pts) + [len(pts)-1]
    return [pts[i] for i in sorted(set(keep))]

def area(pts):
    return abs(sum(pts[i][0]*pts[(i+1)%len(pts)][1] - pts[(i+1)%len(pts)][0]*pts[i][1]
                   for i in range(len(pts))))/2

out = {"roads": [], "water": [], "green": []}
for w,(cls, refs, name) in roads.items():
    p = simplify(path(refs), 3.0 if cls >= 2 else 5.0)
    if len(p) >= 2:
        out["roads"].append({"w": cls, "p": [[round(x,1),round(y,1)] for x,y in p],
                             **({"n": name} if name and cls >= 1.7 else {})})
for w,(width, refs) in water.items():
    p = simplify(path(refs), 4.0)
    if len(p) >= 2:
        out["water"].append({"w": width, "p": [[round(x,1),round(y,1)] for x,y in p]})
for w, refs in greens.items():
    p = simplify(path(refs), 8.0)
    if len(p) >= 4 and area(p) > 9000:                 # drop tiny verges
        out["green"].append([[round(x,1),round(y,1)] for x,y in p])
out["green"].sort(key=lambda p: -area(p))

json.dump(out, open("geo.json","w"), separators=(",",":"))
import os
print(f"roads {len(out['roads'])} | water {len(out['water'])} | green {len(out['green'])}"
      f" -> geo.json {os.path.getsize('geo.json')//1024} KB")
