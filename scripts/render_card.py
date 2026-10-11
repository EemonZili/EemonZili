"""Render the profile SVGs.

assets/now.svg is a now-playing card. Its cover, background and equalizer
all come from one color. assets/soular.svg is the 思想银河 project card.

Fonts are subset and embedded because GitHub serves README SVGs as images.

Usage: python scripts/render_card.py <noto-700.ttf> <noto-500.ttf> <Outfit[wght].ttf>
"""
import base64
import io
import random
import sys
from pathlib import Path

from fontTools.subset import Options, Subsetter
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ASSETS = Path(__file__).resolve().parent.parent / "assets"
OUT = ASSETS / "now.svg"
SOULAR = ASSETS / "soular.svg"

W, H = 540, 135
COVER = "#4C6FFF"
BG = "#1B2550"
SONG = "晴天"
ARTIST = "周杰伦"
SONG_URL = "https://music.apple.com/hk/search?term=%E5%91%A8%E6%9D%B0%E4%BC%A6%20%E6%99%B4%E5%A4%A9"
BAR_COLORS = ("#E7EDFF", "#9DB4FF", "#4C6FFF", "#2C4DB5")


def font_face(path, weight):
    data = base64.b64encode(Path(path).read_bytes()).decode()
    return (
        f"@font-face{{font-family:'Noto Sans SC';font-weight:{weight};"
        f"src:url(data:font/ttf;base64,{data}) format('truetype')}}"
    )


def bars():
    rng = random.Random(7)
    x, y_base, width, gap, max_h = 148, 122, 3.4, 1.7, 32
    out = []
    i = 0
    while x + width < 524:
        dur = rng.uniform(0.52, 0.68)
        delay = -i * 0.003
        color = BAR_COLORS[i % len(BAR_COLORS)]
        out.append(
            f'<rect x="{x:.2f}" y="{y_base - max_h}" width="{width}" height="{max_h}" rx="1.6" '
            f'fill="{color}" class="bar" style="animation-duration:{dur:.3f}s;animation-delay:{delay:.3f}s"/>'
        )
        x += width + gap
        i += 1
    return "".join(out)


def render(bold, regular):
    faces = font_face(bold, 700) + font_face(regular, 500)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
  <style>{faces}
    .song{{font:700 30px 'Noto Sans SC',sans-serif}}
    .artist{{font:500 15px 'Noto Sans SC',sans-serif}}
    .bar{{opacity:.9;transform-box:fill-box;transform-origin:center bottom;animation:pulse ease-out infinite alternate}}
    @keyframes pulse{{0%{{transform:scaleY(.42)}}100%{{transform:scaleY(1)}}}}
  </style>
  <linearGradient id="song" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#F5F7FF"/><stop offset="1" stop-color="#B9C9FF"/>
  </linearGradient>
  <linearGradient id="artist" x1="1" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#F5F7FF"/><stop offset="1" stop-color="#9AACE8"/>
  </linearGradient>
  <filter id="shadow" x="-40%" y="-40%" width="180%" height="180%">
    <feDropShadow dx="0" dy="3" stdDeviation="4" flood-color="#0B1233" flood-opacity=".55"/>
  </filter>
  <clipPath id="card"><rect width="{W}" height="{H}" rx="10"/></clipPath>
</defs>
<a href="{SONG_URL}">
<g clip-path="url(#card)">
  <rect width="{W}" height="{H}" fill="{BG}"/>
  <rect x="-20" y="-20" width="180" height="180" fill="{COVER}" opacity=".55" filter="url(#shadow)"/>
  <rect width="{W}" height="{H}" fill="#000" fill-opacity=".28"/>
  <rect x="16" y="16" width="103" height="103" rx="8" fill="{COVER}" filter="url(#shadow)"/>
  <text x="336" y="58" text-anchor="middle" class="song" fill="url(#song)">{SONG}</text>
  <text x="336" y="82" text-anchor="middle" class="artist" fill="url(#artist)">{ARTIST}</text>
  {bars()}
</g>
</a>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="10" fill="none" stroke="#ffffff"/>
</svg>
'''


def subset_woff2(path, text, weight):
    font = TTFont(path)
    if "fvar" in font:
        font = instancer.instantiateVariableFont(font, {"wght": weight})
    opts = Options()
    opts.flavor = "woff2"
    opts.layout_features = ["kern", "liga"]
    sub = Subsetter(opts)
    sub.populate(text=text)
    sub.subset(font)
    buf = io.BytesIO()
    font.flavor = "woff2"
    font.save(buf)
    data = base64.b64encode(buf.getvalue()).decode()
    return (
        f"@font-face{{font-family:'Outfit';font-weight:{weight};"
        f"src:url(data:font/woff2;base64,{data}) format('woff2')}}"
    )


def render_soular(bold, outfit):
    faces = font_face(bold, 700) + subset_woff2(
        outfit,
        "Turns answers under one question into a map of viewpoints. React · TypeScript · Three.js",
        400,
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="720" height="128" viewBox="0 0 720 128">
<defs>
  <style>{faces}
    .title{{font:700 22px 'Noto Sans SC',sans-serif;fill:#16181d}}
    .desc{{font:400 14px 'Outfit',-apple-system,sans-serif;fill:#4b5160}}
    .meta{{font:400 12px 'Outfit',-apple-system,sans-serif;fill:#4C6FFF}}
  </style>
  <clipPath id="c"><rect width="720" height="128" rx="8"/></clipPath>
</defs>
<g clip-path="url(#c)">
  <rect width="720" height="128" fill="#ffffff"/>
  <rect width="6" height="128" fill="{COVER}"/>
  <text x="32" y="52" class="title">思想银河</text>
  <text x="32" y="78" class="desc">Turns answers under one question into a map of viewpoints.</text>
  <text x="32" y="102" class="meta">React  ·  TypeScript  ·  Three.js</text>
</g>
<rect x=".5" y=".5" width="719" height="127" rx="8" fill="none" stroke="#e6e8ee"/>
</svg>
'''


def main(argv):
    if len(argv) != 4:
        print(__doc__)
        return 2
    ASSETS.mkdir(exist_ok=True)
    OUT.write_text(render(argv[1], argv[2]), encoding="utf-8")
    SOULAR.write_text(render_soular(argv[1], argv[3]), encoding="utf-8")
    for path in (OUT, SOULAR):
        print(f"{path.name} {path.stat().st_size // 1024} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
