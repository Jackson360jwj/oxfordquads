#!/usr/bin/env python3
"""
scrape.py — read visitor hours/prices from tier-B college sites, diff vs last run.

  python3 scrape.py            # scrape tier B, report changes
  python3 scrape.py --all      # include tier A (for the periodic audit)
  python3 scrape.py --only "New College"

Writes  snapshot.json  (state)  and  changes.md  (human report).
Exit code 1 if anything changed, so cron/CI can alert on it.
"""
import json, re, sys, time, hashlib, datetime, urllib.parse as up
import requests
from bs4 import BeautifulSoup

UA = "OxfordCollegeAccess/1.0 (visitor-hours aggregator; contact: you@example.com)"
HEADERS = {"User-Agent": UA}
TIMEOUT = 25
POLITE_DELAY = 1.5           # seconds between requests to the same estate

# a line matters if it mentions a time, a price, or a closure
TIME_RE  = re.compile(r'\b\d{1,2}[:.]\d{2}\s*(?:am|pm)?\b|\b\d{1,2}\s*(?:am|pm)\b', re.I)
PRICE_RE = re.compile(r'£\s?\d+(?:\.\d{2})?|\bfree\b|\bno charge\b|\bconcession', re.I)
SHUT_RE  = re.compile(r'\bclos(?:ed|ure|es|ing)\b|\bnot open\b|\bby appointment\b|\bpre-?book', re.I)
KEEP_RE  = re.compile(r'\bopen|\bvisit|\badmission|\bentry|\bticket|\bhours\b|\bclos', re.I)
SEP = r'\s*(?:to|until|till|[-\u2013\u2014&])\s*'
CLOCK = r'(?:\d{1,2}(?:[:.]\d{2})?\s*(?:am|pm)|noon|midday|midnight)'
RANGE_RE = re.compile(
    CLOCK + SEP + CLOCK                                   # 2.00pm to 4.00pm, noon – 5pm
    + r'|' + CLOCK + SEP + r'\d{1,2}(?:[:.]\d{2})?'       # 10am to 12
    + r'|\b\d{1,2}[:.]\d{2}' + SEP + r'\d{1,2}[:.]\d{2}\b', re.I)  # 13:00 to 16:15
MONEY_RE = re.compile(r'£\s?\d')
DROP_RE  = re.compile(r'cookie|newsletter|privacy|copyright|vacanc|instagram|twitter|facebook'
                      r'|conferenc|wedding|b&b|accommodation|term dates|library open'
                      r'|gaudy|reunion|matric|lecture|seminar|webinar|concert|recital', re.I)
# "18 September 2026, 8am-5pm" is an event, not an opening time
EVENT_RE = re.compile(r'\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+20\d{2}', re.I)

VISIT_HINT = re.compile(r'visit|visitor|tourist|opening|plan-your|see-the-college', re.I)


def get(url):
    r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    return r.text


GOOD = re.compile(r'plan[-_ ]your[-_ ]visit|visit[-_ ]us|visiting[-_ ](?:the[-_ ])?college|'
                  r'visitor|tourist|opening[-_ ]times|opening[-_ ]hours|/visit\b|visiting[-_ ]corpus|'
                  r'visiting[-_ ]lincoln|see[-_ ]the[-_ ]college', re.I)
BAD  = re.compile(r'visiting[-_ ]student|study|news|event|undergrad|postgrad|admission|applicant|'
                  r'programme|course|exchange|academic|conference|alumni|library|schools?\b|'
                  r'open[-_ ]day|job|research|fellow', re.I)
GUESS_PATHS = ["/visit", "/visit-us", "/visitors", "/visiting", "/about/visit-us",
               "/about-us/visit-us", "/discover/visiting", "/plan-your-visit"]


def discover(homepage):
    """Find the college's own visitor page. Scores links, then falls back to
    probing the handful of paths Oxford colleges actually use."""
    try:
        soup = BeautifulSoup(get(homepage), "lxml")
    except Exception:
        return None
    host = up.urlparse(homepage).netloc
    best = None
    for a in soup.find_all("a", href=True):
        text = " ".join((a.get_text() or "").split()).lower()
        href = a["href"]
        full = up.urljoin(homepage, href)
        if up.urlparse(full).netloc != host:
            continue
        blob = text + " " + href
        if BAD.search(blob):
            continue
        score = 0
        if GOOD.search(href): score += 3
        if GOOD.search(text): score += 3
        if text in ("visit", "visit us", "visiting", "visitors", "visitor information"): score += 4
        if score and (best is None or score > best[0]):
            best = (score, full)
    if best:
        return best[1]
    for path in GUESS_PATHS:                       # cheap fallback probe
        cand = up.urljoin(homepage, path)
        try:
            time.sleep(0.4)
            if len(signals(get(cand))) >= 2:
                return cand
        except Exception:
            continue
    return None


MAIN_SELECTORS = ["main", "article", "[role=main]", "#main", "#content",
                  ".entry-content", ".page-content", ".content"]


def _body(soup):
    """Some college themes wrap the whole page in <header>, so never strip chrome
    blindly. Prefer a real main-content container; only drop nav/header/footer
    when they hold a minority of the page's text."""
    for tag in soup(["script", "style", "noscript", "form", "svg"]):
        tag.decompose()
    total = len(soup.get_text(strip=True)) or 1
    for sel in MAIN_SELECTORS:
        el = soup.select_one(sel)
        if el and len(el.get_text(strip=True)) > 0.25 * total:
            return el
    for tag in soup(["nav", "header", "footer"]):
        if len(tag.get_text(strip=True)) < 0.4 * total:
            tag.decompose()
    return soup.body or soup


