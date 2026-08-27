#!/usr/bin/env python3
"""Oxford Quads static site generator.

Source of truth: pipeline/data_block.js (the curated college data the daily
scrape pipeline maintains). This script converts it via node, then writes the
complete deployable site into deploy/: index, 43 college pages, 404, sitemap,
robots.txt, llms.txt, and self-hosted assets.

Run from the repo root or from generator/:  python3 generator/build.py
The daily GitHub Action runs this after the scrape; the commit redeploys.
"""
import json, math, re, html, os, sys, datetime, subprocess, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
SITE = os.environ.get("OUT", os.path.join(ROOT, "deploy"))
DATA_BLOCK = os.path.join(ROOT, "pipeline", "data_block.js")

DOMAIN = "https://oxfordquads.com"
BRAND = "Oxford Quads"
TODAY = datetime.date.today()
TODAY_ISO = TODAY.isoformat()
CHECKED = TODAY.strftime("%d %B %Y").lstrip("0")

# ---------------------------------------------------------------- load data

def load_raw():
    """data_block.js -> list of dicts, via node (same engine the site uses)."""
    script = (
        'const fs=require("fs");'
        f'const src=fs.readFileSync({json.dumps(DATA_BLOCK)},"utf8");'
        'const C=new Function(src+";return C;")();'
        'process.stdout.write(JSON.stringify(C));'
    )
    out = subprocess.run(["node", "-e", script], capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit("node conversion of data_block.js failed:\n" + out.stderr)
    return json.loads(out.stdout)

SLUG_KEEP = {"University College": "university-college", "New College": "new-college"}

def slugify(name):
    if name in SLUG_KEEP:
        return SLUG_KEEP[name]
    s = re.sub(r"^The\s+", "", name)
    s = re.sub(r"\s+College$", "", s)
    s = s.lower().replace("'", "").replace(".", "")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")

ACCESS_MAP = {"walkin": "open", "book": "tours", "appointment": "appointment",
              "restricted": "restricted", "closed": "closed"}
ACCESS_LABEL = {
    "open": "Open to visitors",
    "appointment": "By appointment",
    "tours": "Pre-booked tours",
    "restricted": "Restricted entry",
    "closed": "Closed to visitors",
}

def transform(raw):
    """data_block entry -> internal shape used by templates and the status JS."""
    out = []
    for r in raw:
        rules = []
        for w in r.get("win", []) or []:
            rules.append({
                "days": [7 if d == 0 else d for d in w["days"]],  # 0=Sun -> ISO 7
                "months": w.get("months"),
                "open": w["o"], "close": w["c"],
                "approx": bool(w.get("approx")),
            })
        out.append({
            "name": r["n"], "slug": slugify(r["n"]),
            "street": r["st"], "postcode": r["pc"],
            "address": f'{r["st"]}, Oxford {r["pc"]}',
            "phone": r["tel"], "email": r.get("email"),
            "website": r["web"].rstrip("/"),
            "lat": r["lat"], "lng": r["lng"],
            "access": ACCESS_MAP[r["access"]],
            "pill": r.get("pill"),
            "price_low": r.get("price"),
            "entry_text": r.get("priceT"),
            "hours_text": r["hoursT"],
            "note": r.get("note"),
            "dispute": r.get("dispute"),
            "advice": r.get("advice") or [],
            "tour": r.get("tour"),
            "hall": bool(r.get("hall")), "grad": bool(r.get("grad")),
            "rules": rules,
        })
    return out

C = transform(load_raw())
BY_SLUG = {c["slug"]: c for c in C}

# search aliases: how people actually refer to colleges
ALIASES = {
    "st-edmund-hall": ["teddy hall", "seh"],
    "university-college": ["univ"],
    "lady-margaret-hall": ["lmh"],
    "brasenose": ["bnc"],
    "corpus-christi": ["corpus", "ccc"],
    "st-catherines": ["catz", "st catz", "catherines"],
    "christ-church": ["the house", "christchurch", "christ church college"],
    "regents-park": ["regents"],
    "queens": ["queen's", "the queens college"],
    "new-college": ["new"],
    "wycliffe-hall": ["wycliffe"],
    "st-antonys": ["antonys"],
    "all-souls": ["allsouls"],
}

def search_blob(c):
    return " ".join([c["name"].lower()] + ALIASES.get(c["slug"], []))

def show_price_chip(c):
    """Price chips only where a member of the public can actually pay or walk in."""
    return c["access"] in ("open", "tours") and c.get("entry_text")

def esc(s):
    return html.escape(s, quote=True) if s else ""

def phone_intl(p):
    digits = re.sub(r"\D", "", p)
    return "+44" + digits[1:] if digits.startswith("0") else "+44" + digits

def dist(a, b):
    return math.hypot((a["lat"] - b["lat"]) * 111.0, (a["lng"] - b["lng"]) * 69.0)

def nearby(c, n=3):
    return sorted((o for o in C if o["slug"] != c["slug"]), key=lambda o: dist(c, o))[:n]

def gmaps(c):
    q = (c["name"] + " Oxford").replace(" ", "+")
    return f"https://www.google.com/maps/search/?api=1&query={q}"

def is_free(c):
    return c.get("price_low") == 0

def price_short(c):
    if c.get("entry_text") is None:
        return "See college"
    if is_free(c):
        return "Free"
    if c.get("price_low"):
        return f"From £{c['price_low']}"
    return "Ticketed"

SCHEMA_DAYS = {1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday",
               5: "Friday", 6: "Saturday", 7: "Sunday"}

def status_chip_label(c):
    return c["pill"] or ACCESS_LABEL[c["access"]]

def opening_hours_jsonld(c):
    """Structured hours only for exact, non-seasonal weekly rules."""
    if c["access"] != "open":
        return None
    specs = []
    for r in c["rules"]:
        if r.get("months") or r.get("approx"):
            return None  # seasonal or approximate: page text is authoritative
        specs.append({
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": [SCHEMA_DAYS[d] for d in r["days"]],
            "opens": r["open"], "closes": r["close"],
        })
    return specs or None

def college_jsonld(c):
    url = f"{DOMAIN}/colleges/{c['slug']}/"
    node = {
        "@context": "https://schema.org",
        "@type": "TouristAttraction",
        "name": c["name"], "url": url,
        "description": meta_desc(c),
        "telephone": phone_intl(c["phone"]),
        "address": {"@type": "PostalAddress", "streetAddress": c["street"],
                    "addressLocality": "Oxford", "postalCode": c["postcode"],
                    "addressCountry": "GB"},
        "geo": {"@type": "GeoCoordinates", "latitude": c["lat"], "longitude": c["lng"]},
        "sameAs": [c["website"]],
        "isPartOf": {"@type": "CollegeOrUniversity", "name": "University of Oxford"},
    }
    if c.get("price_low") is not None:
        node["isAccessibleForFree"] = is_free(c)
    ohs = opening_hours_jsonld(c)
    if ohs:
        node["openingHoursSpecification"] = ohs
    if c.get("email"):
        node["email"] = c["email"]
    return node

def breadcrumb_jsonld(c):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": BRAND, "item": DOMAIN + "/"},
                {"@type": "ListItem", "position": 2, "name": c["name"],
                 "item": f"{DOMAIN}/colleges/{c['slug']}/"}]}

