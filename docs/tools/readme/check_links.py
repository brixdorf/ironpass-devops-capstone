"""Checks that every relative link and image in the README and docs exists.
Usage: python3 docs/tools/readme/check_links.py   (run from the repository root)
"""
import re
import sys
from pathlib import Path

root = Path(".")
bad = 0
total = 0
for md in [Path("README.md"), *sorted(Path("docs").glob("*.md")), *sorted(Path("monitoring").glob("*.md")), Path("k8s/README.md"), Path("terraform/README.md")]:
    if not md.exists():
        continue
    text = md.read_text()
    refs = re.findall(r"\]\(([^)\s]+)\)", text) + re.findall(r'(?:src|href)="([^"]+)"', text)
    for ref in refs:
        if re.match(r"^(https?:|mailto:|#)", ref):
            continue
        target = (md.parent / ref.split("#")[0]).resolve()
        total += 1
        if not target.exists():
            print(f"BROKEN in {md}: {ref}")
            bad += 1
print(f"checked {total} relative links, {bad} broken")
sys.exit(1 if bad else 0)
