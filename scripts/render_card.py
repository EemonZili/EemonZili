"""Render the neofetch-style profile card as light and dark SVGs."""

import json
import os
import urllib.request
from html import escape
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps

USER = "EemonZili"
ROOT = Path(__file__).resolve().parent.parent

ASCII_COLS, ASCII_ROWS = 38, 21
ASCII_CROP = (60, 50, 340, 350)
RAMP = " .:-=+*#%@"

# Sized for the widest common monospace fallback (Menlo, 0.602em) so nothing overflows.
FONT_SIZE = 14
LINE_HEIGHT = 19
CHAR_WIDTH = FONT_SIZE * 0.602
PAD = 20
INFO_WIDTH = 60
INFO_X = round(PAD + (ASCII_COLS + 3) * CHAR_WIDTH)
WIDTH = round(INFO_X + INFO_WIDTH * CHAR_WIDTH + PAD)
TOP = 32

THEMES = {
    "light": {"bg": "#f6f8fa", "text": "#24292f", "art": "#57606a", "key": "#953800", "value": "#0a3069", "dots": "#c2cfde"},
    "dark": {"bg": "#161b22", "text": "#c9d1d9", "art": "#8b949e", "key": "#ffa657", "value": "#a5d6ff", "dots": "#616e7f"},
}


def api(path):
    req = urllib.request.Request(f"https://api.github.com{path}", headers={"Accept": "application/vnd.github+json"})
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def stats():
    user = api(f"/users/{USER}")
    commits = api(f"/search/commits?q=author:{USER}&per_page=1")["total_count"]
    return {"repos": user["public_repos"], "commits": commits}


def ascii_art(avatar_url):
    with urllib.request.urlopen(avatar_url, timeout=30) as resp:
        im = Image.open(BytesIO(resp.read())).convert("L").resize((400, 400))
    im = ImageOps.autocontrast(im.crop(ASCII_CROP), cutoff=3)
    im = ImageEnhance.Contrast(im).enhance(1.6).resize((ASCII_COLS, ASCII_ROWS))
    return [
        "".join(RAMP[int((255 - im.getpixel((x, y))) * (len(RAMP) - 1) / 255)] for x in range(ASCII_COLS))
        for y in range(ASCII_ROWS)
    ]


def info_lines(s):
    return [
        ("title", "eemon@github"),
        ("kv", "OS", "macOS, Linux"),
        ("kv", "Role", "Backend & AI Agent Developer"),
        ("kv", "Focus", "Real-time pipelines, LLM agents"),
        ("blank",),
        ("kv", "Languages.Programming", "Go, Java, Python, TypeScript"),
        ("kv", "Languages.Real", "Chinese, English"),
        ("kv", "Infra", "Kafka, Redis, MySQL, Doris"),
        ("kv", "Observability", "Grafana, alerting"),
        ("blank",),
        ("kv", "AI.Building", "Auto-labeling, RAG, tool agents"),
        ("kv", "AI.Learning", "Context engineering, evals"),
        ("kv", "Hobbies", "Tech books, game prototypes"),
        ("blank",),
        ("section", "Contact"),
        ("kv", "Blog", "eemonzili.github.io"),
        ("kv", "GitHub", USER),
        ("blank",),
        ("section", "GitHub Stats"),
        ("stats", s),
    ]


def dots(n):
    return " " + "." * max(n, 2) + " "


def render_info(lines):
    out = []
    for i, line in enumerate(lines):
        y = TOP + i * LINE_HEIGHT
        kind = line[0]
        if kind == "blank":
            continue
        if kind == "title":
            rule = "-" * (INFO_WIDTH - len(line[1]) - 1)
            out.append(f'<tspan x="{INFO_X}" y="{y}">{escape(line[1])} {rule}</tspan>')
        elif kind == "section":
            rule = "-" * (INFO_WIDTH - len(line[1]) - 3)
            out.append(f'<tspan x="{INFO_X}" y="{y}">- {escape(line[1])} {rule}</tspan>')
        elif kind == "kv":
            key, value = line[1], line[2]
            gap = INFO_WIDTH - 2 - len(key) - 1 - len(value) - 2
            out.append(
                f'<tspan x="{INFO_X}" y="{y}" class="cc">. </tspan>'
                f'<tspan class="key">{escape(key)}</tspan>:'
                f'<tspan class="cc">{dots(gap)}</tspan>'
                f'<tspan class="value">{escape(value)}</tspan>'
            )
        elif kind == "stats":
            s = line[1]
            out.append(
                f'<tspan x="{INFO_X}" y="{y}" class="cc">. </tspan>'
                f'<tspan class="key">Repos</tspan>: <tspan class="value">{s["repos"]}</tspan>'
                f'<tspan class="cc"> | </tspan><tspan class="key">Commits</tspan>: <tspan class="value">{s["commits"]}</tspan>'
            )
    return "\n".join(out)


def render(theme, art, lines):
    c = THEMES[theme]
    rows = max(len(lines) + 1, ASCII_ROWS)
    height = TOP + rows * LINE_HEIGHT - LINE_HEIGHT // 2
    art_top = TOP + (rows - ASCII_ROWS) // 2 * LINE_HEIGHT
    art_spans = "\n".join(
        f'<tspan x="{PAD}" y="{art_top + i * LINE_HEIGHT}">{escape(row)}</tspan>' for i, row in enumerate(art)
    )
    return f"""<?xml version='1.0' encoding='UTF-8'?>
<svg xmlns="http://www.w3.org/2000/svg" font-family="'SFMono-Regular',Menlo,Consolas,'Liberation Mono',monospace" width="{WIDTH}" height="{height}" font-size="{FONT_SIZE}px">
<style>
.key {{ fill: {c['key']}; }}
.value {{ fill: {c['value']}; }}
.cc {{ fill: {c['dots']}; }}
.ascii {{ fill: {c['art']}; }}
text, tspan {{ white-space: pre; }}
</style>
<rect width="{WIDTH}" height="{height}" fill="{c['bg']}" rx="12"/>
<text x="{PAD}" y="{art_top}" class="ascii">
{art_spans}
</text>
<text x="{INFO_X}" y="{TOP}" fill="{c['text']}">
{render_info(lines)}
</text>
</svg>
"""


def main():
    user = api(f"/users/{USER}")
    art = ascii_art(user["avatar_url"] + "&s=400")
    lines = info_lines(stats())
    for theme in THEMES:
        (ROOT / f"{theme}_mode.svg").write_text(render(theme, art, lines), encoding="utf-8")


if __name__ == "__main__":
    main()