def faq_pairs(c):
    qs = []
    open_a = {
        "open": f"Yes. {c['name']} welcomes visitors. Current visitor hours: {c['hours_text']}",
        "appointment": f"Only by appointment. Contact the porters' lodge on {c['phone']} to arrange a visit.",
        "tours": f"Only with a pre-booked tour. {c['hours_text']} Contact the lodge on {c['phone']} to book.",
        "restricted": f"Entry is restricted. {c['hours_text']}",
        "closed": f"No. {c['hours_text']} Check the college website in case this changes.",
    }[c["access"]]
    if c.get("note"):
        open_a += " " + c["note"]
    qs.append((f"Can you visit {c['name']}?", open_a))
    if c.get("entry_text"):
        qs.append((f"How much does it cost to visit {c['name']}?", c["entry_text"] + "."))
    central = "central Oxford, a short walk from Carfax" if c["postcode"].startswith("OX1") \
        else "Oxford, a little way out from the very centre"
    qs.append((f"Where is {c['name']} and how do I get there?",
               f"{c['name']} is at {c['address']}, in {central}. Oxford's centre is compact "
               "and walkable; use the map link on this page for turn-by-turn directions."))
    return qs

def faq_jsonld(pairs):
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q,
                            "acceptedAnswer": {"@type": "Answer", "text": a}}
                           for q, a in pairs]}

def meta_desc(c):
    bits = [f"{c['name']} visitor information"]
    if c["access"] == "open":
        bits.append(f"opening hours: {c['hours_text'].rstrip('.')}")
    else:
        bits.append(status_chip_label(c).lower())
    if c.get("entry_text"):
        entry = c["entry_text"].split("·")[0].strip().rstrip(".")
        bits.append(f"entry: {entry}")
    bits.append("Address, porters' lodge contact and map.")
    d = ". ".join(b[0].upper() + b[1:] for b in bits)
    return (d[:157] + "…") if len(d) > 160 else d

# ---------------------------------------------------------------- shared assets

FONTS = (
    '<link rel="icon" href="/favicon.svg" type="image/svg+xml">'
    '<link rel="preload" href="/assets/fonts/fraunces-latin-standard-normal.woff2" as="font" type="font/woff2" crossorigin>'
    '<link rel="preload" href="/assets/fonts/libre-franklin-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>'
)

FONT_FACE_CSS = """
@font-face{font-family:'Fraunces';font-style:normal;font-display:swap;font-weight:100 900;
  src:url(/assets/fonts/fraunces-latin-standard-normal.woff2) format('woff2-variations');}
@font-face{font-family:'Libre Franklin';font-style:normal;font-display:swap;font-weight:100 900;
  src:url(/assets/fonts/libre-franklin-latin-wght-normal.woff2) format('woff2-variations');}
"""

