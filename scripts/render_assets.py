import random
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"


def stars(rng, w, h, n, min_r=0.4, max_r=1.6):
    out = []
    for _ in range(n):
        x, y = rng.uniform(0, w), rng.uniform(0, h)
        r = rng.uniform(min_r, max_r)
        dur = rng.uniform(2.5, 6.0)
        delay = rng.uniform(0, 6.0)
        out.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" fill="#fff" class="tw" '
            f'style="animation-duration:{dur:.2f}s;animation-delay:-{delay:.2f}s"/>'
        )
    return "\n".join(out)


def banner():
    w, h = 1000, 320
    rng = random.Random(7)
    nodes = [(640, 90), (720, 190), (820, 110), (900, 220), (860, 60), (760, 270), (950, 140)]
    edges = [(0, 1), (0, 2), (1, 2), (2, 4), (2, 6), (1, 3), (3, 6), (1, 5), (5, 3), (4, 6)]
    edge_svg = []
    for i, (a, b) in enumerate(edges):
        (x1, y1), (x2, y2) = nodes[a], nodes[b]
        edge_svg.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="edge"/>')
        edge_svg.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="flow" '
            f'style="animation-delay:-{i * 0.37:.2f}s"/>'
        )
    node_svg = []
    for i, (x, y) in enumerate(nodes):
        r = 9 if i in (1, 2) else 6
        node_svg.append(
            f'<circle cx="{x}" cy="{y}" r="{r * 2.6}" fill="url(#glow)" class="pulse" '
            f'style="animation-delay:-{i * 0.6:.1f}s"/>'
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="#0b1024" stroke="#8b9cff" stroke-width="2"/>'
            f'<circle cx="{x}" cy="{y}" r="{r * 0.45:.1f}" fill="#c4b5fd"/>'
        )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#070a1a"/><stop offset="0.55" stop-color="#11143a"/><stop offset="1" stop-color="#241047"/>
  </linearGradient>
  <radialGradient id="neb1" cx="0.78" cy="0.35" r="0.5"><stop offset="0" stop-color="#6d5dfc" stop-opacity="0.45"/><stop offset="1" stop-color="#6d5dfc" stop-opacity="0"/></radialGradient>
  <radialGradient id="neb2" cx="0.12" cy="0.95" r="0.45"><stop offset="0" stop-color="#22d3ee" stop-opacity="0.22"/><stop offset="1" stop-color="#22d3ee" stop-opacity="0"/></radialGradient>
  <radialGradient id="glow"><stop offset="0" stop-color="#a78bfa" stop-opacity="0.75"/><stop offset="1" stop-color="#a78bfa" stop-opacity="0"/></radialGradient>
  <linearGradient id="title" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#e0e7ff"/><stop offset="0.5" stop-color="#a5b4fc"/><stop offset="1" stop-color="#67e8f9"/>
  </linearGradient>
  <clipPath id="card"><rect width="{w}" height="{h}" rx="18"/></clipPath>
