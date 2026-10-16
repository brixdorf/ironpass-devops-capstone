// Builds the picture assets of the presentation: backgrounds, icon tiles, framed screenshots and diagrams.
// Run from a folder where playwright, lucide-static and simple-icons are installed:
//   node assets.mjs <repo-root> <output-dir>
import { chromium } from "playwright";
import fs from "node:fs";
import path from "node:path";
import * as si from "simple-icons";

const [repo = ".", out = "./build"] = process.argv.slice(2);
fs.mkdirSync(out, { recursive: true });
for (const d of ["bg", "icons", "frames", "diagrams"]) fs.mkdirSync(path.join(out, d), { recursive: true });

const C = {
  ink: "#0B1020", panel: "#141B34", line: "#2A3355", white: "#F5F7FA", dim: "#9AA4C4",
  lime: "#C6FF3D", coral: "#FF5D5D", violet: "#7C4DFF", cyan: "#22D3EE", amber: "#FFB547", pink: "#FF6BD6", mint: "#2EE6A6",
};
// one colour for every DevOps stage, used the same way on every slide
const STAGE = { code: C.lime, test: C.cyan, build: C.amber, scan: C.coral, provision: C.violet, deploy: C.pink, monitor: C.mint };
const onColor = (hex) => (hex === C.violet ? C.white : C.ink); // readable text colour on a stage colour

const lucide = (name) => {
  const svg = fs.readFileSync(`node_modules/lucide-static/icons/${name}.svg`, "utf8");
  return svg.replace(/<!--[\s\S]*?-->/g, "");
};

const browser = await chromium.launch();

async function render(html, file, { w, h, scale = 1, transparent = false }) {
  const page = await browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: scale });
  await page.setContent(`<html><head><style>
    *{box-sizing:border-box;margin:0;padding:0}
    html,body{width:${w}px;height:${h}px;background:${transparent ? "transparent" : C.ink};overflow:hidden}
    body{font-family:'DM Sans',sans-serif;color:${C.white}}
    .u{font-family:'Unbounded',sans-serif}
  </style></head><body>${html}</body></html>`);
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: file, omitBackground: transparent });
  await page.close();
}

// ---------- backgrounds (2560 x 1440) ----------
const grid = `background-image:linear-gradient(rgba(255,255,255,.045) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.045) 1px,transparent 1px);background-size:80px 80px;`;
const glow = (x, y, color, size, alpha) => `radial-gradient(circle at ${x}% ${y}%, ${color}${alpha} 0%, transparent ${size}%)`;
// The centre of the two rings on the title slide, in pixels of the 2560 x 1440 background.
// The logo tile on that slide is placed on this same point (build_deck.py reads it from bg/title-rings.json).
const RING = { cx: 2210, cy: 690 };
fs.writeFileSync(`${out}/bg/title-rings.json`, JSON.stringify({ ...RING, width: 2560, height: 1440 }));
const bgs = {
  "grid-lime": `<div style="position:absolute;inset:0;background:${glow(92, 8, C.lime, 38, "22")},${C.ink};"></div><div style="position:absolute;inset:0;${grid}"></div>`,
  "grid-cyan": `<div style="position:absolute;inset:0;background:${glow(6, 95, C.cyan, 40, "1f")},${glow(95, 5, C.violet, 30, "18")},${C.ink};"></div><div style="position:absolute;inset:0;${grid}"></div>`,
  "grid-coral": `<div style="position:absolute;inset:0;background:${glow(95, 95, C.coral, 40, "20")},${C.ink};"></div><div style="position:absolute;inset:0;${grid}"></div>`,
  "grid-violet": `<div style="position:absolute;inset:0;background:${glow(10, 10, C.violet, 45, "40")},${glow(95, 95, C.cyan, 30, "14")},${C.ink};"></div><div style="position:absolute;inset:0;${grid}"></div>`,
  "grid-mint": `<div style="position:absolute;inset:0;background:${glow(90, 90, C.mint, 40, "1c")},${glow(8, 8, C.violet, 25, "18")},${C.ink};"></div><div style="position:absolute;inset:0;${grid}"></div>`,
  "grid-pink": `<div style="position:absolute;inset:0;background:${glow(92, 12, C.pink, 38, "1c")},${glow(5, 90, C.violet, 30, "20")},${C.ink};"></div><div style="position:absolute;inset:0;${grid}"></div>`,
  title: `<div style="position:absolute;inset:0;background:${glow(82, 40, C.lime, 42, "40")},${glow(8, 95, C.violet, 45, "55")},${glow(60, 100, C.coral, 25, "30")},${C.ink};"></div><div style="position:absolute;inset:0;${grid}"></div>
    <div style="position:absolute;left:${RING.cx - 550}px;top:${RING.cy - 550}px;width:1100px;height:1100px;border-radius:50%;border:3px solid ${C.lime}44"></div>
    <div style="position:absolute;left:${RING.cx - 410}px;top:${RING.cy - 410}px;width:820px;height:820px;border-radius:50%;border:3px solid ${C.cyan}33"></div>`,
  lime: `<div style="position:absolute;inset:0;background:${C.lime}"></div>
    <div style="position:absolute;left:-300px;bottom:-500px;width:1400px;height:1400px;border-radius:50%;background:#D6FF6B"></div>
    <div style="position:absolute;right:-250px;top:-450px;width:1100px;height:1100px;border-radius:50%;background:#B5EE2C"></div>
    <div style="position:absolute;right:300px;bottom:-200px;width:520px;height:520px;border-radius:50%;border:6px solid #0B102022"></div>`,
  closing: `<div style="position:absolute;inset:0;background:${glow(50, 0, C.lime, 55, "38")},${glow(0, 100, C.violet, 45, "55")},${glow(100, 100, C.cyan, 40, "26")},${C.ink};"></div><div style="position:absolute;inset:0;${grid}"></div>`,
  split: `<div style="position:absolute;inset:0;background:${C.ink}"></div><div style="position:absolute;left:0;top:0;bottom:0;width:46%;background:${C.panel}"></div><div style="position:absolute;left:46%;top:0;bottom:0;width:6px;background:${C.lime}"></div><div style="position:absolute;inset:0;${grid}"></div>`,
};
for (const [name, html] of Object.entries(bgs)) {
  await render(`<div style="position:relative;width:2560px;height:1440px">${html}</div>`, `${out}/bg/${name}.png`, { w: 2560, h: 1440 });
}