CSS = r"""
:root{
  --paper:#FBF7EF; --paper-2:#F4EDDE; --card:#FFFFFF;
  --ink:#1A2334; --ink-soft:#44506A; --ink-faint:#6B7692;
  --oxblue:#002147; --stone:#B8934A; --stone-soft:#E9DCBE;
  --line:#E2D9C5; --line-strong:#C9BD9F;
  --open:#1E6E34; --open-bg:#E3F2E4; --shut:#9A2B2B; --shut-bg:#F8E7E4;
  --warn:#8A5A00; --warn-bg:#FBEFD4; --mute:#5A6272; --mute-bg:#ECEDEF;
  --radius:14px; --shadow:0 1px 2px rgba(26,35,52,.06),0 8px 24px -12px rgba(26,35,52,.18);
}
*{margin:0;padding:0;box-sizing:border-box}
html{scroll-behavior:smooth}
body{
  font-family:"Libre Franklin",Segoe UI,Helvetica,Arial,sans-serif;
  background:var(--paper); color:var(--ink);
  font-size:17px; line-height:1.6;
  background-image:radial-gradient(rgba(184,147,74,.05) 1px,transparent 1px);
  background-size:26px 26px;
}
h1,h2,h3{font-family:"Fraunces",Georgia,serif;color:var(--oxblue);line-height:1.15;letter-spacing:-.01em}
a{color:var(--oxblue)}
a:hover{color:var(--stone)}
.wrap{max-width:1080px;margin:0 auto;padding:0 20px}
.skip{position:absolute;left:-999px}.skip:focus{left:10px;top:10px;background:var(--card);padding:8px 14px;z-index:99;border-radius:8px}

header.top{border-bottom:3px double var(--line-strong);background:var(--paper)}
.topbar{display:flex;align-items:center;justify-content:space-between;padding:16px 0;gap:16px;flex-wrap:wrap}
.brand{font-family:"Fraunces",serif;font-weight:720;font-size:1.35rem;color:var(--oxblue);text-decoration:none;display:flex;align-items:center;gap:10px}
.brand .mark{width:30px;height:30px;border:2.5px solid var(--oxblue);border-radius:6px;display:grid;place-items:center;font-size:.8rem;background:var(--stone-soft)}
.crumb{font-size:.9rem;color:var(--ink-faint)}
.crumb a{color:var(--ink-soft);text-decoration:none}

.hero{padding:44px 0 28px}
.hero h1{font-size:clamp(1.9rem,4.6vw,3rem);max-width:21ch}
.hero .lede{margin-top:14px;max-width:62ch;font-size:1.06rem;color:var(--ink-soft)}
.kicker{display:inline-block;font-size:.78rem;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--stone);margin-bottom:10px}
.datestamp{margin-top:14px;font-size:.92rem;color:var(--ink-faint)}
.datestamp strong{color:var(--ink)}

.chip{display:inline-flex;align-items:center;gap:7px;font-size:.85rem;font-weight:600;padding:5px 12px;border-radius:999px;white-space:nowrap}
.chip::before{content:"";width:9px;height:9px;border-radius:50%;background:currentColor;flex:none}
.chip.open{color:var(--open);background:var(--open-bg)}
.chip.shut{color:var(--shut);background:var(--shut-bg)}
.chip.warn{color:var(--warn);background:var(--warn-bg)}
.chip.mute{color:var(--mute);background:var(--mute-bg)}
.tag{display:inline-block;font-size:.72rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-faint);border:1px solid var(--line-strong);border-radius:6px;padding:2px 8px;vertical-align:middle}

.plan{margin-top:20px;display:flex;gap:10px;flex-wrap:wrap;align-items:center;background:var(--card);border:1.5px solid var(--line);border-radius:12px;padding:12px 16px;box-shadow:var(--shadow);max-width:640px}
.plan-label{font-weight:700;color:var(--oxblue);font-size:.95rem}
.plan input{font:inherit;font-size:.92rem;padding:8px 10px;border:1.5px solid var(--line-strong);border-radius:8px;background:var(--paper);color:var(--ink)}
.plan button{font:inherit;font-size:.92rem;font-weight:700;padding:9px 14px;border-radius:8px;border:none;background:var(--oxblue);color:#fff;cursor:pointer}
.plan button.ghost{background:transparent;color:var(--oxblue);border:1.5px solid var(--oxblue)}
.plan-note{margin-top:10px;font-size:.88rem;color:var(--warn);background:var(--warn-bg);border-radius:8px;padding:8px 12px;max-width:620px}
#q{font:inherit;font-size:.92rem;padding:9px 14px;border:1.5px solid var(--line-strong);border-radius:999px;background:var(--card);color:var(--ink);min-width:220px}
#q:focus{outline:2px solid var(--stone);outline-offset:1px}
.filters{display:flex;gap:10px;flex-wrap:wrap;padding:18px 0;position:sticky;top:0;background:linear-gradient(var(--paper) 88%,transparent);z-index:20}
.filters button{font:inherit;font-size:.92rem;font-weight:600;padding:9px 16px;border-radius:999px;border:1.5px solid var(--line-strong);background:var(--card);color:var(--ink-soft);cursor:pointer}
.filters button[aria-pressed="true"]{background:var(--oxblue);border-color:var(--oxblue);color:#fff}
.count-note{align-self:center;font-size:.9rem;color:var(--ink-faint);margin-left:auto}

#map{height:440px;border-radius:var(--radius);border:1.5px solid var(--line-strong);box-shadow:var(--shadow);z-index:1}
.map-note{font-size:.85rem;color:var(--ink-faint);margin-top:8px}
.pin{width:16px;height:16px;border-radius:50%;border:2.5px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,.4)}
.pin.open{background:var(--open)} .pin.shut{background:#B23A3A} .pin.warn{background:#C98A00} .pin.mute{background:#7A8296}
.leaflet-popup-content{font-family:"Libre Franklin",sans-serif;font-size:.95rem}
.leaflet-popup-content a{font-weight:700}

.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:18px;padding:10px 0 30px}
.card{background:var(--card);border:1.5px solid var(--line);border-radius:var(--radius);padding:20px 20px 18px;box-shadow:var(--shadow);display:flex;flex-direction:column;gap:10px;position:relative}
.card h3{font-size:1.22rem}
.card h3 a{text-decoration:none}
.card h3 a::after{content:"";position:absolute;inset:0}
.card .addr{font-size:.9rem;color:var(--ink-faint)}
.card dl{display:grid;grid-template-columns:auto 1fr;gap:4px 12px;font-size:.95rem}
.card dt{font-weight:700;color:var(--stone);font-size:.78rem;letter-spacing:.08em;text-transform:uppercase;padding-top:3px}
.card dd{color:var(--ink-soft)}
.card .foot{margin-top:auto;display:flex;justify-content:space-between;align-items:center;gap:8px}
.price-tag{font-weight:700;font-size:.95rem;color:var(--oxblue)}
.card:hover{border-color:var(--stone)}
.hidden{display:none}

section.band{padding:34px 0;border-top:1.5px solid var(--line)}
.band h2{font-size:clamp(1.4rem,3vw,1.9rem);margin-bottom:14px}
.band p{max-width:68ch;color:var(--ink-soft);margin-bottom:12px}
.band ul.advice{max-width:68ch;color:var(--ink-soft);margin:0 0 12px 22px}
.band ul.advice li{margin-bottom:6px}

.callout{max-width:760px;background:var(--warn-bg);border:1.5px solid #E8D5A3;border-radius:12px;padding:14px 18px;color:#5C4300;font-size:.97rem;margin:18px 0}
.callout strong{color:#4A3600}

.faq details{border:1.5px solid var(--line);border-radius:12px;background:var(--card);margin-bottom:10px;max-width:760px}
.faq summary{cursor:pointer;font-weight:600;padding:14px 18px;color:var(--oxblue)}
.faq details[open] summary{border-bottom:1.5px solid var(--line)}
.faq .a{padding:14px 18px;color:var(--ink-soft)}

.college-head{padding:40px 0 8px}
.college-head h1{font-size:clamp(1.8rem,4.2vw,2.7rem)}
.college-head .sub{margin-top:10px;color:var(--ink-soft);font-size:1.05rem;max-width:60ch}
.status-line{margin:18px 0 6px;display:flex;gap:10px;flex-wrap:wrap;align-items:center}
.facts{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px;margin:24px 0}
.fact{background:var(--card);border:1.5px solid var(--line);border-radius:var(--radius);padding:18px;box-shadow:var(--shadow)}
.fact h2{font-size:.8rem;letter-spacing:.12em;text-transform:uppercase;color:var(--stone);font-family:"Libre Franklin",sans-serif;font-weight:700;margin-bottom:8px}
.fact p{font-size:1rem;color:var(--ink)}
.fact .small{font-size:.88rem;color:var(--ink-faint);margin-top:6px}
.fact a.button{display:inline-block;margin-top:10px;font-weight:700;font-size:.92rem;text-decoration:none;background:var(--oxblue);color:#fff;padding:9px 15px;border-radius:9px}
.fact a.button.ghost{background:transparent;color:var(--oxblue);border:1.5px solid var(--oxblue)}
.nearby{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px}
.nearby a{display:block;background:var(--card);border:1.5px solid var(--line);border-radius:12px;padding:14px 16px;text-decoration:none;box-shadow:var(--shadow)}
.nearby a:hover{border-color:var(--stone)}
.nearby .n{font-family:"Fraunces",serif;font-weight:650;color:var(--oxblue)}
.nearby .d{font-size:.85rem;color:var(--ink-faint);margin-top:2px}

footer.bottom{border-top:3px double var(--line-strong);margin-top:40px;padding:30px 0 40px;font-size:.92rem;color:var(--ink-faint)}
footer.bottom p{max-width:75ch;margin-bottom:10px}
footer.bottom a{color:var(--ink-soft)}
.backlink{display:inline-block;margin:26px 0 0;font-weight:600;text-decoration:none}
@media (max-width:640px){ body{font-size:16px} #map{height:340px} .filters{gap:7px} .filters button{padding:8px 12px;font-size:.86rem} }
@media print{ .filters,#map,.map-note{display:none} body{background:#fff} }
"""

