"""Builds the README icon tiles (docs/assets/icons/*.svg) from Lucide icons.

Usage: python3 build_icons.py <lucide-static icons folder> <output folder>
Each tile is a 36 px rounded square with a tint of the accent colour behind a
24 px bold glyph. The tile has its own dark base, so it looks the same on the
light and the dark GitHub theme.
"""
import re
import sys
from pathlib import Path

ACCENT = {
    "lime": "#C6FF3D",
    "coral": "#FF5D5D",
    "violet": "#A58BFF",
    "cyan": "#22D3EE",
    "amber": "#FFB547",
}

# file name, Lucide icon, accent colour, alt text
ICONS = [
    ("presentation", "presentation", "lime", "Presentation"),
    ("pdf", "file-text", "amber", "PDF"),
    ("glance-endpoints", "plug", "lime", "Endpoints"),
    ("glance-tests", "flask-conical", "coral", "Tests"),
    ("glance-pipeline", "timer", "amber", "Pipeline time"),
    ("glance-pods", "boxes", "violet", "Pods"),
    ("glance-targets", "activity", "cyan", "Prometheus targets"),
    ("quick-start", "rocket", "lime", "Quick start"),
    ("how-it-works", "workflow", "lime", "How it works"),
    ("built-with", "blocks", "lime", "Built with"),
    ("api", "plug", "lime", "API"),
    ("run-by-hand", "terminal", "lime", "Run by hand"),
    ("docker", "container", "amber", "Docker"),
    ("compose", "layers", "amber", "Docker Compose"),
    ("kubernetes", "ship-wheel", "violet", "Kubernetes"),
    ("terraform", "server-cog", "violet", "Terraform"),
    ("cicd", "git-merge", "amber", "CI/CD"),
    ("monitoring", "activity", "cyan", "Monitoring"),
    ("troubleshooting", "wrench", "coral", "Troubleshooting"),
    ("rubric", "list-checks", "amber", "Rubric"),
    ("structure", "folder-tree", "amber", "Repository structure"),
    ("teardown", "power", "coral", "Teardown"),
    ("check", "circle-check", "lime", "Done"),
]

TEMPLATE = """<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 36 36" role="img" aria-label="{alt}">
  <title>{alt}</title>
  <rect width="36" height="36" rx="10" fill="#0B1020"/>
  <rect width="36" height="36" rx="10" fill="{color}" fill-opacity="0.2"/>
  <rect x="0.5" y="0.5" width="35" height="35" rx="9.5" fill="none" stroke="{color}" stroke-opacity="0.5"/>
  <g transform="translate(6 6)" fill="none" stroke="{color}" stroke-width="2.25" stroke-linecap="round" stroke-linejoin="round">
{body}
  </g>
</svg>
"""

src = Path(sys.argv[1])
out = Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
for name, lucide, accent, alt in ICONS:
    text = (src / f"{lucide}.svg").read_text()
    inner = re.search(r"<svg[^>]*>(.*)</svg>", text, re.S).group(1).strip()
    body = "\n".join("    " + line.strip() for line in inner.splitlines() if line.strip())
    (out / f"{name}.svg").write_text(TEMPLATE.format(alt=alt, color=ACCENT[accent], body=body))
print(f"wrote {len(ICONS)} icons to {out}")
