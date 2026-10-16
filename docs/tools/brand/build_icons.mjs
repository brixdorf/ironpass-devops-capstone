// Builds the website icon set and the logo for GitHub from one barbell mark.
//   node build_icons.mjs <repo-root> <work-dir>
// Run it from a folder where playwright is installed. Then run make_ico.py for favicon.ico.
import { chromium } from "playwright";
import fs from "node:fs";
import path from "node:path";

const repo = path.resolve(process.argv[2] || ".");
const work = path.resolve(process.argv[3] || "./brand-work");
fs.mkdirSync(work, { recursive: true });
const pub = path.join(repo, "frontend/public");
const INK = "#0B1020";
const LIME = "#C6FF3D";

// The barbell on a 64 x 64 grid: two big plates and one bar, so it still reads at 16 px. The edges sit on a 4 unit grid, which is one pixel at 16 px.
const barbell = (fill) => `
  <rect x="8" y="16" width="12" height="32" rx="3" fill="${fill}"/>
  <rect x="44" y="16" width="12" height="32" rx="3" fill="${fill}"/>
  <rect x="20" y="28" width="24" height="8" fill="${fill}"/>`;

// the favicon: a full lime tile with rounded corners
const favicon = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="14" fill="${LIME}"/>${barbell(INK)}
</svg>
`;

// the logo for the README: the same mark with a thin ink rim so it also shows on a white page
const logo = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="IronPass logo">
  <title>IronPass logo</title>
  <rect width="64" height="64" rx="16" fill="${INK}"/>
  <rect x="3" y="3" width="58" height="58" rx="13" fill="${LIME}"/>
  <g transform="translate(32 32) scale(0.86) translate(-32 -32)">${barbell(INK)}</g>
</svg>
`;

// a square icon: the tile fills the canvas (full) or sits on an ink background (card)
const square = (size, { mode }) => {
  if (mode === "full") {
    // solid lime square, mark kept inside the safe zone (a circle of 80 percent of the width)
    return `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 64 64">
  <rect width="64" height="64" fill="${LIME}"/>
  <g transform="translate(32 32) scale(0.7) translate(-32 -32)">${barbell(INK)}</g>
</svg>`;
  }
  // card: ink square with a lime tile inset
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 64 64">
  <rect width="64" height="64" fill="${INK}"/>
  <rect x="8" y="8" width="48" height="48" rx="12" fill="${LIME}"/>
  <g transform="translate(32 32) scale(0.75) translate(-32 -32)">${barbell(INK)}</g>
</svg>`;
};

fs.writeFileSync(path.join(pub, "favicon.svg"), favicon);
fs.mkdirSync(path.join(repo, "docs/assets"), { recursive: true });
fs.writeFileSync(path.join(repo, "docs/assets/logo.svg"), logo);

const browser = await chromium.launch();
async function png(svg, size, file, transparent = false) {
  const page = await browser.newPage({ viewport: { width: size, height: size } });
  await page.setContent(`<html><body style="margin:0;background:${transparent ? "transparent" : INK}">${svg.replace("<svg ", `<svg width="${size}" height="${size}" `)}</body></html>`);
  await page.screenshot({ path: file, omitBackground: transparent });
  await page.close();
}
// favicon sizes come straight from favicon.svg with transparent corners
for (const [size, name] of [[16, "_f16.png"], [32, "favicon-32.png"], [48, "_f48.png"]]) {
  await png(favicon, size, path.join(name.startsWith("_") ? work : pub, name), true);
}
await png(square(180, { mode: "full" }), 180, path.join(pub, "apple-touch-icon.png"));
await png(square(192, { mode: "card" }), 192, path.join(pub, "icon-192.png"));
await png(square(512, { mode: "card" }), 512, path.join(pub, "icon-512.png"));
await png(square(512, { mode: "full" }), 512, path.join(pub, "icon-maskable-512.png"));
await browser.close();
console.log("done");
