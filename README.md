# Oxford Quads — Railway kit (the SongWeaver pattern)

Repo layout, mirroring how songweaver.co ships:

    repo/
      server.js                 <- Express static server (this kit)
      package.json
      railway.json
      deploy/                   <- the built site (index.html, robots, sitemap, llms, og, favicon)
      pipeline/                 <- scrapers, template, data
      .github/workflows/daily.yml   <- pipeline/github-workflow-daily.yml, moved here

Flow: GitHub repo -> Railway service auto-deploys on push -> Cloudflare DNS
(orange-cloud proxy) on oxfordquads.com in front, exactly like songweaver.co.

Daily data refresh stays in GitHub Actions: it scrapes, rebuilds
deploy/index.html, re-stamps the checked dates and commits — the commit is
what redeploys Railway. Every day's data change is a git commit, so the
provenance trail the site advertises is literally the repo history.

Setup, once:
1. Push this repo to GitHub.
2. Railway -> New Project -> Deploy from GitHub repo. Nixpacks detects Node;
   railway.json sets start command + /healthz healthcheck.
3. Railway -> Settings -> Domains -> add oxfordquads.com; add the CNAME it gives
   you in Cloudflare DNS, proxy ON (orange cloud), like songweaver.co.
4. Enable the GitHub Action; run it once by hand (workflow_dispatch) to see a
   green refresh.

One thing to copy back the other way: songweaver.co has robots.txt and
sitemap.xml but no llms.txt — the one in deploy/ here is a good template.

## Site generator (added 27 Aug 2026)

The single-page template flow was replaced by `generator/build.py`, which reads
`pipeline/data_block.js` (still the curated source of truth the scrape pipeline
maintains) and writes the whole site into `deploy/`: the index plus one page
per college at `/colleges/<name>/`, each with TouristAttraction + FAQPage +
BreadcrumbList JSON-LD, a 404 page, sitemap.xml (44 URLs), robots.txt and
llms.txt. Fonts and Leaflet are self-hosted in `deploy/assets/`.

Rebuild locally:  `python3 generator/build.py`  (needs node on PATH for the
data conversion). The daily workflow runs the same command, so every data
change in data_block.js flows to all 44 pages on the next commit.
`pipeline/site_template.html` and `pipeline/data_block.js`'s geo consumer are
retired from the build; geo.json remains for the pipeline's own use.
