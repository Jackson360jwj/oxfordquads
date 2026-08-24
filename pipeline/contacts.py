#!/usr/bin/env python3
"""
contacts.py — pull the visitor contact route and any "check before you come"
instruction from each college's own page.

Reads snapshot.json for URLs already resolved by scrape.py, falls back to
sources.json. Writes contacts.json.

Advisory text is classified, not copied: we detect what the college is telling
visitors to do and render it in our own consistent wording.
"""
import json, re, time, sys
import requests
from bs4 import BeautifulSoup
sys.path.insert(0, ".")
from scrape import HEADERS, TIMEOUT, POLITE_DELAY, _body

EMAIL_RE = re.compile(r'\b[\w.+-]+@[\w-]+\.[\w.-]+\b')
PHONE_RE = re.compile(r'(?:\+44\s?\(?0?\)?\s?|\b0)1865[\s.-]?\d{3}[\s.-]?\d{3}\b')
# only trust a number the college states in lodge / porter context — a bare
# number on the page is as likely to be the development office
LODGE_PHONE_RE = re.compile(
    r'(?:lodge|porters?|call|contact|telephone|phone)[^.]{0,70}?'
    r'((?:\+44\s?\(?0?\)?\s?|\b0)1865[\s.-]?\d{3}[\s.-]?\d{3})', re.I)

# which mailbox is the right one to send a visitor to
GOOD_BOX = [("lodge", 10), ("porter", 10), ("visit", 9), ("tourism", 9), ("tours", 8),
            ("reception", 7), ("enquir", 6), ("info", 5), ("office", 4), ("contact", 4)]
BAD_BOX = re.compile(r'admission|alumni|development|jobs?|recruit|webmaster|press|'
                     r'conference|wedding|library|academic|hr@|finance|it@|donat', re.I)

# what the college is asking visitors to do, and how we say it
ADVISORIES = [
    ("call_first",
     re.compile(r"\b(?:call|phone|telephone|ring|contact)\s+(?:the\s+)?"
                r"(?:duty\s+)?(?:porters?'?s?\s+)?(?:lodge|porters?)\b", re.I),
     "The college asks visitors to phone the lodge before setting out."),
    ("check_ahead",
     re.compile(r'(?:contact|check|confirm|email)[^.]{0,70}?'
                r'(?:in advance|before your visit|beforehand|ahead of|prior to|up[- ]to[- ]date)', re.I),
     "Contact the college in advance to confirm it is open."),
    ("short_notice",
     re.compile(r'(?:close|closed|closure)[^.]{0,60}?(?:short notice|without notice|at any time)'
                r'|reserves the right to close', re.I),
     "The college reserves the right to close at short notice."),
    ("groups_book",
     re.compile(r'group[^.]{0,70}?(?:must|should|need to|are asked to)[^.]{0,30}?'
                r'(?:book|arrange|contact|pre-?book)', re.I),
     "Groups must book ahead rather than turning up."),
    ("events_close",
     re.compile(r'clos(?:ed|es|ure)[^.]{0,70}?(?:event|exam|ceremon|conferen|function|service)', re.I),
     "Closes for events, exams and ceremonies during the year."),
]


def best_email(cands):
    best = None
    for e in cands:
        if BAD_BOX.search(e):
            continue
        if not re.search(r'\.ox\.ac\.uk$|\.oxford\.ac\.uk$', e, re.I):
            continue
        score = 0
        for frag, pts in GOOD_BOX:
            if frag in e.split("@")[0].lower():
                score = max(score, pts)
        if score and (best is None or score > best[0]):
            best = (score, e.lower())
    return best[1] if best else None


def harvest(url):
    r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")

    mailtos = [a["href"].split("mailto:")[1].split("?")[0]
               for a in soup.find_all("a", href=True) if a["href"].lower().startswith("mailto:")]
    body = _body(BeautifulSoup(r.text, "lxml"))
    text = " ".join(body.get_text(" ").split())

    emails = mailtos + EMAIL_RE.findall(text)
    phones = [re.sub(r'[\s.-]+', ' ', p).strip() for p in LODGE_PHONE_RE.findall(text)]
    # normalise 01865 279900 / +44 (0)1865 279900 -> 01865 279900
    norm = []
    for p in phones:
        digits = re.sub(r'\D', '', p)
        if digits.startswith("44"):
            digits = "0" + digits[2:]
        if len(digits) == 11:
            norm.append(f"{digits[:5]} {digits[5:]}")

    flags = []
    for key, rx, wording in ADVISORIES:
        m = rx.search(text)
        if m:
            flags.append({"key": key, "say": wording,
                          "evidence": " ".join(m.group(0).split())[:90]})
    return {"email": best_email(emails), "phones": sorted(set(norm)), "advisories": flags}


def main():
    try:
        snap = {r["name"]: r for r in json.load(open("snapshot.json"))}
    except Exception:
        snap = {}
    cols = json.load(open("sources.json"))

    out = []
    for i, c in enumerate(cols, 1):
        url = (snap.get(c["name"], {}).get("url") or c.get("url") or c.get("homepage"))
        rec = {"name": c["name"], "tier": c["tier"], "source": url}
        try:
            rec.update(harvest(url))
            rec["status"] = "ok"
        except Exception as e:
            rec.update(status="error", error=str(e)[:90], email=None, phones=[], advisories=[])
        out.append(rec)
        print(f"[{i:>2}/{len(cols)}] {c['name']:<28} "
              f"{'email ' + rec['email'] if rec.get('email') else 'no email':<34} "
              f"{len(rec.get('advisories', []))} advisories", flush=True)
        time.sleep(POLITE_DELAY)

    json.dump(out, open("contacts.json", "w"), indent=1)
    withe = sum(1 for r in out if r.get("email"))
    witha = sum(1 for r in out if r.get("advisories"))
    print(f"\n{withe}/{len(out)} have a visitor email · {witha}/{len(out)} give a check-first instruction")


if __name__ == "__main__":
    main()