// ---------- icon tiles (512 x 512, transparent corners) ----------
async function tile(name, { bg, fg, shape = "round", file }) {
  const radius = shape === "circle" ? "50%" : "26%";
  const svg = lucide(name).replace("<svg", `<svg style="width:56%;height:56%;color:${fg}" stroke-width="2"`);
  await render(`<div style="width:512px;height:512px;border-radius:${radius};background:${bg};display:flex;align-items:center;justify-content:center">${svg}</div>`, `${out}/icons/${file || name + "-" + bg.slice(1)}.png`, { w: 512, h: 512, transparent: true });
}
const stageIcons = {
  code: ["laptop", STAGE.code], test: ["flask-conical", STAGE.test], build: ["hammer", STAGE.build], scan: ["shield-check", STAGE.scan],
  provision: ["cloud", STAGE.provision], deploy: ["rocket", STAGE.deploy], monitor: ["activity", STAGE.monitor],
};
for (const [stage, [icon, color]] of Object.entries(stageIcons)) await tile(icon, { bg: color, fg: onColor(color), file: `stage-${stage}` });
// extra icons used on slides: [file, lucide name, tile colour]
const extra = [
  ["users", "users", C.lime], ["user-check", "user-check", C.cyan], ["ban", "ban", C.coral], ["git-branch", "git-branch", C.lime], ["git-commit", "git-commit", C.cyan],
  ["package", "package", C.amber], ["server", "server", C.violet], ["boxes", "boxes", C.pink], ["route", "route", C.pink], ["trending-up", "trending-up", C.pink],
  ["gauge", "gauge", C.mint], ["chart-line", "chart-line", C.mint], ["bug", "bug", C.coral], ["unlink", "unlink", C.amber], ["repeat", "repeat", C.cyan],
  ["scale", "scale", C.violet], ["lightbulb", "lightbulb", C.lime], ["graduation-cap", "graduation-cap", C.cyan], ["heart", "heart", C.coral], ["target", "target", C.amber],
  ["container", "container", C.amber], ["lock", "lock", C.coral], ["circle-check", "circle-check", C.lime], ["database", "database", C.cyan], ["globe", "globe", C.mint],
  ["wrench", "wrench", C.amber], ["terminal", "terminal", C.lime], ["siren", "siren", C.coral], ["search", "search", C.cyan], ["shield", "shield", C.coral], ["clock", "clock", C.cyan], ["rotate-ccw", "rotate-ccw", C.amber],
  ["dumbbell", "dumbbell", C.lime], ["rocket", "rocket", C.pink], ["cloud", "cloud", C.violet], ["x", "x", C.coral], ["check", "check", C.lime], ["network", "network", C.violet], ["cpu", "cpu", C.violet], ["layers", "layers", C.pink],
];
for (const [file, name, color] of extra) await tile(name, { bg: color, fg: onColor(color), file });

