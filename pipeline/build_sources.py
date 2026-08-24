#!/usr/bin/env python3
"""
Build sources.json: which colleges we trust the University page for,
and which we must read from the college's own site.

Tiering is evidence-led, from the 25-college audit:
  A  ox.ac.uk verified or cross-source agreement, AND free entry, AND
     no seasonal hour switch  -> trust ox.ac.uk
  B  anything priced (prices are revised annually and that is where every
     confirmed error appeared), plus disputed, unverified, and corrected
     entries, plus anything with a term/seasonal split -> scrape the college
"""
import json, re, sys

HTML = "/mnt/user-data/outputs/oxford-college-access.html"
src = open(HTML).read()
block = src[src.index("const C = ["):src.index("\n/* ---------------- time in Oxford")]

# pull the fields we need out of the JS object literals
entries = []
for m in re.finditer(r'\{n:"((?:[^"\\]|\\.)*)"', block):
    start = m.start()
    end = block.find('},\n\n', start)
    if end == -1:
        end = len(block)
    seg = block[start:end]
    def field(k, default=None):
        mm = re.search(k + r':"((?:[^"\\]|\\.)*)"', seg)
        return mm.group(1) if mm else default
    price = re.search(r'price:(null|\d+)', seg)
    entries.append({
        "name": m.group(1),
        "web": field("web"),
        "vis": field("vis"),
        "access": field("access"),
        "price": None if (not price or price.group(1) == "null") else int(price.group(1)),
        "seasonal": ("months:" in seg) or ("term:" in seg),
        "audited_ok": bool(re.search(r"[,\s]ok:", seg)),
        "corrected": bool(re.search(r"[,\s]fix:", seg)),
        "disputed": bool(re.search(r"[,\s]dispute:", seg)),
    })

# colleges never independently confirmed during the audit
UNVERIFIED = {"Jesus College", "Lincoln College", "Mansfield College", "St John's College",
              "St Peter's College", "Somerville College", "University College"}

# known-good deep links found during the audit; the scraper discovers the rest
KNOWN = {
    "All Souls College":        "https://www.asc.ox.ac.uk/visiting-college",
    "Balliol College":          "https://www.balliol.ox.ac.uk/visit-balliol",
    "Brasenose College":        "https://www.bnc.ox.ac.uk/about-brasenose/visiting/",
    "Christ Church":            "https://www.chch.ox.ac.uk/visit/tickets-and-information",
    "Corpus Christi College":   "https://www.ccc.ox.ac.uk/visiting-corpus",
    "Exeter College":           "https://www.exeter.ox.ac.uk/contact-us/",
    "Harris Manchester College":"https://www.hmc.ox.ac.uk/",
    "Hertford College":         "https://www.hertford.ox.ac.uk/",
    "Jesus College":            "https://www.jesus.ox.ac.uk/visit-us/",
    "Lincoln College":          "https://www.lincoln.ox.ac.uk/discover/the-college/visiting-lincoln/",
    "Magdalen College":         "https://www.magd.ox.ac.uk/visiting-magdalen-college/",
    "Mansfield College":        "https://www.mansfield.ox.ac.uk/",
    "Merton College":           "https://www.merton.ox.ac.uk/visitor-information",
    "New College":              "https://www.new.ox.ac.uk/visiting-the-college",
    "Oriel College":            "https://www.oriel.ox.ac.uk/",
    "Somerville College":       "https://www.some.ox.ac.uk/",
    "St Catherine's College":   "https://www.stcatz.ox.ac.uk/",
    "St Edmund Hall":           "https://www.seh.ox.ac.uk/",
    "St Hilda's College":       "https://www.st-hildas.ox.ac.uk/",
    "St Hugh's College":        "https://www.st-hughs.ox.ac.uk/",
    "St John's College":        "https://www.sjc.ox.ac.uk/",
    "St Peter's College":       "https://www.spc.ox.ac.uk/",
    "Trinity College":          "https://www.trinity.ox.ac.uk/visiting",
    "University College":       "https://www.univ.ox.ac.uk/",
    "Wadham College":           "https://www.wadham.ox.ac.uk/groups-visiting-wadham-college",
}
# pages that carry date-specific closures: these are the volatile ones
CLOSURES = {
    "New College":      "https://www.new.ox.ac.uk/planned-closures",
    "Christ Church":    "https://www.chch.ox.ac.uk/visit/tickets-and-information",
    "Magdalen College": "https://www.magd.ox.ac.uk/visiting-magdalen-college/",
}

out = []
for e in entries:
    reasons = []
    if e["price"]:                       reasons.append("priced")
    if e["disputed"]:                    reasons.append("sources disagree")
    if e["corrected"]:                   reasons.append("ox.ac.uk was wrong")
    if e["name"] in UNVERIFIED:          reasons.append("never verified")
    if e["seasonal"] and e["access"] == "walkin": reasons.append("seasonal hours")

    tier = "B" if reasons else "A"
    if tier == "A":
        reasons = ["verified at source"] if e["audited_ok"] else \
                  (["both University sources agree"] if e["access"] in ("walkin", "closed")
                   else ["appointment only, low volatility"])

    out.append({
        "name": e["name"],
        "tier": tier,
        "why": reasons,
        "access": e["access"],
        "price": e["price"],
        "authority": "ox.ac.uk" if tier == "A" else "college",
        "url": KNOWN.get(e["name"], e["vis"] or e["web"]),
        "closures_url": CLOSURES.get(e["name"]),
        "homepage": e["web"],
    })

json.dump(out, open("sources.json", "w"), indent=1)
a = [c for c in out if c["tier"] == "A"]
b = [c for c in out if c["tier"] == "B"]
print(f"{len(out)} colleges -> tier A (trust ox.ac.uk): {len(a)} | tier B (scrape college): {len(b)}")
print("\nTIER B, and why:")
for c in sorted(b, key=lambda x: x["name"]):
    print(f"  {c['name']:<28} {', '.join(c['why'])}")
