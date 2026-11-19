#!/usr/bin/env python3
"""Slide decks as one file per slide.

A deck directory holds:
  frame/head.html   everything before the first slide (styles, <body>, chrome)
  frame/tail.html   everything after the last slide (nav, script)
  slides/<id>.html  one <section class="slide"> per file, named by its id
  order.txt         slide ids in presentation order; '#' starts a comment
  deck.conf         optional: s3=s3://bucket/path/index.html

Commands:
  deck.py new <deck-dir> "<title>"       start a deck in the house style (frame from kit/template.html)
  deck.py split <deck.html> <deck-dir>   turn an existing single-file deck into a deck dir
  deck.py build <deck-dir>               write index.html and deck.md (the text version)
  deck.py shot <deck-dir> <id> [phase]   render one slide to shots/<id>.png at 1920x1080
  deck.py publish <deck-dir>             build, then upload index.html to the deck.conf s3 path
"""
import html
import os
import re
import subprocess
import sys
from html.parser import HTMLParser

SECTION = re.compile(r'^<section\b[^>]*class="[^"]*\bslide\b[^"]*"[^>]*>.*?^</section>', re.M | re.S)
SLIDE_ID = re.compile(r'<section\b[^>]*\bid="([^"]+)"')
SLIDE_NUM = re.compile(r'<span class="slide-num">[^<]*</span>')


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def write(path, text):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def split(src, deck, quiet=False):
    text = read(src)
    sections = list(SECTION.finditer(text))
    if not sections:
        sys.exit(f"no <section class=\"slide\"> found in {src}")
    head = text[:sections[0].start()]
    tail = text[sections[-1].end():]
    # Drop the banner comment that precedes each slide in hand-written decks; build writes its own.
    head = re.sub(r'(\s*<!--[^>]*-->\s*)+$', "\n", head)
    write(f"{deck}/frame/head.html", head)
    write(f"{deck}/frame/tail.html", tail)
    ids = []
    for n, m in enumerate(sections, 1):
        body = m.group(0)
        found = SLIDE_ID.search(body)
        sid = found.group(1) if found else f"slide{n}"
        if sid in ids:
            sid = f"{sid}-{n}"
        ids.append(sid)
        write(f"{deck}/slides/{sid}.html", body + "\n")
    write(f"{deck}/order.txt", "\n".join(ids) + "\n")
    if not quiet:
        print(f"split {len(ids)} slides into {deck}")


TITLE_SLIDE = """<section class="slide" id="title" style="justify-content:center">
  <span class="slide-num"></span>
  <h1>{title}</h1>
  <p class="subtitle">Subtitle</p>
  <div class="presenter-notes">Opening line.</div>
</section>
"""

CONTENT_SLIDE = """<section class="slide" id="{sid}">
  <span class="slide-num"></span>
  <div class="slide-header">
    <span class="section-tag">Section</span>
    <h2>{heading}</h2>
  </div>
  <div class="slide-content">
    <p>Body.</p>
  </div>
  <div class="presenter-notes">What I say here.</div>
</section>
"""


def new(deck, title):
    if os.path.exists(deck):
        sys.exit(f"{deck} already exists")
    template = os.path.join(os.path.dirname(os.path.abspath(__file__)), "template.html")
    split(template, deck, quiet=True)
    for f in os.listdir(f"{deck}/slides"):
        os.remove(f"{deck}/slides/{f}")
    for part in ("head", "tail"):
        path = f"{deck}/frame/{part}.html"
        text = read(path)
        text = re.sub(r"<title>.*?</title>", f"<title>{html.escape(title)}</title>", text, flags=re.S)
        text = re.sub(r'(<meta name="description" content=")[^"]*', r"\1", text)
        write(path, text)
    write(f"{deck}/slides/title.html", TITLE_SLIDE.format(title=html.escape(title)))
    write(f"{deck}/slides/s1.html", CONTENT_SLIDE.format(sid="s1", heading="First point"))
    write(f"{deck}/order.txt", "title\ns1\n")
    write(f"{deck}/deck.conf", f"s3=s3://ksh-public/{os.path.basename(os.path.abspath(deck))}/index.html\n")
    build(deck)


def order(deck):
    ids = []
    for line in read(f"{deck}/order.txt").splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            ids.append(line)
    return ids


def is_appendix(body):
    return bool(re.search(r'<section\b[^>]*class="[^"]*\bappendix-slide\b', body))


def build(deck):
    ids = order(deck)
    bodies = []
    for sid in ids:
        path = f"{deck}/slides/{sid}.html"
        if not os.path.exists(path):
            sys.exit(f"order.txt names {sid} but {path} does not exist")
        bodies.append(read(path).rstrip() + "\n")
    unused = sorted(set(f[:-5] for f in os.listdir(f"{deck}/slides") if f.endswith(".html")) - set(ids))
    main_total = sum(not is_appendix(b) for b in bodies)
    out, main_n, app_n, outline = [], 0, 0, []
    for sid, body in zip(ids, bodies):
        if is_appendix(body):
            app_n += 1
            label = f"A{app_n}"
        else:
            main_n += 1
            label = f"{main_n} / {main_total}"
        body = SLIDE_NUM.sub(f'<span class="slide-num">{label}</span>', body, count=1)
        title = slide_title(body)
        out.append(f"\n<!-- {label.split(' /')[0]}: {sid} · {title} -->\n{body}")
        outline.append((label, sid, body))
    write(f"{deck}/index.html", read(f"{deck}/frame/head.html") + "".join(out) + read(f"{deck}/frame/tail.html"))
    write(f"{deck}/deck.md", text_version(deck, outline))
    print(f"built {deck}/index.html: {main_total} slides + {app_n} appendix")
    if unused:
        print(f"not in order.txt (not built): {', '.join(unused)}")


