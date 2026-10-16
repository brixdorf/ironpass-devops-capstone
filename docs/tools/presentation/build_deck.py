"""Builds IronPass-Presentation.pptx from the picture assets made by assets.mjs.

Only text boxes, plain shapes, pictures and one table are used, so the file imports
cleanly into Google Slides. The font name is set on every run.

Usage: python build_deck.py <assets-dir> <output.pptx> <commit-count> <pipeline-time>
"""
import json
import sys
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

ASSETS = Path(sys.argv[1])
OUT = sys.argv[2]
COMMITS = sys.argv[3]
PIPELINE_TIME = sys.argv[4]

TITLE_FONT, BODY_FONT, MONO_FONT = "Unbounded", "DM Sans", "JetBrains Mono"

INK, PANEL, LINE, WHITE, DIM = "0B1020", "141B34", "2A3355", "F5F7FA", "9AA4C4"
LIME, CORAL, VIOLET, CYAN, AMBER, PINK, MINT = "C6FF3D", "FF5D5D", "7C4DFF", "22D3EE", "FFB547", "FF6BD6", "2EE6A6"
VIOLET_LIGHT = "B7A0FF"
STAGE = {"code": LIME, "test": CYAN, "build": AMBER, "scan": CORAL, "provision": VIOLET, "deploy": PINK, "monitor": MINT}

FRAMES = json.loads((ASSETS / "frames" / "info.json").read_text())

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]


def rgb(hex_):
    return RGBColor.from_string(hex_)


def on_color(hex_):
    return WHITE if hex_ == VIOLET else INK


def add_text(slide, x, y, w, h, paras, font=BODY_FONT, size=20, color=WHITE, bold=False,
             align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, line_spacing=1.1):
    """paras: a string, or a list of strings / lists of (text, overrides) runs."""
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    if isinstance(paras, str):
        paras = [paras]
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = line_spacing
        runs = [(para, {})] if isinstance(para, str) else para
        for text, o in runs:
            r = p.add_run()
            r.text = text
            r.font.name = o.get("font", font)
            r.font.size = Pt(o.get("size", size))
            r.font.bold = o.get("bold", bold)
            r.font.color.rgb = rgb(o.get("color", color))
    return box


def add_rect(slide, x, y, w, h, fill, line=None, radius=0.12, shape=MSO_SHAPE.ROUNDED_RECTANGLE):
    s = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        s.adjustments[0] = radius
    s.fill.solid()
    s.fill.fore_color.rgb = rgb(fill)
    if line:
        s.line.color.rgb = rgb(line)
        s.line.width = Pt(1.5)
    else:
        s.line.fill.background()
    s.shadow.inherit = False
    return s


def add_pic(slide, path, x, y, w=None, h=None):
    return slide.shapes.add_picture(str(path), Inches(x), Inches(y), Inches(w) if w else None, Inches(h) if h else None)


def background(slide, name):
    pic = slide.shapes.add_picture(str(ASSETS / "bg" / f"{name}.png"), 0, 0, prs.slide_width, prs.slide_height)
    slide.shapes._spTree.remove(pic._element)
    slide.shapes._spTree.insert(2, pic._element)  # send to the back


def icon(slide, name, x, y, size):
    return add_pic(slide, ASSETS / "icons" / f"{name}.png", x, y, size, size)