STATUS_JS = r"""
function ukParts(){
  var p = new Intl.DateTimeFormat('en-GB',{timeZone:'Europe/London',weekday:'short',hour:'2-digit',minute:'2-digit',month:'numeric',hour12:false}).formatToParts(new Date());
  var o = {}; p.forEach(function(x){o[x.type]=x.value});
  var days = {Mon:1,Tue:2,Wed:3,Thu:4,Fri:5,Sat:6,Sun:7};
  return {dow:days[o.weekday], hm:parseInt(o.hour,10)*60+parseInt(o.minute,10), month:parseInt(o.month,10)};
}
function dateParts(dstr, tstr){
  var p = dstr.split('-'); var y=+p[0], mo=+p[1], d=+p[2];
  var dow = new Date(Date.UTC(y, mo-1, d)).getUTCDay(); if(dow===0) dow=7;
  var hm = 0;
  if(tstr){ var a=tstr.split(':'); hm=(+a[0])*60+(+a[1]); }
  return {dow:dow, hm:hm, month:mo};
}
function mins(t){ var a=t.split(':'); return parseInt(a[0],10)*60+parseInt(a[1],10); }
function fmt(m){ var h=Math.floor(m/60), mm=m%60; return (h<10?'0':'')+h+':'+(mm<10?'0':'')+mm; }
function collegeStatus(c, when){
  var now = when || ukParts();
  var A = c.access;
  if(A==='closed') return {cls:'shut', label:c.pill||'Closed to visitors'};
  if(A==='appointment') return {cls:'warn', label:c.pill||'By appointment'};
  if(A==='tours') return {cls:'warn', label:c.pill||'Pre-booked tours'};
  if(A==='restricted') return {cls:'mute', label:c.pill||'Restricted entry'};
  var todays = [];
  (c.rules||[]).forEach(function(r){
    if(r.months && r.months.indexOf(now.month)===-1) return;
    if(r.days.indexOf(now.dow)!==-1) todays.push(r);
  });
  var monthShut = (c.rules||[]).length && (c.rules||[]).every(function(r){
    return r.months && r.months.indexOf(now.month)===-1;
  });
  if(monthShut) return {cls:'shut', label:'Closed this month'};
  if(!todays.length) return {cls:'shut', label:'Closed today'};
  todays.sort(function(a,b){return mins(a.open)-mins(b.open);});
  for(var i=0;i<todays.length;i++){
    var r=todays[i], o=mins(r.open), cl=mins(r.close);
    if(now.hm>=o && now.hm<cl)
      return r.approx ? {cls:'open', label:'Likely open until ~'+fmt(cl)}
                      : {cls:'open', label:'Open now until '+fmt(cl)};
    if(now.hm<o)
      return r.approx ? {cls:'shut', label:'Likely opens ~'+fmt(o)}
                      : {cls:'shut', label:'Opens '+fmt(o)+' today'};
  }
  return {cls:'shut', label:'Closed for today'};
}
function applyStatus(el, c, when){
  var s = collegeStatus(c, when);
  el.classList.remove('open','shut','warn','mute');
  el.classList.add('chip', s.cls);
  el.textContent = s.label;
  return s;
}
"""

