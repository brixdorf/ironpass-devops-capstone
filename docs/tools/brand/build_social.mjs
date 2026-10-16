// Builds docs/assets/social-preview.png (1280 x 640) for the GitHub repository.
//   node build_social.mjs <repo-root> <work-dir>
// Run it from a folder where playwright, lucide-static and simple-icons are installed.
import { chromium } from "playwright";
import * as si from "simple-icons";
import fs from "node:fs";
import path from "node:path";

const repo = path.resolve(process.argv[2] || ".");
const work = path.resolve(process.argv[3] || "./brand-work");
fs.mkdirSync(work, { recursive: true });
const fonts = path.join(repo, "frontend/node_modules/@fontsource-variable");
const font = (family, pkg, file) =>
  `@font-face{font-family:'${family}';src:url('file://${fonts}/${pkg}/files/${file}') format('woff2');font-weight:100 900;font-display:block}`;

const logo = fs.readFileSync(path.join(repo, "docs/assets/logo.svg"), "utf8").replace("<svg ", '<svg width="150" height="150" ');
const brands = [
  ["Python", si.siPython], ["FastAPI", si.siFastapi], ["React", si.siReact], ["PostgreSQL", si.siPostgresql], ["Docker", si.siDocker],
  ["Kubernetes", si.siKubernetes], ["Helm", si.siHelm], ["Terraform", si.siTerraform], ["AWS", null], ["GitHub Actions", si.siGithubactions],
  ["Prometheus", si.siPrometheus], ["Grafana", si.siGrafana],
];
const color = { React: "#0A7EA4" };
const cloud = fs.readFileSync("node_modules/lucide-static/icons/cloud.svg", "utf8").replace(/<!--[\s\S]*?-->/g, "").replace("<svg", '<svg style="width:58%;height:58%;color:#0B1020" stroke-width="2"');
const tiles = brands.map(([name, icon]) =>
  icon
    ? `<div class="t" title="${name}"><svg viewBox="0 0 24 24" style="width:58%;height:58%"><path fill="${color[name] || "#" + icon.hex}" d="${icon.path}"/></svg></div>`
    : `<div class="t" style="background:#FF9900" title="${name}">${cloud}</div>`).join("");

const html = `<!doctype html><html><head><meta charset="utf-8"><style>
${font("Unbounded", "unbounded", "unbounded-latin-wght-normal.woff2")}
${font("DM Sans", "dm-sans", "dm-sans-latin-wght-normal.woff2")}
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1280px;height:640px;overflow:hidden}
body{position:relative;background:#0B1020;color:#F5F7FA;font-family:'DM Sans',sans-serif}
.bg{position:absolute;inset:0;background:radial-gradient(circle at 88% 12%,#C6FF3D33 0,transparent 42%),radial-gradient(circle at 6% 100%,#7C4DFF55 0,transparent 45%),radial-gradient(circle at 62% 110%,#FF5D5D30 0,transparent 30%)}
.grid{position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.045) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.045) 1px,transparent 1px);background-size:40px 40px}
.main{position:absolute;left:80px;top:96px;right:80px}
.brand{display:flex;align-items:center;gap:36px}
.word{font-family:'Unbounded',sans-serif;font-weight:700;font-size:112px;line-height:1;color:#C6FF3D;letter-spacing:-1px}
.tag{margin-top:40px;font-size:40px;line-height:1.25;font-weight:500;max-width:1120px}
.sub{margin-top:14px;font-size:26px;color:#9AA4C4}
.row{position:absolute;left:80px;bottom:72px;display:flex;gap:16px}
.t{width:64px;height:64px;border-radius:16px;background:#F5F7FA;display:flex;align-items:center;justify-content:center}
</style></head><body><div class="bg"></div><div class="grid"></div>
<div class="main"><div class="brand">${logo}<div class="word">IronPass</div></div>
<div class="tag">From code on a laptop to a monitored cluster on AWS</div>
<div class="sub">A gym membership app with a full DevOps pipeline</div></div>
<div class="row">${tiles}</div></body></html>`;

const file = path.join(work, "social.html");
fs.writeFileSync(file, html);
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1280, height: 640 }, deviceScaleFactor: 1 });
await page.goto("file://" + file);
await page.evaluate(() => document.fonts.ready);
await page.waitForTimeout(300);
const used = await page.evaluate(() => [...document.fonts].filter((f) => f.status === "loaded").map((f) => f.family));
console.log("fonts loaded:", used.join(", "));
await page.screenshot({ path: path.join(repo, "docs/assets/social-preview.png") });
await browser.close();