// brand logos from Simple Icons on a light tile
const brands = {
  python: si.siPython, fastapi: si.siFastapi, react: si.siReact, postgresql: si.siPostgresql, docker: si.siDocker, kubernetes: si.siKubernetes,
  helm: si.siHelm, terraform: si.siTerraform, githubactions: si.siGithubactions, prometheus: si.siPrometheus, grafana: si.siGrafana, traefik: si.siTraefikproxy,
  github: si.siGithub, nginx: si.siNginx, trivy: si.siTrivy, vite: si.siVite,
};
const brandColor = { react: "#0A7EA4", github: "#181717" };
for (const [name, icon] of Object.entries(brands)) {
  const color = brandColor[name] || `#${icon.hex}`;
  await render(`<div style="width:512px;height:512px;border-radius:26%;background:${C.white};display:flex;align-items:center;justify-content:center"><svg viewBox="0 0 24 24" style="width:58%;height:58%"><path fill="${color}" d="${icon.path}"/></svg></div>`, `${out}/icons/brand-${name}.png`, { w: 512, h: 512, transparent: true });
}
// AWS has no logo in Simple Icons, so it gets an orange cloud tile
await tile("cloud", { bg: "#FF9900", fg: C.ink, file: "brand-aws" });

// ---------- framed screenshots ----------
// A rounded frame with a thin border and a soft shadow, baked into the picture.
async function frame(src, file, { crop, width = 1200, border = C.line, radius = 22 }) {
  const dataUrl = "data:image/png;base64," + fs.readFileSync(src).toString("base64");
  const meta = await (async () => {
    const page = await browser.newPage();
    await page.setContent(`<img id=i src="${dataUrl}">`);
    const size = await page.evaluate(() => new Promise((r) => { const i = document.getElementById("i"); i.onload ? 0 : 0; if (i.complete) r([i.naturalWidth, i.naturalHeight]); else i.onload = () => r([i.naturalWidth, i.naturalHeight]); }));
    await page.close();
    return size;
  })();
  const [iw, ih] = meta;
  const c = crop || { x: 0, y: 0, w: iw, h: ih };
  const scale = width / c.w;
  const h = Math.round(c.h * scale);
  const pad = 46;
  await render(
    `<div style="position:absolute;left:${pad}px;top:${pad - 14}px;width:${width}px;height:${h}px;border-radius:${radius}px;overflow:hidden;border:3px solid ${border};box-shadow:0 22px 50px rgba(0,0,0,.55);background:#000">
       <img src="${dataUrl}" style="position:absolute;left:${-c.x * scale}px;top:${-c.y * scale}px;width:${iw * scale}px;height:${ih * scale}px">
     </div>`,
    file, { w: width + pad * 2, h: h + pad * 2 - 14 + 14, transparent: true });
  return { w: width + pad * 2, h: h + pad * 2, pad };
}
const shots = JSON.parse(fs.readFileSync(path.join(path.dirname(new URL(import.meta.url).pathname), "shots.json"), "utf8"));
const frameInfo = {};
for (const s of shots) {
  frameInfo[s.name] = await frame(path.isAbsolute(s.src) ? s.src : path.join(repo, s.src), `${out}/frames/${s.name}.png`, { crop: s.crop, width: s.width || 1400, border: s.border || C.line });
}
fs.writeFileSync(`${out}/frames/info.json`, JSON.stringify(frameInfo, null, 2));

// ---------- diagrams ----------
const ic = (name, color, size = 40) => lucide(name).replace("<svg", `<svg style="width:${size}px;height:${size}px;color:${color}" stroke-width="2"`);
const node = (icon, label, color, sub = "") => `
  <div style="display:flex;flex-direction:column;align-items:center;width:250px">
    <div style="width:150px;height:150px;border-radius:38px;background:${color};display:flex;align-items:center;justify-content:center;box-shadow:0 14px 30px ${color}44">${ic(icon, onColor(color), 78)}</div>
    <div class="u" style="margin-top:20px;font-size:30px;font-weight:700;color:${C.white}">${label}</div>
    <div style="margin-top:6px;font-size:26px;color:${C.dim};text-align:center;line-height:1.2">${sub}</div>
  </div>`;