def head(title, desc, canonical, extra=""):
    return f"""<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:locale" content="en_GB">
<meta property="og:image" content="{DOMAIN}/assets/og-image.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="theme-color" content="#FBF7EF">
{FONTS}
<style>{FONT_FACE_CSS}{CSS}</style>
{extra}
</head>"""

def header_nav(crumb=None):
    crumb_html = (f'<nav class="crumb" aria-label="Breadcrumb"><a href="/">All colleges</a> '
                  f'&rsaquo; {esc(crumb)}</nav>') if crumb else \
        '<nav class="crumb">All 43 colleges &amp; halls, on one page</nav>'
    return f"""<header class="top"><div class="wrap topbar">
<a class="brand" href="/"><span class="mark">OQ</span> Oxford Quads</a>
{crumb_html}
</div></header>"""

SOURCE_NOTE = (f"Opening times, charges and telephone numbers begin from the University of "
               f"Oxford's Visiting the Colleges page and each college's own visitor pages. "
               f"An automated pipeline re-checks the college pages daily and flags changes "
               f"for review; this build is from {CHECKED}. Where official sources disagree, "
               f"the college's page says so rather than papering over it.")

def footer():
    return f"""<footer class="bottom"><div class="wrap">
<p><strong>How far this has been checked.</strong> {esc(SOURCE_NOTE)} Colleges close at short notice for exams, events and ceremonies, so for a special trip it is always worth a call to the porters' lodge first.</p>
<p>Map data &copy; <a href="https://www.openstreetmap.org/copyright" rel="noopener">OpenStreetMap</a> contributors. {BRAND} is an independent guide and is not affiliated with the University of Oxford or any college.</p>
</div></footer>"""

# ---------------------------------------------------------------- college pages

def college_page(c):
    url = f"{DOMAIN}/colleges/{c['slug']}/"
    title = f"{c['name']} Visitor Hours, Tickets & Entry | {BRAND}"
    desc = meta_desc(c)
    pairs = faq_pairs(c)
    jsonld = [college_jsonld(c), breadcrumb_jsonld(c), faq_jsonld(pairs)]
    extra = "".join(f'<script type="application/ld+json">{json.dumps(j, ensure_ascii=False)}</script>' for j in jsonld)
    near = nearby(c)
    cjson = json.dumps({
        "me": {k: c.get(k) for k in ("access", "rules", "pill")},
        "near": [{k: o.get(k) for k in ("slug", "access", "rules", "pill")} for o in near],
    }, ensure_ascii=False)
    near_html = "".join(
        f'<a href="/colleges/{o["slug"]}/"><span class="n">{esc(o["name"])}</span><br>'
        f'<span class="d">{esc(o["street"])}</span><br>'
        f'<span class="chip mute js-near" data-slug="{o["slug"]}">{esc(status_chip_label(o))}</span></a>'
        for o in near)
    email_html = f'<p><a href="mailto:{c["email"]}">{c["email"]}</a></p>' if c.get("email") else ""
    note_html = f'<p class="small">{esc(c["note"])}</p>' if c.get("note") else ""
    entry = esc(c["entry_text"]) if c.get("entry_text") else "Not published. Ask when arranging your visit."
    tag_html = ""
    if c["hall"]:
        tag_html = ' <span class="tag">Permanent private hall</span>'
    elif c["grad"]:
        tag_html = ' <span class="tag">Graduate college</span>'
    tour_html = f' <a class="button ghost" href="{c["tour"]}" rel="noopener">Book a tour</a>' if c.get("tour") and c["access"] == "tours" else ""
    dispute_html = (f'<div class="callout"><strong>Worth knowing:</strong> {esc(c["dispute"])}</div>'
                    if c.get("dispute") else "")
    advice_html = ""
    if c["advice"]:
        items = "".join(f"<li>{esc(a)}</li>" for a in c["advice"])
        advice_html = f'<section class="band"><h2>Before you go</h2><ul class="advice">{items}</ul></section>'
    faq_html = "".join(f'<details><summary>{esc(q)}</summary><div class="a">{esc(a)}</div></details>' for q, a in pairs)
    body = f"""<body>
<a class="skip" href="#main">Skip to content</a>
{header_nav(c['name'])}
<main id="main" class="wrap">
<div class="college-head">
<span class="kicker">Oxford college visitor guide</span>
<h1>Visiting {esc(c['name'])}{tag_html}</h1>
<p class="sub">{esc(c['name'])} on {esc(c['street'])}: current visitor hours, entry prices and how to reach the porters' lodge, so you know before you walk there.</p>
<div class="status-line"><span class="chip mute" id="live-status">{esc(status_chip_label(c))}</span>{f'<span class="chip mute">{esc(price_short(c))}</span>' if show_price_chip(c) else ''}</div>
{dispute_html}
</div>
<div class="facts">
<article class="fact"><h2>Visitor hours</h2><p>{esc(c['hours_text'])}</p>{note_html}</article>
<article class="fact"><h2>Entry price</h2><p>{entry}</p></article>
<article class="fact"><h2>Porters' lodge</h2><p><a href="tel:{phone_intl(c['phone'])}">{esc(c['phone'])}</a></p>{email_html}<p class="small">The lodge is the front door of every college. If in doubt, call ahead.</p></article>
<article class="fact"><h2>Find it</h2><p>{esc(c['address'])}</p><a class="button" href="{gmaps(c)}" rel="noopener">Directions in Google Maps</a> <a class="button ghost" href="{c['website']}" rel="noopener">Official college site</a>{tour_html}</article>
</div>
{advice_html}
<section class="band faq"><h2>Quick answers</h2>{faq_html}</section>
<section class="band"><h2>While you're nearby</h2><p>These are the closest colleges to {esc(c['name'])}, in case its gates are shut when you arrive.</p><div class="nearby">{near_html}</div>
<a class="backlink" href="/">&larr; See which of all 43 colleges are open right now</a></section>
</main>
{footer()}
<script>{STATUS_JS}
var D = {cjson};
applyStatus(document.getElementById('live-status'), D.me);
document.querySelectorAll('.js-near').forEach(function(el){{
  var n = D.near.find(function(x){{return x.slug===el.dataset.slug}});
  if(n) applyStatus(el, n);
}});
</script>
</body>
</html>"""
    return head(title, desc, url, extra) + body