def header(slide, stage_color, label, title, dark=False):
    """Stage chip and big title. dark=True is used on the lime slide."""
    chip_w = 0.5 + 0.155 * len(label)
    add_rect(slide, 0.65, 0.5, chip_w, 0.44, INK if dark else stage_color, radius=0.5)
    add_text(slide, 0.65, 0.5, chip_w, 0.44, label.upper(), size=18, bold=True,
             color=stage_color if dark else on_color(stage_color), align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    add_text(slide, 0.65, 1.05, 12.0, 0.8, title, font=TITLE_FONT, size=38, bold=True, color=INK if dark else WHITE)


def frame(slide, name, x, y, max_w, max_h, caption=None, caption_color=DIM):
    """Places a framed screenshot so it fits in the box. Returns (x, y, w, h) of the picture."""
    info = FRAMES[name]
    aspect = info["w"] / info["h"]
    w, h = max_w, max_w / aspect
    if h > max_h:
        h, w = max_h, max_h * aspect
    pic = add_pic(slide, ASSETS / "frames" / f"{name}.png", x, y, w, h)
    if caption:
        pad = info["pad"] / info["w"] * w
        add_text(slide, x + pad, y + h - pad * 0.55, w - 2 * pad, 0.4, caption, size=18, color=caption_color)
    return x, y, w, h


def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


def icon_row(slide, name, x, y, text, size=0.7, text_size=24, w=5.2):
    icon(slide, name, x, y, size)
    add_text(slide, x + size + 0.25, y, w, size, text, size=text_size, anchor=MSO_ANCHOR.MIDDLE)


# 1 ------------------------------------------------------------------ title
s = prs.slides.add_slide(BLANK)
background(s, "title")
add_text(s, 0.8, 1.55, 9.5, 0.4, "DEVOPS FINAL CAPSTONE", font=BODY_FONT, size=20, bold=True, color=CYAN)
add_text(s, 0.8, 2.05, 11, 1.6, "IronPass", font=TITLE_FONT, size=96, bold=True, color=LIME)
add_text(s, 0.8, 3.85, 10.0, 0.8, "From code to a monitored Kubernetes cluster", size=30, color=WHITE)
add_text(s, 0.8, 4.7, 8, 0.4, "A gym membership app by Romit", size=22, color=DIM)
legend = [("code", "Code"), ("test", "Test"), ("build", "Build"), ("scan", "Scan"), ("provision", "Provision"), ("deploy", "Deploy"), ("monitor", "Monitor")]
for i, (key, label) in enumerate(legend):
    x = 0.8 + i * 1.62
    icon(s, f"stage-{key}", x, 5.75, 0.8)
    add_text(s, x - 0.1, 6.65, 1.2, 0.35, label, size=18, color=STAGE[key], bold=True)
# the tile sits exactly on the centre of the two rings drawn in the title background
ring = json.loads((ASSETS / "bg" / "title-rings.json").read_text())
tile = 1.9
icon(s, "dumbbell", ring["cx"] / ring["width"] * 13.333 - tile / 2, ring["cy"] / ring["height"] * 7.5 - tile / 2, tile)
notes(s, "Hi, I am Romit and this is IronPass, a gym membership app. I used it to learn how one app travels from my laptop to a monitored Kubernetes cluster on AWS. The seven colours at the bottom are the stages you will see on every slide.")

# 2 ------------------------------------------------------------------ problem and product
s = prs.slides.add_slide(BLANK)
background(s, "grid-lime")
header(s, STAGE["code"], "01  The product", "The problem")
add_text(s, 0.65, 2.1, 5.6, 1.2, "Paper lists let expired members in.", size=28, bold=True)
icon_row(s, "users", 0.65, 3.55, "Sign members up", w=4.6)
icon_row(s, "user-check", 0.65, 4.55, "Check them in", w=4.6)
icon_row(s, "ban", 0.65, 5.55, "Refuse expired plans", w=4.6)
frame(s, "rejected", 5.35, 1.97, 5.6, 4.0, caption="Expired plan, check-in refused")
frame(s, "mobile", 11.05, 1.95, 2.2, 4.8)
notes(s, "A gym front desk needs to know quickly who may come in. IronPass lets staff sign members up and check them in. If a member's plan has expired, the API refuses the check-in, and you can see that message on the screen. The page also works on a phone.")

# 3 ------------------------------------------------------------------ tech stack
s = prs.slides.add_slide(BLANK)
background(s, "grid-cyan")
header(s, STAGE["code"], "02  Tech stack", "Tech stack")
brands = [("python", "Python"), ("fastapi", "FastAPI"), ("react", "React"), ("postgresql", "PostgreSQL"),
          ("docker", "Docker"), ("kubernetes", "Kubernetes"), ("helm", "Helm"), ("terraform", "Terraform"),
          ("aws", "AWS"), ("githubactions", "GitHub Actions"), ("prometheus", "Prometheus"), ("grafana", "Grafana")]
for i, (key, label) in enumerate(brands):
    col, row = i % 4, i // 4
    x, y = 0.75 + col * 3.1, 2.2 + row * 1.75
    icon(s, f"brand-{key}", x, y, 1.0)
    add_text(s, x + 1.15, y, 1.8, 1.0, label, size=20, anchor=MSO_ANCHOR.MIDDLE, bold=True)
add_text(s, 6.6, 1.15, 6.1, 0.8, "Python backend, React frontend, PostgreSQL database, all in containers.", size=20, color=DIM)
notes(s, "The backend is Python with FastAPI, the frontend is React, and the data lives in PostgreSQL. Docker packs them into containers. Terraform builds the cloud, GitHub Actions is the pipeline, and Prometheus with Grafana watch the result.")

# 4 ------------------------------------------------------------------ architecture
s = prs.slides.add_slide(BLANK)
background(s, "grid-violet")
header(s, STAGE["provision"], "03  Architecture", "Architecture")
info = FRAMES  # (diagram has no frame, read its size from the file)
dpic = add_pic(s, ASSETS / "diagrams" / "architecture.png", 0.85, 1.95, 11.6)
add_text(s, 0.65, 6.75, 12, 0.45, "Traefik routes web and API traffic into the cluster.", size=20, color=DIM)
notes(s, "This is the AWS picture. One network with two public and two private subnets, and an EKS cluster with two worker nodes in the private ones. Traffic comes in through a load balancer to Traefik, which sends it to the frontend and backend pods.")

# 5 ------------------------------------------------------------------ docker
s = prs.slides.add_slide(BLANK)
background(s, "grid-lime")
header(s, STAGE["code"], "04  Run locally", "Run it with Docker")
add_text(s, 0.65, 1.9, 12, 0.45, "One command starts the database, the API and the website.", size=20, color=DIM)
frame(s, "compose", 0.4, 2.7, 8.0, 4.4)
cards = [("3", "services, in order", LIME), ("3 of 3", "clean starts healthy", CYAN), ("0", "records lost on restart", MINT)]
for i, (big, small, col) in enumerate(cards):
    y = 2.5 + i * 1.5
    add_rect(s, 8.7, y, 4.0, 1.3, PANEL, line=LINE)
    add_text(s, 8.95, y + 0.1, 3.6, 0.7, big, font=TITLE_FONT, size=32, bold=True, color=col)
    add_text(s, 8.95, y + 0.78, 3.6, 0.4, small, size=18)
notes(s, "docker compose up starts three containers. The database has a health check, and the backend and frontend wait until the one before them is healthy. I started it three times from clean and each time everything came up healthy, and a record I created was still there after a restart.")

# 6 ------------------------------------------------------------------ tests
s = prs.slides.add_slide(BLANK)
background(s, "grid-cyan")
header(s, STAGE["test"], "05  Test", "Tests")
add_text(s, 0.65, 2.2, 4.8, 1.9, "32", font=TITLE_FONT, size=110, bold=True, color=CYAN)
add_text(s, 0.65, 4.0, 4.8, 0.5, "tests pass", size=28, bold=True)
add_text(s, 0.65, 4.8, 4.6, 1.6, "Checks wrong input, missing members and the expired plan rule.", size=22, color=DIM)
frame(s, "pytest", 5.5, 2.1, 7.3, 4.8)
notes(s, "There are thirty two tests and they all pass. They check real things like a wrong plan type returning an error, a missing member returning not found, and the rule that an expired plan cannot check in. The tests use a throwaway SQLite database, so real data is never touched.")

# 7 ------------------------------------------------------------------ git
s = prs.slides.add_slide(BLANK)
background(s, "grid-lime")
header(s, STAGE["code"], "06  Code", "Git and GitHub")
frame(s, "repo", 0.3, 1.85, 6.5, 4.0, caption=None)
frame(s, "commits", 6.55, 1.85, 6.5, 4.0, caption=None)
add_rect(s, 0.65, 6.05, 3.0, 0.85, LIME, radius=0.3)
add_text(s, 0.65, 6.05, 3.0, 0.85, f"{COMMITS} commits", font=TITLE_FONT, size=24, bold=True, color=INK, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
add_text(s, 3.95, 6.05, 8.8, 0.85, "Small commits, clear messages, no secrets in git.", size=22, anchor=MSO_ANCHOR.MIDDLE)
notes(s, "The code lives in a public GitHub repository. I made many small commits, each with a plain message, so every change is easy to find. Passwords and keys are never stored in git.")

# 8 ------------------------------------------------------------------ ci/cd
s = prs.slides.add_slide(BLANK)
background(s, "grid-pink")
header(s, STAGE["build"], "07  CI/CD", "The pipeline")
add_pic(s, ASSETS / "diagrams" / "pipeline.png", 0.85, 1.75, 11.6)
frame(s, "run", 0.35, 4.85, 6.8, 2.5)
icon_row(s, "circle-check", 7.5, 5.0, "Tests gate everything", size=0.55, text_size=22, w=4.6)
icon_row(s, "shield", 7.5, 5.8, "Scanned image is pushed", size=0.55, text_size=22, w=4.6)
icon_row(s, "rocket", 7.5, 6.6, "Smoke test, then EKS", size=0.55, text_size=22, w=4.6)
notes(s, "Every push to main starts this pipeline. It runs the tests, builds each image once, scans that same image with Trivy, pushes it and tries it on a temporary cluster before deploying to EKS. Terraform, the purple bar, builds the cloud before the first deploy.")

# 9 ------------------------------------------------------------------ security
s = prs.slides.add_slide(BLANK)
background(s, "grid-coral")
header(s, STAGE["scan"], "08  Scan", "Security scan")
add_text(s, 0.65, 1.9, 12, 0.45, "Trivy fails the build on fixable HIGH or CRITICAL issues.", size=20, color=DIM)
frame(s, "red", 2.0, 2.5, 4.6, 3.9, caption=None)
add_text(s, 0.75, 6.4, 5.8, 0.5, "A bad image stops the pipeline", size=20, bold=True, color=CORAL)
frame(s, "trivy", 6.7, 2.5, 6.4, 3.9, caption=None)
add_text(s, 7.2, 6.4, 5.8, 0.5, "My real images: 0 findings", size=20, bold=True, color=MINT)
notes(s, "Trivy scans both images for known security problems. On the left I added an old library on purpose in a throwaway branch, and the pipeline stopped. On the right is the real result, where both images are clean.")

# 10 ----------------------------------------------------------------- registry
s = prs.slides.add_slide(BLANK)
background(s, "grid-lime")
header(s, STAGE["build"], "09  Registry", "Container registry")
frame(s, "ghcr", 0.35, 2.0, 7.6, 4.6)
icon_row(s, "package", 8.5, 2.5, "Tagged by commit", w=3.8)
icon_row(s, "lock", 8.5, 3.6, "Built-in GITHUB_TOKEN", w=3.8, text_size=20)
icon_row(s, "globe", 8.5, 4.7, "Public packages", w=3.8)
notes(s, "The images go to the GitHub Container Registry. Each one is tagged with the commit hash, so I can trace any running pod back to the exact code. The pipeline uses the built in token, so there are no stored passwords.")

# 11 ----------------------------------------------------------------- terraform
s = prs.slides.add_slide(BLANK)
background(s, "grid-violet")
header(s, STAGE["provision"], "10  Provision", "Terraform on AWS")
add_text(s, 0.65, 2.1, 5.0, 1.6, "62", font=TITLE_FONT, size=110, bold=True, color=VIOLET_LIGHT)
add_text(s, 0.65, 4.0, 5.0, 0.5, "resources from one plan", size=26, bold=True)
add_text(s, 0.65, 4.8, 4.6, 1.6, "Code builds the network, the cluster and the GitHub sign-in.", size=22, color=DIM)
frame(s, "terraform", 5.6, 2.1, 7.3, 4.6)
notes(s, "Terraform builds everything on AWS from code, so nobody clicks in the console. The plan shows sixty two resources, including the network, the EKS cluster and the sign in for GitHub. The nodes are c7i flex large because this free plan account refuses t3 medium.")

# 12 ----------------------------------------------------------------- kubernetes and helm
s = prs.slides.add_slide(BLANK)
background(s, "grid-pink")
header(s, STAGE["deploy"], "11  Deploy", "Kubernetes and Helm")
frame(s, "k8s", 0.35, 2.0, 7.8, 4.6)
icon_row(s, "boxes", 8.6, 2.3, "5 pods, 3 services", w=3.9)
icon_row(s, "layers", 8.6, 3.6, "One Helm chart", w=3.9)
icon_row(s, "rotate-ccw", 8.6, 4.9, "Rollback in one command", w=3.9, text_size=20)
notes(s, "Helm installs the app on Kubernetes. There are two copies of the backend, two of the frontend and one database pod, each behind its own service. If a release goes wrong, helm rollback puts the old version back.")

# 13 ----------------------------------------------------------------- ingress
s = prs.slides.add_slide(BLANK)
background(s, "grid-pink")
header(s, STAGE["deploy"], "12  Deploy", "Ingress")
add_pic(s, ASSETS / "diagrams" / "ingress.png", 0.45, 2.0, 6.3)
add_text(s, 0.65, 4.0, 5.9, 1.8, "One address for the whole app.", size=28, bold=True)
add_text(s, 0.65, 5.2, 5.9, 1.6, "Traefik replaced ingress-nginx, which is retired.", size=22, color=DIM)
frame(s, "ingress", 6.9, 1.95, 6.2, 4.9)
notes(s, "The Ingress is the front door. Slash goes to the frontend and slash api goes to the backend, all on one load balancer address. I use Traefik because the Kubernetes project retired ingress-nginx, and I moved the live cluster over without a break.")

# 14 ----------------------------------------------------------------- autoscaling
s = prs.slides.add_slide(BLANK)
background(s, "grid-pink")
header(s, STAGE["deploy"], "13  Deploy", "Autoscaling")
add_text(s, 0.65, 2.1, 5.2, 1.4, "2 to 6", font=TITLE_FONT, size=72, bold=True, color=PINK)
add_text(s, 0.65, 3.55, 5.0, 0.5, "backend pods under load", size=26, bold=True)
add_text(s, 0.65, 4.4, 4.6, 1.6, "The load script raises CPU. The autoscaler adds pods.", size=22, color=DIM)
add_text(s, 6.3, 1.9, 3, 0.4, "Before the load", size=18, bold=True, color=DIM)
frame(s, "hpa-before", 5.9, 2.2, 6.9, 1.5, caption=None)
add_text(s, 6.3, 3.95, 3.5, 0.4, "During the load", size=18, bold=True, color=PINK)
frame(s, "hpa-during", 5.9, 4.25, 6.9, 3.1, caption=None)
notes(s, "The backend has a horizontal pod autoscaler. When my load script pushed the CPU over fifty percent, it grew the backend from two pods to six, and it shrinks again when the load stops. It needs resource requests and metrics server to do this.")

# 15 ----------------------------------------------------------------- monitoring
s = prs.slides.add_slide(BLANK)
background(s, "grid-mint")
header(s, STAGE["monitor"], "14  Monitor", "Monitoring")
frame(s, "grafana", 0.3, 1.95, 7.5, 5.2)
frame(s, "prom", 7.85, 1.95, 5.2, 2.7)
add_text(s, 8.2, 4.95, 4.6, 1.8, "Prometheus scrapes the backend. Grafana shows rate, latency and errors.", size=22)
notes(s, "The backend exposes a metrics page. Prometheus collects it, and Grafana draws the request rate, the latency, the errors and the number of pods. The dashboard is stored as code in the Helm chart, so it appears by itself when the app is deployed.")

# 16 ----------------------------------------------------------------- troubleshooting
s = prs.slides.add_slide(BLANK)
background(s, "grid-coral")
header(s, STAGE["build"], "15  Practice", "Troubleshooting")
cards = [("bug", "ImagePullBackOff", "Wrong image tag."), ("unlink", "No endpoints", "Label typo."), ("repeat", "CrashLoopBackOff", "Missing setting.")]
for i, (ic, head, line) in enumerate(cards):
    x = 0.65 + i * 4.1
    add_rect(s, x, 2.2, 3.85, 3.7, PANEL, line=LINE)
    icon(s, ic, x + 0.3, 2.5, 1.0)
    add_text(s, x + 0.3, 3.7, 3.4, 0.6, head, font=TITLE_FONT, size=18, bold=True, color=AMBER)
    add_text(s, x + 0.3, 4.5, 3.3, 0.9, line, size=24)
add_text(s, 0.65, 6.3, 12, 0.5, "Found with kubectl, fixed with apply -f.", size=22, color=DIM)
notes(s, "I broke three deployments on purpose and fixed them. One had an image tag that does not exist, one had a label typo so the service found no pods, and one crashed because a setting was missing. For each I used kubectl get, describe, events and logs, then fixed the file and applied it again.")

# 17 ----------------------------------------------------------------- alternatives
s = prs.slides.add_slide(BLANK)
background(s, "grid-mint")
header(s, STAGE["provision"], "16  Why Kubernetes", "Why Kubernetes?")
rows = [
    ("", "Self-heals", "Auto scales", "Rolling updates", "Any cloud"),
    ("Docker Compose only", "Partly", "No", "No", "Yes"),
    ("A single VM", "No", "No", "No", "Yes"),
    ("Managed container service", "Yes", "Yes", "Yes", "No"),
    ("Kubernetes", "Yes", "Yes", "Yes", "Yes"),
]
tbl_shape = s.shapes.add_table(len(rows), 5, Inches(0.65), Inches(2.1), Inches(12.0), Inches(4.0))
tbl = tbl_shape.table
tbl.columns[0].width = Inches(3.9)
for c in range(1, 5):
    tbl.columns[c].width = Inches(2.025)
for r, row in enumerate(rows):
    tbl.rows[r].height = Inches(0.8)
    for c, text in enumerate(row):
        cell = tbl.cell(r, c)
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        cell.fill.solid()
        last = r == len(rows) - 1
        cell.fill.fore_color.rgb = rgb(VIOLET if r == 0 else (LIME if last else PANEL))
        tf = cell.text_frame
        tf.paragraphs[0].alignment = PP_ALIGN.LEFT if c == 0 else PP_ALIGN.CENTER
        run = tf.paragraphs[0].add_run()
        run.text = text
        run.font.name = BODY_FONT
        run.font.size = Pt(20)
        run.font.bold = r == 0 or last or c == 0
        if r == 0:
            col = WHITE
        elif last:
            col = INK
        elif c == 0:
            col = WHITE
        else:
            col = {"Yes": MINT, "No": CORAL, "Partly": AMBER}[text]
        run.font.color.rgb = rgb(col)
add_text(s, 0.65, 6.4, 12, 0.5, "Kubernetes does it all, on any cloud. The price is more to learn.", size=22, color=WHITE)
notes(s, "I looked at four ways to run the app. Compose alone and a single server are simple but cannot scale or heal themselves. A managed container service does, but only on one cloud. Kubernetes does all of it on any cloud, and the price is that it is harder to learn.")

# 18 ----------------------------------------------------------------- results
s = prs.slides.add_slide(BLANK)
background(s, "lime")
header(s, LIME, "17  Results", "Results in numbers", dark=True)
stats = [("32", "tests pass"), ("15", "API endpoints"), (PIPELINE_TIME, "full pipeline"), ("0", "HIGH or CRITICAL"),
         ("5", "pods running"), ("2 to 6", "backend pods (HPA)"), ("309 MB", "backend image"), ("90.5 MB", "frontend image")]
colors = [LIME, CYAN, AMBER, MINT, PINK, CORAL, AMBER, CYAN]
for i, ((big, small), col) in enumerate(zip(stats, colors)):
    cx, cy = i % 4, i // 4
    x, y = 0.65 + cx * 3.05, 2.2 + cy * 2.35
    add_rect(s, x, y, 2.85, 2.15, INK, radius=0.1)
    add_text(s, x + 0.2, y + 0.25, 2.5, 0.9, big, font=TITLE_FONT, size=32 if len(big) < 7 else 26, bold=True, color=col, anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, x + 0.2, y + 1.3, 2.5, 0.6, small, size=18, color=WHITE)
notes(s, "These are the real numbers from the project. Thirty two tests pass, the API has fifteen endpoints, and the whole pipeline takes about four minutes. Both images are clean in Trivy, the backend scales from two to six pods, and the images are small.")

# 19 ----------------------------------------------------------------- learned
s = prs.slides.add_slide(BLANK)
background(s, "grid-violet")
header(s, VIOLET, "18  Learned", "What I learned")
items = [("lightbulb", "One job per tool"), ("lock", "Pin versions, scan images"), ("git-commit", "Small commits, easy fixes"), ("wrench", "Break it, then fix it")]
for i, (ic, text) in enumerate(items):
    y = 2.2 + i * 1.2
    icon(s, ic, 0.9, y, 0.95)
    add_text(s, 2.2, y, 10, 0.95, text, size=32, bold=True, anchor=MSO_ANCHOR.MIDDLE)
for i, (key, _label) in enumerate(legend):
    x = 8.2 + (i % 4) * 1.2
    y = 2.4 + (i // 4) * 1.3
    icon(s, f"stage-{key}", x, y, 1.05)
add_text(s, 8.2, 5.0, 4.6, 0.5, "Seven stages, one pipeline.", size=20, color=DIM)
notes(s, "My biggest lesson is that every tool has one job, and the pipeline joins them together. Pinning versions and scanning images catches problems early. Small commits make problems easy to find, and breaking things on purpose is the fastest way to learn how to fix them.")

# 20 ----------------------------------------------------------------- thank you
s = prs.slides.add_slide(BLANK)
background(s, "closing")
add_text(s, 0.8, 2.0, 8, 1.4, "Thank you", font=TITLE_FONT, size=72, bold=True, color=LIME)
add_text(s, 0.8, 3.6, 7.5, 0.9, "From code to a monitored cluster.", size=28)
add_text(s, 0.8, 5.2, 8, 0.5, "github.com/brixdorf/ironpass-devops-capstone", font=MONO_FONT, size=20, color=CYAN)
add_rect(s, 9.2, 1.9, 3.5, 3.5, WHITE, radius=0.08)
add_pic(s, ASSETS / "qr.png", 9.4, 2.1, 3.1, 3.1)
add_text(s, 9.2, 5.6, 3.5, 0.4, "Scan to open the repo", size=18, color=DIM, align=PP_ALIGN.CENTER)
notes(s, "Thank you for watching. The code, the screenshots and the documentation are all in the GitHub repository, and you can reach it with the QR code.")

prs.save(OUT)
print("saved", OUT, len(prs.slides._sldIdLst), "slides")