</defs>
<style>
  .tw{{animation:tw ease-in-out infinite}}
  @keyframes tw{{0%,100%{{opacity:.15}}50%{{opacity:.95}}}}
  .edge{{stroke:#8b9cff;stroke-opacity:.18;stroke-width:1.2}}
  .flow{{stroke:#67e8f9;stroke-width:2;stroke-linecap:round;stroke-dasharray:6 160;animation:flow 3.2s linear infinite}}
  @keyframes flow{{to{{stroke-dashoffset:-166}}}}
  .pulse{{animation:pulse 3.6s ease-in-out infinite;transform-box:fill-box;transform-origin:center}}
  @keyframes pulse{{0%,100%{{opacity:.35;transform:scale(.8)}}50%{{opacity:.9;transform:scale(1.15)}}}}
  .orbit{{animation:spin 26s linear infinite;transform-origin:780px 165px}}
  @keyframes spin{{to{{transform:rotate(360deg)}}}}
  .cursor{{animation:blink 1s steps(1) infinite}}
  @keyframes blink{{50%{{opacity:0}}}}
</style>
<g clip-path="url(#card)">
  <rect width="{w}" height="{h}" fill="url(#bg)"/>
  <rect width="{w}" height="{h}" fill="url(#neb1)"/>
  <rect width="{w}" height="{h}" fill="url(#neb2)"/>
  {stars(rng, w, h, 120)}
  <g class="orbit">
    <ellipse cx="780" cy="165" rx="230" ry="230" fill="none" stroke="#a5b4fc" stroke-opacity=".08" stroke-dasharray="2 8"/>
    <circle cx="1010" cy="165" r="3.5" fill="#67e8f9"/>
  </g>
  {"".join(edge_svg)}
  {"".join(node_svg)}
  <g>
    <text x="64" y="128" font-family="{SANS}" font-size="64" font-weight="800" fill="url(#title)" letter-spacing="-1">Eemon</text>
    <text x="66" y="170" font-family="{SANS}" font-size="20" font-weight="500" fill="#c7d2fe" letter-spacing="1">Backend Engineer  ·  AI Agents  ·  Real-time Data</text>
  </g>
  <rect x="64" y="204" width="470" height="44" rx="10" fill="#0b1024" fill-opacity=".7" stroke="#8b9cff" stroke-opacity=".25"/>
  <text x="82" y="232" font-family="{MONO}" font-size="15" fill="#67e8f9">❯</text>
  <clipPath id="type"><rect x="102" y="210" width="0" height="34">
    <animate attributeName="width" values="372;372;0;0;372" keyTimes="0;.45;.55;.62;1" dur="8s" repeatCount="indefinite"/>
  </rect></clipPath>
  <text x="102" y="232" font-family="{MONO}" font-size="15" fill="#e0e7ff" clip-path="url(#type)">building agents that speak plain language</text>
  <rect x="478" y="217" width="8" height="19" fill="#67e8f9" class="cursor">
    <animate attributeName="x" values="478;478;104;104;478" keyTimes="0;.45;.55;.62;1" dur="8s" repeatCount="indefinite"/>
  </rect>
</g>
<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="18" fill="none" stroke="#8b9cff" stroke-opacity=".25"/>
</svg>
'''


def card(title, subtitle, desc_lines, tags, accent, icon, seed):
    w, h = 490, 190
    rng = random.Random(seed)
    desc = "".join(
        f'<text x="28" y="{104 + i * 22}" font-family="{SANS}" font-size="14" fill="#c7d2fe">{line}</text>'
        for i, line in enumerate(desc_lines)
    )
    x = 28
    tag_svg = []
    for t in tags:
        tw = 14 + len(t) * 7.4
        tag_svg.append(
            f'<rect x="{x}" y="150" width="{tw:.0f}" height="24" rx="12" fill="{accent}" fill-opacity=".14" stroke="{accent}" stroke-opacity=".45"/>'
            f'<text x="{x + tw / 2:.0f}" y="166" text-anchor="middle" font-family="{MONO}" font-size="12" fill="{accent}">{t}</text>'
        )
        x += tw + 8
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#090c20"/><stop offset="1" stop-color="#18123a"/></linearGradient>
  <radialGradient id="neb" cx="0.92" cy="0.1" r="0.7"><stop offset="0" stop-color="{accent}" stop-opacity=".35"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/></radialGradient>
  <linearGradient id="line" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{accent}"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/></linearGradient>
  <clipPath id="c"><rect width="{w}" height="{h}" rx="16"/></clipPath>
</defs>
<style>
  .tw{{animation:tw ease-in-out infinite}}
  @keyframes tw{{0%,100%{{opacity:.1}}50%{{opacity:.8}}}}
  .scan{{animation:scan 5s ease-in-out infinite}}
  @keyframes scan{{0%{{transform:translateX(-200px)}}100%{{transform:translateX(560px)}}}}
</style>
<g clip-path="url(#c)">
  <rect width="{w}" height="{h}" fill="url(#bg)"/>
  <rect width="{w}" height="{h}" fill="url(#neb)"/>
  {stars(rng, w, h, 28, 0.3, 1.1)}
  <rect x="0" y="0" width="160" height="2" fill="url(#line)" class="scan"/>
  <text x="28" y="54" font-family="{SANS}" font-size="26">{icon}</text>
  <text x="66" y="52" font-family="{SANS}" font-size="22" font-weight="700" fill="#eef2ff">{title}</text>
  <text x="28" y="78" font-family="{MONO}" font-size="12" fill="{accent}" letter-spacing="1">{subtitle}</text>
  {desc}
  {"".join(tag_svg)}
  <text x="{w - 28}" y="52" text-anchor="end" font-family="{SANS}" font-size="18" fill="{accent}">↗</text>
</g>
<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="16" fill="none" stroke="{accent}" stroke-opacity=".35"/>
</svg>
'''


def main():
    OUT.mkdir(exist_ok=True)
    (OUT / "banner.svg").write_text(banner(), encoding="utf-8")
    (OUT / "card-campus.svg").write_text(card(
        "Campus Review", "WEB APP · CAMPUS COMMUNITY",
        ["Reviews, ratings and comments for campus life,", "with WeChat login and a role-based admin."],
        ["React", "TypeScript", "Vite"], "#67e8f9", "🏫", 11,
    ), encoding="utf-8")
    (OUT / "card-galaxy.svg").write_text(card(
        "思想银河", "HACKATHON · 3D VIEWPOINT MAP",
        ["Every answer under one question becomes a star;", "position shows stance, distance shows disagreement."],
        ["React", "Three.js", "Cloudflare Workers"], "#c084fc", "🌌", 23,
    ), encoding="utf-8")


if __name__ == "__main__":
    main()