# ---------------------------------------------------------------- index page

def index_page():
    url = DOMAIN + "/"
    title = f"Oxford College Opening Times, Prices & Visitor Access | {BRAND}"
    desc = ("Which Oxford colleges are open today? Live opening status, visitor hours, entry prices and porters' "
            "lodge contacts for all 43 colleges and halls, checked daily against official college pages.")
    free_names = [c["name"] for c in C if is_free(c) and c["access"] == "open"]
    paid = sorted((c for c in C if c.get("price_low") not in (None, 0)), key=lambda x: x["price_low"])
    paid_names = [f"{c['name']} (from £{c['price_low']})" for c in paid]
    site_faq = [
        ("Are Oxford colleges free to visit?",
         f"Many are. {len(free_names)} of the 43 colleges and halls currently let visitors in without charge during their stated hours, including {free_names[0]}, {free_names[1]} and {free_names[2]}. Others charge between £2 and about £20."),
        ("Which Oxford colleges charge for entry?",
         "Ticketed colleges currently include " + ", ".join(paid_names[:6]) + " and Christ Church, which uses a timed online ticket."),
        ("When is the best time of day to visit Oxford colleges?",
         "Afternoons. Most colleges that admit visitors open their gates after about 13:00 or 14:00, once morning teaching is done. Only a handful open in the morning."),
        ("Why was every college closed when I visited?",
         "Colleges are working institutions and close for exams, ceremonies, conferences and holidays, often at short notice. Check the live status on this page on the day, and phone the porters' lodge before making a special trip."),
    ]
    jsonld = [
        {"@context": "https://schema.org", "@type": "WebSite", "name": BRAND, "url": url, "description": desc},
        {"@context": "https://schema.org", "@type": "ItemList",
         "name": "Oxford colleges and permanent private halls: visitor information",
         "numberOfItems": len(C),
         "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": c["name"],
                              "url": f"{DOMAIN}/colleges/{c['slug']}/"} for i, c in enumerate(C)]},
        faq_jsonld(site_faq),
    ]
    extra = ('<link rel="stylesheet" href="/assets/leaflet.css">'
             + "".join(f'<script type="application/ld+json">{json.dumps(j, ensure_ascii=False)}</script>' for j in jsonld))
    cards = []
    for c in C:
        tags = ["all"]
        if is_free(c): tags.append("free")
        if c.get("price_low") not in (None, 0): tags.append("ticketed")
        if c["access"] in ("appointment", "tours"): tags.append("arrange")
        price_html = f'<span class="price-tag">{esc(price_short(c))}</span>' if show_price_chip(c) else ''
        cards.append(f"""<article class="card" data-slug="{c['slug']}" data-tags="{' '.join(tags)}" data-search="{esc(search_blob(c))}">
<h3><a href="/colleges/{c['slug']}/">{esc(c['name'])}</a></h3>
<p class="addr">{esc(c['address'])}</p>
<dl><dt>Hours</dt><dd>{esc(c['hours_text'])}</dd><dt>Entry</dt><dd>{esc(c['entry_text'] or 'Ask when arranging your visit')}</dd></dl>
<div class="foot"><span class="chip mute js-status">{esc(status_chip_label(c))}</span>{price_html}</div>
</article>""")
    data_js = json.dumps(
        [{k: c.get(k) for k in ("name", "slug", "lat", "lng", "access", "rules", "pill")} for c in C],
        ensure_ascii=False)
    faq_html = "".join(f'<details><summary>{esc(q)}</summary><div class="a">{esc(a)}</div></details>' for q, a in site_faq)
    body = f"""<body>
<a class="skip" href="#main">Skip to content</a>
{header_nav()}
<main id="main" class="wrap">
<div class="hero">
<span class="kicker">Checked daily against official college pages · {esc(CHECKED)}</span>
<h1>Which Oxford colleges are open today?</h1>
<p class="lede">Oxford's 39 colleges and 4 permanent private halls each set their own visiting rules, and most gates are shut more often than open. This page shows live opening status, visitor hours, entry prices and porters' lodge contacts for all 43, so you can plan a walking route that actually gets you inside.</p>
<p class="datestamp" id="uk-clock"></p>
<div class="plan">
<span class="plan-label">Planning ahead?</span>
<input type="date" id="plan-date" aria-label="Date of your visit">
<input type="time" id="plan-time" value="14:00" aria-label="Time of your visit, Oxford time">
<button id="plan-go">Check that moment</button>
<button id="plan-now" class="ghost" hidden>Back to now</button>
</div>
<p class="plan-note" id="plan-note" hidden>Expected status from published hours, in Oxford time. Colleges close at short notice for exams and events, so check again nearer the day.</p>
</div>
<div id="map" aria-label="Map of Oxford colleges, coloured by current opening status"></div>
<p class="map-note">Pin colours show live status: green open, red closed, amber tours or appointment, grey restricted. Use each college page for turn-by-turn directions.</p>
<div class="filters" role="group" aria-label="Filter colleges">
<input type="search" id="q" placeholder="Find a college… try Teddy Hall" aria-label="Search colleges by name">
<button data-f="all" aria-pressed="true">All 43</button>
<button data-f="open-now" aria-pressed="false">Open right now</button>
<button data-f="free" aria-pressed="false">Free entry</button>
<button data-f="ticketed" aria-pressed="false">Ticketed</button>
<button data-f="arrange" aria-pressed="false">Tours &amp; appointment</button>
<span class="count-note" id="count-note"></span>
</div>
<div class="grid" id="grid">{''.join(cards)}</div>
<section class="band"><h2>Oxford college visitor opening times, explained</h2>
<p>Every college is a private, working institution: students live behind those gates, and tutors teach in the quads you want to photograph. That is why visitor access is patchy and why it changes with exams, ceremonies and conferences. As a rule of thumb, afternoons beat mornings, out of term beats term time for the famous colleges, and the porters' lodge phone number answers questions no website can.</p>
<p>The classic heavyweights, Christ Church, Magdalen, New College and Trinity, charge for entry and reward the fee. A long list of quieter colleges, from Balliol's neighbours on Broad Street to the Victorian brick of Keble, cost nothing at all. Each college's page here carries its hours, prices, contact details, quick answers and the nearest alternatives if you find the gate shut.</p></section>
<section class="band faq"><h2>Common questions</h2>{faq_html}</section>
</main>
{footer()}
<script src="/assets/leaflet.js"></script>
<script>{STATUS_JS}
var COLLEGES = {data_js};
var CURRENT = null;   // null = live now; otherwise parts from the planner
var statusBySlug = {{}}, markerBySlug = {{}};
var clock = document.getElementById('uk-clock');
var note = document.getElementById('count-note');
var activeFilter = 'all', q = '';

var map = L.map('map', {{scrollWheelZoom:false}}).setView([51.7565,-1.2570], 14);
L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{maxZoom:19, attribution:'&copy; OpenStreetMap contributors'}}).addTo(map);
COLLEGES.forEach(function(c){{
  markerBySlug[c.slug] = L.marker([c.lat, c.lng], {{icon:L.divIcon({{className:'', html:'<div class="pin mute"></div>', iconSize:[16,16], iconAnchor:[8,8]}}), title:c.name}}).addTo(map).bindPopup('');
}});

function applyFilter(){{
  var shown = 0;
  document.querySelectorAll('.card').forEach(function(card){{
    var ok;
    if(activeFilter==='open-now') ok = statusBySlug[card.dataset.slug].cls==='open';
    else ok = card.dataset.tags.split(' ').indexOf(activeFilter)!==-1;
    if(ok && q) ok = card.dataset.search.indexOf(q)!==-1;
    card.classList.toggle('hidden', !ok);
    if(ok) shown++;
  }});
  note.textContent = 'Showing '+shown+' of 43';
}}

function refreshAll(){{
  document.querySelectorAll('.card').forEach(function(card){{
    var c = COLLEGES.find(function(x){{return x.slug===card.dataset.slug}});
    var s = applyStatus(card.querySelector('.js-status'), c, CURRENT);
    if(CURRENT){{
      var el = card.querySelector('.js-status');
      el.textContent = el.textContent
        .replace('Open now until','Open until').replace('Likely open until','Likely open until')
        .replace(/Opens (~?[0-9:]+) today/,'Opens $1 that day').replace(/Likely opens (~?[0-9:]+)/,'Likely opens $1')
        .replace('Closed for today','Closed by then').replace('Closed today','Closed that day');
      s.label = el.textContent;
    }}
    statusBySlug[c.slug] = s;
  }});
  COLLEGES.forEach(function(c){{
    var s = statusBySlug[c.slug], m = markerBySlug[c.slug];
    m.setIcon(L.divIcon({{className:'', html:'<div class="pin '+s.cls+'"></div>', iconSize:[16,16], iconAnchor:[8,8]}}));
    m.setPopupContent('<a href="/colleges/'+c.slug+'/">'+c.name+'</a><br>'+s.label);
  }});
  var openCount = Object.keys(statusBySlug).filter(function(s){{return statusBySlug[s].cls==='open'}}).length;
  var verb = openCount===1 ? 'is' : 'are';
  if(!CURRENT){{
    var ukTime = new Intl.DateTimeFormat('en-GB',{{timeZone:'Europe/London',weekday:'long',hour:'2-digit',minute:'2-digit',hour12:false}}).format(new Date());
    clock.innerHTML = 'In Oxford it is <strong>'+ukTime+'</strong> and <strong>'+openCount+' of 43</strong> '+verb+' open to walk into right now.';
  }} else {{
    clock.innerHTML = 'At that moment, <strong>'+openCount+' of 43</strong> '+verb+' expected to be open to walk into.';
  }}
  applyFilter();
}}

document.querySelectorAll('.filters button').forEach(function(b){{
  b.addEventListener('click', function(){{
    document.querySelectorAll('.filters button').forEach(function(x){{x.setAttribute('aria-pressed','false')}});
    b.setAttribute('aria-pressed','true');
    activeFilter = b.dataset.f;
    applyFilter();
  }});
}});
document.getElementById('q').addEventListener('input', function(){{ q = this.value.toLowerCase().trim(); applyFilter(); }});

var planDate = document.getElementById('plan-date'), planTime = document.getElementById('plan-time');
var planNote = document.getElementById('plan-note'), planNow = document.getElementById('plan-now');
planDate.min = new Date().toISOString().slice(0,10);
document.getElementById('plan-go').addEventListener('click', function(){{
  if(!planDate.value) {{ planDate.focus(); return; }}
  CURRENT = dateParts(planDate.value, planTime.value || '12:00');
  planNote.hidden = false; planNow.hidden = false;
  refreshAll();
}});
planNow.addEventListener('click', function(){{
  CURRENT = null; planNote.hidden = true; planNow.hidden = true;
  refreshAll();
}});
refreshAll();
</script>
</body>
</html>"""
    return head(title, desc, url, extra) + body

