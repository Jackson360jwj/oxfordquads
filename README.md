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
