"""Render assets/now.svg, a "now building" card in the style of a now-playing widget.

Fonts are subset and embedded because GitHub serves README SVGs as images,
which cannot load external fonts.

Usage: python scripts/render_card.py <Outfit[wght].ttf> <JetBrainsMono[wght].ttf> <avatar image>
"""
import base64
import io
import random
import sys
from pathlib import Path

from fontTools.subset import Options, Subsetter
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from PIL import Image

OUT = Path(__file__).resolve().parent.parent / "assets" / "now.svg"
W, H = 540, 180
LABEL = "NOW BUILDING"
TITLE = "AI Agents & Data Pipelines"
SUBTITLE = "Eemon · Backend Engineer"
TAGS = "Go  ·  Java  ·  Python  ·  TypeScript"


def font_face(path, family, weight, text):
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
    return (f"@font-face{{font-family:'{family}';font-weight:{weight};"
            f"src:url(data:font/woff2;base64,{data}) format('woff2')}}")


def avatar_data(path, size):
    img = Image.open(path).convert("RGB").resize((size, size), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=82)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def bars(x0, y_base, n=48, width=4, gap=3, max_h=22):
    rng = random.Random(3)
    out = []
    for i in range(n):
        dur = rng.uniform(0.7, 1.5)
        delay = rng.uniform(0, 1.5)
        out.append(
            f'<rect x="{x0 + i * (width + gap)}" y="{y_base - max_h}" width="{width}" height="{max_h}" rx="2" '
            f'class="bar" style="animation-duration:{dur:.2f}s;animation-delay:-{delay:.2f}s"/>'
        )
    return "".join(out)


def render(outfit, mono, avatar):
    faces = "".join([
        font_face(outfit, "Outfit", 600, TITLE),
        font_face(outfit, "Outfit", 400, SUBTITLE + TAGS),
        font_face(mono, "JBMono", 500, LABEL),
    ])
    pic = avatar_data(avatar, 240)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
  <style>{faces}
    .label{{font:500 11px 'JBMono',ui-monospace,Menlo,monospace;letter-spacing:2.5px;fill:#fff;fill-opacity:.65}}
    .title{{font:600 26px 'Outfit',-apple-system,'Segoe UI',sans-serif;fill:#fff}}
    .sub{{font:400 16px 'Outfit',-apple-system,'Segoe UI',sans-serif;fill:#fff;fill-opacity:.8}}
    .tags{{font:400 13px 'Outfit',-apple-system,'Segoe UI',sans-serif;fill:#fff;fill-opacity:.55}}
    .bar{{fill:#fff;fill-opacity:.85;transform-box:fill-box;transform-origin:bottom;animation:eq ease-in-out infinite alternate}}
    @keyframes eq{{0%{{transform:scaleY(.15)}}50%{{transform:scaleY(.6)}}100%{{transform:scaleY(1)}}}}
  </style>
  <clipPath id="card"><rect width="{W}" height="{H}" rx="14"/></clipPath>
  <clipPath id="cover"><rect x="24" y="24" width="132" height="132" rx="10"/></clipPath>
  <filter id="blur" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="28"/></filter>
  <filter id="shadow" x="-30%" y="-30%" width="160%" height="160%"><feDropShadow dx="0" dy="6" stdDeviation="8" flood-color="#000" flood-opacity=".45"/></filter>
</defs>
<g clip-path="url(#card)">
  <image href="{pic}" xlink:href="{pic}" x="-40" y="-{(W + 80 - H) // 2}" width="{W + 80}" height="{W + 80}" preserveAspectRatio="xMidYMid slice" filter="url(#blur)"/>
  <rect width="{W}" height="{H}" fill="#0b0b10" fill-opacity=".55"/>
  <rect x="24" y="24" width="132" height="132" rx="10" fill="#000" filter="url(#shadow)"/>
  <image href="{pic}" xlink:href="{pic}" x="24" y="24" width="132" height="132" clip-path="url(#cover)"/>
  <text x="180" y="44" class="label">{LABEL}</text>
  <text x="180" y="78" class="title">{TITLE.replace("&", "&amp;")}</text>
  <text x="180" y="103" class="sub">{SUBTITLE}</text>
  <text x="180" y="124" class="tags">{TAGS}</text>
  {bars(180, 156)}
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="14" fill="none" stroke="#fff" stroke-opacity=".9"/>
</svg>
'''


def main(argv):
    if len(argv) != 4:
        print(__doc__)
        return 2
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(render(*argv[1:]), encoding="utf-8")
    print(f"{OUT} {OUT.stat().st_size // 1024} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