const arrow = (color) => `<div style="flex:1;display:flex;align-items:center;margin-top:-90px"><div style="flex:1;height:6px;background:${color}"></div><div style="width:0;height:0;border-left:22px solid ${color};border-top:15px solid transparent;border-bottom:15px solid transparent"></div></div>`;

// pipeline: developer to monitored cluster
await render(`
  <div style="position:absolute;inset:0;padding:60px 50px 40px">
    <div style="display:flex;align-items:flex-start;justify-content:space-between">
      ${node("laptop", "Code", STAGE.code, "git push")}${arrow(C.dim)}
      ${node("flask-conical", "Test", STAGE.test, "pytest, build")}${arrow(C.dim)}
      ${node("hammer", "Build", STAGE.build, "one image each")}${arrow(C.dim)}
      ${node("shield-check", "Scan", STAGE.scan, "Trivy gate")}${arrow(C.dim)}
      ${node("package", "Push", STAGE.build, "GHCR, SHA tag")}${arrow(C.dim)}
      ${node("rocket", "Deploy", STAGE.deploy, "kind, then EKS")}${arrow(C.dim)}
      ${node("activity", "Monitor", STAGE.monitor, "Prometheus, Grafana")}
    </div>
    <div style="margin:46px 30px 0;display:flex;align-items:center;gap:26px;height:110px;border-radius:30px;background:${C.violet};padding:0 34px">
      ${ic("cloud", C.white, 56)}
      <div class="u" style="font-size:30px;font-weight:700;color:${C.white}">Provision</div>
      <div style="font-size:30px;color:${C.white};opacity:.95">Terraform builds the VPC, the EKS cluster and the GitHub sign-in before the first deploy</div>
    </div>
  </div>`, `${out}/diagrams/pipeline.png`, { w: 2400, h: 640, scale: 1.5, transparent: true });

// AWS architecture
const pod = (label, color, w = 150) => `<div style="width:${w}px;height:64px;border-radius:16px;background:${color};color:${onColor(color)};font-weight:700;font-size:26px;display:flex;align-items:center;justify-content:center">${label}</div>`;
await render(`
  <div style="position:absolute;inset:0">
    <!-- users and load balancer -->
    <div style="position:absolute;left:30px;top:300px;width:230px;display:flex;flex-direction:column;align-items:center;gap:14px">
      <div style="width:130px;height:130px;border-radius:34px;background:${C.cyan};display:flex;align-items:center;justify-content:center">${ic("globe", C.ink, 70)}</div>
      <div class="u" style="font-size:28px;font-weight:700">Browser</div>
    </div>
    <div style="position:absolute;left:250px;top:358px;width:150px;height:6px;background:${C.dim}"></div>
    <div style="position:absolute;left:392px;top:344px;border-left:22px solid ${C.dim};border-top:15px solid transparent;border-bottom:15px solid transparent"></div>

    <!-- VPC -->
    <div style="position:absolute;left:420px;top:20px;width:1960px;height:900px;border-radius:36px;border:5px dashed ${C.violet};background:${C.violet}12"></div>
    <div class="u" style="position:absolute;left:460px;top:44px;font-size:30px;font-weight:700;color:${C.violet === "" ? "" : "#B7A0FF"}">VPC 10.20.0.0/16 in ap-south-1</div>

    <!-- public subnets -->
    <div style="position:absolute;left:460px;top:110px;width:1880px;height:230px;border-radius:26px;background:${C.mint}18;border:3px solid ${C.mint}88"></div>
    <div style="position:absolute;left:490px;top:122px;font-size:26px;font-weight:700;color:${C.mint}">2 public subnets</div>
    <div style="position:absolute;left:500px;top:178px;display:flex;gap:40px;align-items:center">
      <div style="display:flex;align-items:center;gap:14px;padding:0 22px;height:100px;border-radius:24px;background:#FF9900;color:${C.ink};font-weight:700;font-size:30px">${ic("network", C.ink, 52)} Load balancer</div>
      <div style="display:flex;align-items:center;gap:14px;padding:0 22px;height:100px;border-radius:24px;background:${C.mint};color:${C.ink};font-weight:700;font-size:30px">${ic("route", C.ink, 52)} NAT gateway</div>
    </div>
    <div style="position:absolute;left:1560px;top:178px;display:flex;align-items:center;gap:14px;padding:0 22px;height:100px;border-radius:24px;background:${C.panel};border:3px solid ${C.line};font-size:28px;color:${C.white}">Internet gateway</div>

    <div style="position:absolute;left:640px;top:280px;width:6px;height:190px;background:${C.pink}"></div><div style="position:absolute;left:626px;top:452px;border-top:22px solid ${C.pink};border-left:15px solid transparent;border-right:15px solid transparent"></div>
    <!-- private subnets with EKS -->
    <div style="position:absolute;left:460px;top:380px;width:1880px;height:490px;border-radius:26px;background:${C.cyan}12;border:3px solid ${C.cyan}77"></div>
    <div style="position:absolute;left:700px;top:392px;font-size:26px;font-weight:700;color:${C.cyan}">2 private subnets, EKS cluster with 2 worker nodes</div>

    <div style="position:absolute;left:500px;top:440px;width:880px;height:410px;border-radius:26px;background:${C.ink};border:3px solid ${C.line}"></div>
    <div style="position:absolute;left:530px;top:452px;font-size:26px;font-weight:700;color:${C.white}">Node A, zone a</div>
    <div style="position:absolute;left:530px;top:500px;display:flex;flex-direction:column;gap:20px">
      <div style="display:flex;gap:18px">${pod("Traefik", C.pink)}${pod("Frontend", C.lime)}${pod("Backend", C.cyan)}</div>
      <div style="display:flex;gap:18px">${pod("Frontend", C.lime)}${pod("Backend", C.cyan)}${pod("Backend", C.cyan)}</div>
      <div style="display:flex;gap:18px">${pod("Postgres", C.amber, 250)}${pod("EBS disk", C.panel, 200)}</div>
    </div>
    <div style="position:absolute;left:1420px;top:440px;width:880px;height:410px;border-radius:26px;background:${C.ink};border:3px solid ${C.line}"></div>
    <div style="position:absolute;left:1450px;top:452px;font-size:26px;font-weight:700;color:${C.white}">Node B, zone b</div>
    <div style="position:absolute;left:1450px;top:500px;display:flex;flex-direction:column;gap:20px">
      <div style="display:flex;gap:18px">${pod("Prometheus", C.mint, 200)}${pod("Grafana", C.mint, 170)}</div>
      <div style="display:flex;gap:18px">${pod("Backend", C.cyan)}${pod("Backend", C.cyan)}${pod("Backend", C.cyan)}</div>
      <div style="display:flex;gap:18px;align-items:center"><div style="font-size:26px;color:${C.dim};width:520px">HPA adds backend pods, 2 up to 6</div></div>
    </div>
  </div>`, `${out}/diagrams/architecture.png`, { w: 2400, h: 940, scale: 1.5, transparent: true });