def signals(html):
    """Pull the sentences that actually carry visitor hours / prices / closures."""
    soup = _body(BeautifulSoup(html, "lxml"))
    lines, seen = [], set()
    for el in soup.find_all(["p", "li", "h2", "h3", "h4", "td", "div", "span", "strong", "b", "em"]):
        if el.find(["p", "li", "td"]):        # keep leaf-ish nodes only
            continue
        t = " ".join((el.get_text(" ") or "").split())
        if not (12 <= len(t) <= 320):
            continue
        if DROP_RE.search(t) or EVENT_RE.search(t):
            continue
        hit_time, hit_price, hit_shut = TIME_RE.search(t), PRICE_RE.search(t), SHUT_RE.search(t)
        strong = RANGE_RE.search(t) or MONEY_RE.search(t)
        # a bare "10am to 12pm" or "£7" is self-evidently relevant; anything
        # weaker has to also mention opening, visiting, entry or closure
        if not strong and not ((hit_time or hit_price or hit_shut) and KEEP_RE.search(t)):
            continue
        k = t.lower()
        if k in seen:
            continue
        seen.add(k)
        lines.append({
            "text": t,
            "kind": ("hours" if hit_time else "") + ("/price" if hit_price else "") + ("/closure" if hit_shut else ""),
        })
    return lines[:40]


def strength(lines):
    """How many lines are actually a time range or a price. Event listings and
    staff directories score zero, which is how we catch a wrong landing page."""
    return sum(1 for l in lines if RANGE_RE.search(l["text"]) or MONEY_RE.search(l["text"]))


def fingerprint(lines):
    joined = "\n".join(sorted(l["text"].lower() for l in lines))
    return hashlib.sha256(joined.encode()).hexdigest()[:16]


def scrape(col):
    url = col.get("url") or col.get("homepage")
    rec = {"name": col["name"], "tier": col["tier"], "checked": datetime.datetime.now(datetime.timezone.utc)
           .isoformat(timespec="seconds"), "url": url}
    try:
        html = get(url)
    except Exception as e:
        found = discover(col.get("homepage") or url)
        if not found:
            rec.update(status="unreachable", error=str(e)[:120])
            return rec
        rec["url"] = url = found
        try:
            html = get(url)
        except Exception as e2:
            rec.update(status="unreachable", error=str(e2)[:120])
            return rec

    lines = signals(html)
    if strength(lines) < 2:                  # weak or wrong page — go looking for the real one
        found = discover(col.get("homepage") or url)
        if found and found != url:
            try:
                time.sleep(POLITE_DELAY)
                more = signals(get(found))
                if strength(more) > strength(lines):
                    lines, rec["url"] = more, found
            except Exception:
                pass

    extra = []
    if col.get("closures_url") and col["closures_url"] != rec["url"]:
        try:
            time.sleep(POLITE_DELAY)
            extra = signals(get(col["closures_url"]))[:12]
        except Exception:
            pass

    st = strength(lines)
    rec.update(status="ok" if st >= 2 else ("weak" if st == 1 else "no-visitor-hours"),
               strength=st, lines=lines, closures=extra, fp=fingerprint(lines + extra))
    return rec


def main():
    cols = json.load(open("sources.json"))
    if "--only" in sys.argv:
        want = sys.argv[sys.argv.index("--only") + 1].lower()
        cols = [c for c in cols if want in c["name"].lower()]
    elif "--all" not in sys.argv:
        cols = [c for c in cols if c["tier"] == "B"]

    try:
        prev = {r["name"]: r for r in json.load(open("snapshot.json"))}
    except Exception:
        prev = {}

    out, changed, broken = [], [], []
    for i, c in enumerate(cols, 1):
        rec = scrape(c)
        out.append(rec)
        old = prev.get(c["name"])
        if rec["status"] in ("unreachable", "no-visitor-hours"):
            broken.append(rec)
        elif old and old.get("fp") and old["fp"] != rec["fp"]:
            before = {l["text"] for l in old.get("lines", []) + old.get("closures", [])}
            after = {l["text"] for l in rec["lines"] + rec["closures"]}
            changed.append({"name": c["name"], "added": sorted(after - before)[:6],
                            "removed": sorted(before - after)[:6]})
        print(f"[{i:>2}/{len(cols)}] {c['name']:<28} {rec['status']:<12} "
              f"strength {rec.get('strength', 0)}", flush=True)
        time.sleep(POLITE_DELAY)

    json.dump(out, open("snapshot.json", "w"), indent=1)

    today = datetime.date.today().isoformat()
    md = [f"# Visitor-hours check — {today}", "",
          f"{len(out)} colleges read · {len(changed)} changed · {len(broken)} unreachable", ""]
    if changed:
        md.append("## Changed since last run")
        for ch in changed:
            md.append(f"\n### {ch['name']}")
            for t in ch["added"]:   md.append(f"- **now says:** {t}")
            for t in ch["removed"]: md.append(f"- ~~was:~~ {t}")
        md.append("")
    if broken:
        md.append("## Needs a human")
        for b in broken:
            md.append(f"- **{b['name']}** — {b['status']}: {b.get('error','no visitor content found')}")
        md.append("")
    if not changed and not broken:
        md.append("No changes. Nothing to do.")
    open("changes.md", "w").write("\n".join(md))

    print(f"\n{len(changed)} changed, {len(broken)} unreachable -> changes.md")
    sys.exit(1 if (changed or broken) else 0)


if __name__ == "__main__":
    main()