# ---------------------------------------------------------------- misc pages

def notfound_page():
    body = f"""<body>
{header_nav('Not found')}
<main class="wrap"><div class="hero">
<h1>That gate is locked</h1>
<p class="lede">This page does not exist, but all 43 Oxford colleges are one click away.</p>
<a class="backlink" href="/">&larr; Back to the full list</a>
</div></main>
{footer()}
</body></html>"""
    return head(f"Page not found | {BRAND}", "Page not found.", DOMAIN + "/404.html") + body

def sitemap():
    urls = [f"{DOMAIN}/"] + [f"{DOMAIN}/colleges/{c['slug']}/" for c in C]
    items = "".join(
        f"<url><loc>{u}</loc><lastmod>{TODAY_ISO}</lastmod>"
        f"<changefreq>{'daily' if u.endswith('.com/') else 'weekly'}</changefreq>"
        f"<priority>{'1.0' if u.endswith('.com/') else '0.8'}</priority></url>"
        for u in urls)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{items}</urlset>\n')

def robots():
    bots = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-User", "PerplexityBot",
            "Google-Extended", "Applebot-Extended", "CCBot", "meta-externalagent"]
    lines = ["# Everything on this site is meant to be read, by people and by machines.",
             "User-agent: *", "Allow: /", ""]
    for b in bots:
        lines += [f"User-agent: {b}", "Allow: /", ""]
    lines.append(f"Sitemap: {DOMAIN}/sitemap.xml")
    return "\n".join(lines) + "\n"

