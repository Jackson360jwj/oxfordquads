# How often to re-scrape, and why

Short answer: **daily for the 24 tier-B colleges, weekly for the 19 tier-A ones,
plus a full re-read on about 11 known changeover dates a year.** Daily is not
because the pages change daily — most change a few times a year — but because
one class of change carries no notice at all.

## What actually changes, and how fast

Measured from the audit and the first live scrape:

| Thing | How often | Notice given | Needs |
|---|---|---|---|
| Same-day / short-notice closures | ad hoc, all year | **none** | daily |
| Dated closure lists (Merton, Magdalen, New College) | edited continuously | days to months | daily |
| Term ↔ vacation hours (Trinity, Wadham, Somerville, Exeter) | 6 dates/year | fixed calendar | date-triggered |
| Seasonal hours (New College, Magdalen) | 2–4 dates/year | fixed calendar | date-triggered |
| Admission prices | once a year, **1 August** | weeks | annual + weekly safety net |
| Access policy rewrites (Exeter, Hertford) | rare, unpredictable | none | weekly |
| Building-work closures (Nuffield, St Catherine's, Hertford to 2027) | multi-year | months | weekly |

Two findings pin the schedule down:

- **Merton's own page lists `Monday 24 August` among days the college is closed
  for internal events.** That is today. It appeared on no aggregator. Nothing
  slower than daily catches this.
- **Trinity dates its prices "effective 1 August 2025" and New College dates
  its "From 1st August 2025".** Prices move on a shared annual boundary, so
  1 August is the single most valuable date in the year to re-read everything.

## The schedule

- **Daily, 06:15** — 24 tier-B colleges (~2 minutes, ~30 requests at 1.5s spacing).
- **Weekly, Monday** — all 43 including tier A, to catch policy rewrites and to
  re-check that the University page still agrees with the colleges.
- **Date-triggered** — the day before each term boundary, each seasonal switch,
  and 1 August. Eleven runs a year, in `crontab.example`.

Going faster than daily buys nothing: no college edits a visitor page more than
once a day, and you would just be adding load to their servers for no new
information.

## The limit you cannot scrape past

Colleges close at an hour's notice for degree ceremonies, funerals, exams and
private events, and they announce it on a board at the lodge — not on the web.
Balliol, Trinity, Corpus and Oriel all say in writing to phone before visiting.

So the phone number stays on every card. The scraper's job is to keep the
*published* position accurate; it cannot make it *certain*. Any claim stronger
than "this is what the college published as of 06:15 today" would be a lie,
which is why every record carries its own `checked` timestamp and source URL.

## Coverage, honestly

First live run over the 24 tier-B colleges:

- **11 returned usable hours or prices** — including two that settled disputes:
  - **All Souls** publishes Mon–Fri *and* Sunday 14:00–16:00 → the University
    page was right, its alumni directory wrong.
  - **Merton** publishes `Sunday: noon – 5pm` → University page right again.
  - **Corpus Christi** publishes 14:00–17:00, max 19 → University page **wrong**
    (it says 13:30–16:30, max 20).
- **8 returned a single weak signal** — usable but worth a human glance.
- **8 have no machine-readable visitor page at all**: Christ Church (behind a
  booking widget), Harris Manchester, Hertford, Jesus, Mansfield, St Catherine's,
  St Hugh's, University College.

That last group is the honest ceiling. About a third of colleges simply do not
publish structured visitor hours, and no scraping cadence fixes that — those
entries need a person, once a term.