// ingress routing mini diagram
await render(`
  <div style="position:absolute;inset:0;display:flex;align-items:center;gap:30px;padding:0 30px">
    <div style="width:210px;text-align:center"><div style="margin:auto;width:120px;height:120px;border-radius:30px;background:${C.cyan};display:flex;align-items:center;justify-content:center">${ic("globe", C.ink, 64)}</div><div class="u" style="margin-top:14px;font-size:24px;font-weight:700">Browser</div></div>
    <div style="width:110px;height:6px;background:${C.dim}"></div>
    <div style="width:300px;text-align:center"><div style="margin:auto;width:150px;height:150px;border-radius:38px;background:${C.pink};display:flex;align-items:center;justify-content:center">${ic("route", C.ink, 80)}</div><div class="u" style="margin-top:14px;font-size:28px;font-weight:700">Traefik</div><div style="font-size:24px;color:${C.dim}">Ingress</div></div>
    <div style="display:flex;flex-direction:column;gap:60px;flex:1">
      <div style="display:flex;align-items:center;gap:18px"><div style="width:110px;height:6px;background:${C.lime}"></div><div style="font-size:30px;font-weight:700;color:${C.lime};font-family:'JetBrains Mono'">/</div><div style="flex:1;height:6px;background:${C.lime}"></div><div style="padding:18px 30px;border-radius:22px;background:${C.lime};color:${C.ink};font-size:30px;font-weight:700">Frontend</div></div>
      <div style="display:flex;align-items:center;gap:18px"><div style="width:110px;height:6px;background:${C.cyan}"></div><div style="font-size:30px;font-weight:700;color:${C.cyan};font-family:'JetBrains Mono'">/api</div><div style="flex:1;height:6px;background:${C.cyan}"></div><div style="padding:18px 30px;border-radius:22px;background:${C.cyan};color:${C.ink};font-size:30px;font-weight:700">Backend</div></div>
    </div>
  </div>`, `${out}/diagrams/ingress.png`, { w: 1700, h: 360, scale: 1.5, transparent: true });

await browser.close();
console.log("assets ready in", out);