def llms_txt():
    free_n = sum(1 for c in C if is_free(c) and c["access"] == "open")
    return f"""# Oxford Quads ({DOMAIN})

## What this site knows
Visitor access for all 39 University of Oxford colleges and 4 permanent private
halls: current visitor hours, entry prices, porters' lodge phone numbers and
emails, addresses, and whether entry is open, ticketed, tour-only, by
appointment, restricted, or closed. One page per college at
{DOMAIN}/colleges/<name>/, each with schema.org TouristAttraction,
FAQPage and BreadcrumbList JSON-LD. The index at {DOMAIN}/ lists all 43 with a
map and live open/closed status computed in UK time.

## How the data is sourced
Hours, charges and phone numbers begin from the University of Oxford's official
"Visiting the colleges" page and each college's own visitor pages. An automated
pipeline re-checks the college pages daily; this build is from {CHECKED}. Where
official sources disagree, the college's page states the discrepancy openly.

## Caveats an assistant should repeat
- Colleges close at short notice for exams, ceremonies, conferences and
  holidays. For a special trip, phone the porters' lodge first; every college
  page here lists the number.
- {free_n} of the 43 are currently free to walk into during stated hours; the
  famous ones (Christ Church, Magdalen, New College, Trinity) charge.
- Afternoons are far better than mornings: most visitor hours start 13:00-14:00.
- Christ Church requires a timed ticket booked online.

## Key URLs
- {DOMAIN}/ : all 43, live status, map
- {DOMAIN}/colleges/christ-church/ , {DOMAIN}/colleges/magdalen/ ,
  {DOMAIN}/colleges/new-college/ , {DOMAIN}/colleges/trinity/ : the big four
- {DOMAIN}/sitemap.xml
"""

# ---------------------------------------------------------------- write

def main():
    os.makedirs(SITE, exist_ok=True)
    src_assets = os.path.join(HERE, "assets")
    dst_assets = os.path.join(SITE, "assets")
    if os.path.isdir(src_assets):
        shutil.copytree(src_assets, dst_assets, dirs_exist_ok=True)
    # favicon lives at the site root
    fav = os.path.join(dst_assets, "favicon.svg")
    if os.path.exists(fav):
        shutil.move(fav, os.path.join(SITE, "favicon.svg"))
    open(os.path.join(SITE, "index.html"), "w").write(index_page())
    open(os.path.join(SITE, "404.html"), "w").write(notfound_page())
    open(os.path.join(SITE, "sitemap.xml"), "w").write(sitemap())
    open(os.path.join(SITE, "robots.txt"), "w").write(robots())
    open(os.path.join(SITE, "llms.txt"), "w").write(llms_txt())
    for c in C:
        d = os.path.join(SITE, "colleges", c["slug"])
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w").write(college_page(c))
    print(f"Built {2 + len(C)} pages + sitemap + robots + llms.txt into {SITE}")

if __name__ == "__main__":
    main()