class Text(HTMLParser):
    """Visible text of one slide, in reading order, with reveal steps and notes marked."""

    BLOCK = {"p", "div", "li", "tr", "h1", "h2", "h3", "h4", "section", "figure", "figcaption", "pre", "table", "ul", "ol"}
    SKIP = {"script", "style"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lines, self.cur, self.skip, self.notes = [], [], 0, []
        self.in_notes, self.stack = 0, []

    def flush(self):
        line = re.sub(r"\s+", " ", "".join(self.cur)).strip()
        if line:
            (self.notes if self.in_notes else self.lines).append(line)
        self.cur = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = a.get("class") or ""
        marks = ["skipped"] if "slide-num" in cls and tag not in self.SKIP else []
        if tag in self.SKIP or "slide-num" in cls:
            self.skip += 1
        if "presenter-notes" in cls:
            self.flush()
            self.in_notes += 1
            marks.append("notes")
        if tag in self.BLOCK or "data-phase" in a:
            self.flush()
        if tag == "br":
            self.cur.append(" ")
        if "data-phase" in a and not self.in_notes and not self.skip:
            self.lines.append(f"[reveal {a['data-phase']}]")
        if tag == "li":
            self.cur.append("- ")
        if tag == "svg":
            self.flush()
            self.cur.append("[diagram] ")
        if tag in ("text", "tspan") and self.cur and not self.cur[-1].endswith(("] ", " · ")):
            self.cur.append(" · ")
        if tag == "img" and a.get("alt"):
            self.cur.append(f"[image: {a['alt']}] ")
        if tag in ("td", "th"):
            self.cur.append(" | ")
        if tag not in ("br", "img", "meta", "input", "hr"):
            self.stack.append((tag, marks))

    def handle_endtag(self, tag):
        if all(t != tag for t, _ in self.stack):
            return    # a void tag such as <br/>, which was never pushed
        while self.stack:
            t, marks = self.stack.pop()
            if t in self.SKIP or "skipped" in marks:
                self.skip -= 1
            if t in self.BLOCK or t == "svg":
                self.flush()
            if "notes" in marks:
                self.flush()
                self.in_notes -= 1
            if t == tag:
                break

    def handle_data(self, data):
        if not self.skip:
            self.cur.append(data)


def slide_title(body):
    m = re.search(r"<h[12]\b[^>]*>(.*?)</h[12]>", body, re.S)
    if not m:
        return "(untitled)"
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", m.group(1)))).strip()


def text_version(deck, outline):
    name = os.path.basename(os.path.abspath(deck))
    parts = [f"# {name}: text version\n\nGenerated by `deck.py build` from slides/. Do not edit; edit the slide files.\n"]
    for label, sid, body in outline:
        p = Text()
        p.feed(body)
        p.flush()
        lines = [l for l in p.lines if l]
        title = slide_title(body)
        # The title is already the heading; drop its first repeat from the body.
        if title in lines:
            lines.remove(title)
        head = f"\n## {label.split(' /')[0]}. {title}\n`{sid}`\n"
        text = "\n".join(lines)
        notes = " ".join(p.notes)
        parts.append(head + ("\n" + text + "\n" if text else "") + (f"\n> Notes: {notes}\n" if notes else ""))
    return "".join(parts)


def shot(deck, sid, phase=None):
    ids = order(deck)
    if sid not in ids:
        sys.exit(f"{sid} is not in order.txt")
    os.environ.setdefault("PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS", "true")
    from playwright.sync_api import sync_playwright
    out = f"{deck}/shots/{sid}{'-' + phase if phase else ''}.png"
    os.makedirs(f"{deck}/shots", exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--no-sandbox"])
        page = b.new_page(viewport={"width": 1920, "height": 1080})
        page.goto("file://" + os.path.abspath(f"{deck}/index.html"), wait_until="networkidle")
        page.evaluate("""([sid, phase]) => {
            document.body.classList.add('show-appendix');
            document.querySelectorAll('.slide').forEach(s => {
                s.classList.remove('current'); s.style.display = 'none';
            });
            const s = document.getElementById(sid);
            s.classList.add('current', 'active'); s.style.display = '';
            s.querySelectorAll('[data-phase]').forEach(el => {
                if (phase === null || +el.dataset.phase <= +phase) el.classList.add('visible');
            });
            ['nav', 'progress', 'notes-indicator', 'appendix-toggle'].forEach(id => {
                const el = document.getElementById(id); if (el) el.style.display = 'none';
            });
        }""", [sid, phase])
        page.wait_for_timeout(400)
        page.screenshot(path=out)
        b.close()
    print(out)


def publish(deck):
    build(deck)
    conf = dict(l.split("=", 1) for l in read(f"{deck}/deck.conf").splitlines() if "=" in l)
    dest = conf["s3"].strip()
    subprocess.run(["aws", "s3", "cp", f"{deck}/index.html", dest, "--content-type", "text/html; charset=utf-8",
                    "--cache-control", "max-age=60"], check=True)
    print(f"published {dest}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    cmd, args = sys.argv[1], sys.argv[2:]
    {"new": new, "split": split,"build": build, "shot": shot, "publish": publish}[cmd](*args)
