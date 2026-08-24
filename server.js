// Oxford Quads — static server, SongWeaver-pattern (Express on Railway, Cloudflare in front)
const express = require("express");
const path = require("path");
const app = express();
const PORT = process.env.PORT || 3000;
const SITE = path.join(__dirname, "deploy");

app.disable("x-powered-by");
app.use((req, res, next) => {
  res.set("X-Content-Type-Options", "nosniff");
  res.set("Referrer-Policy", "strict-origin-when-cross-origin");
  next();
});

// index.html changes daily — short edge cache; assets are immutable-ish
app.use(express.static(SITE, {
  extensions: ["html"],
  setHeaders(res, filePath) {
    if (filePath.endsWith("index.html"))
      res.set("Cache-Control", "public, max-age=300, stale-while-revalidate=3600");
    else if (/\.(png|svg)$/.test(filePath))
      res.set("Cache-Control", "public, max-age=86400");
    else
      res.set("Cache-Control", "public, max-age=3600");
  },
}));

app.get("/healthz", (_req, res) => res.json({ ok: true, at: new Date().toISOString() }));
app.use((_req, res) => res.status(404).sendFile(path.join(SITE, "index.html")));

app.listen(PORT, () => console.log(`oxfordquads serving ${SITE} on :${PORT}`));
