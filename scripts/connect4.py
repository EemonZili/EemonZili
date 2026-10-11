"""Community Connect Four played through GitHub issues.

Usage:
  python scripts/connect4.py render
  python scripts/connect4.py move "<issue title>" <github login>

The move command prints a one-line result for the issue comment and exits
with code 3 when the move is rejected, leaving state and files untouched.
"""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "game" / "state.json"
ASSETS = ROOT / "assets" / "connect4"
README = ROOT / "README.md"
REPO = "EemonZili/EemonZili"
ROWS, COLS = 6, 7
TEAMS = {
    "cyan": {"label": "Cyan", "fill": "#67e8f9", "core": "#cffafe", "glow": "#22d3ee"},
    "violet": {"label": "Violet", "fill": "#c084fc", "core": "#f3e8ff", "glow": "#a855f7"},
}
TITLE_RE = re.compile(r"^connect4\|drop\|([1-7])$")
START, END = "<!-- CONNECT4:START -->", "<!-- CONNECT4:END -->"
CELL, HEAD = 64, 40
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"


def new_board():
    return [[None] * COLS for _ in range(ROWS)]


def load():
    if STATE.exists():
        return json.loads(STATE.read_text(encoding="utf-8"))
    return {
        "board": new_board(), "turn": "cyan", "last": None,
        "moves": 0, "games": 0, "wins": {"cyan": 0, "violet": 0, "draw": 0},
        "players": [], "history": [], "result": None,
    }


def save(state):
    STATE.parent.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def winner(board, r, c):
    team = board[r][c]
    for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
        n = 1
        for sign in (1, -1):
            rr, cc = r + dr * sign, c + dc * sign
            while 0 <= rr < ROWS and 0 <= cc < COLS and board[rr][cc] == team:
                n += 1
                rr, cc = rr + dr * sign, cc + dc * sign
        if n >= 4:
            return True
    return False


def apply_move(state, title, login):
    m = TITLE_RE.match(title.strip())
    if not m:
        return False, "Unrecognised move. Use the column links on the profile page."
    if not re.fullmatch(r"[A-Za-z0-9-]{1,39}", login):
        return False, "Moves from bot accounts are not accepted."
    col = int(m.group(1)) - 1
    board = state["board"]
    row = next((r for r in range(ROWS - 1, -1, -1) if board[r][col] is None), None)
    if row is None:
        return False, f"Column {col + 1} is full, pick another one."
    team = state["turn"]
    board[row][col] = team
    state["last"] = [row, col]
    state["moves"] += 1
    if login not in state["players"]:
        state["players"].append(login)
    state["history"] = ([{
        "team": team, "col": col + 1, "by": login,
        "at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    }] + state["history"])[:5]
    label = TEAMS[team]["label"]
    if winner(board, row, col):
        state["wins"][team] += 1
        state["games"] += 1
        state["result"] = f"{label} won the last game, final disc by @{login}."
        msg = f"{label} wins! A new game has started."
        state["board"], state["last"], state["turn"] = new_board(), None, "cyan"
        return True, msg
    if all(board[0][c] is not None for c in range(COLS)):
        state["wins"]["draw"] += 1
        state["games"] += 1
        state["result"] = "The last game ended in a draw."
        state["board"], state["last"], state["turn"] = new_board(), None, "cyan"
        return True, "The board is full, it's a draw. A new game has started."
    state["turn"] = "violet" if team == "cyan" else "cyan"
    return True, f"{label} dropped a disc in column {col + 1}. It's {TEAMS[state['turn']]['label']}'s turn."


def disc(cx, cy, team, last):
    t = TEAMS[team]
    ring = (f'<circle cx="{cx}" cy="{cy}" r="27" fill="none" stroke="#fff" stroke-width="2" class="last"/>'
            if last else "")
    return (f'<circle cx="{cx}" cy="{cy}" r="30" fill="{t["glow"]}" opacity=".28"/>'
            f'<circle cx="{cx}" cy="{cy}" r="23" fill="{t["fill"]}"/>'
            f'<circle cx="{cx - 7}" cy="{cy - 7}" r="7" fill="{t["core"]}" opacity=".7"/>{ring}')


def render_column(state, col):
    w, h = CELL, HEAD + ROWS * CELL + 12
    full = state["board"][0][col] is not None
    left, right = col == 0, col == COLS - 1
    bx = 0 if left else -20
    bw = w + (0 if left else 20) + (0 if right else 20)
    cells = []
    for r in range(ROWS):
        cx, cy = w // 2, HEAD + r * CELL + CELL // 2
        cells.append(f'<circle cx="{cx}" cy="{cy}" r="24" fill="#05071a" stroke="#8b9cff" stroke-opacity=".22"/>')
        team = state["board"][r][col]
        if team:
            cells.append(disc(cx, cy, team, state["last"] == [r, col]))
    turn = TEAMS[state["turn"]]
    label = "FULL" if full else f"▼ {col + 1}"
    color = "#64748b" if full else turn["fill"]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0b1024"/><stop offset="1" stop-color="#1a1240"/></linearGradient></defs>
<style>.last{{animation:p 1.6s ease-in-out infinite}}@keyframes p{{50%{{opacity:.2}}}}
.hint{{animation:b 1.8s ease-in-out infinite}}@keyframes b{{50%{{transform:translateY(3px)}}}}</style>
<rect x="{bx}" y="0" width="{bw}" height="{h}" rx="16" fill="url(#bg)"/>
<rect x="{bx}" y="0" width="{bw}" height="{HEAD}" rx="16" fill="{color}" fill-opacity=".08"/>
<rect x="{bx}" y="{HEAD - 16}" width="{bw}" height="16" fill="#0b1024"/>
<text x="{w // 2}" y="{HEAD - 13}" text-anchor="middle" font-family="{MONO}" font-size="14" font-weight="700" fill="{color}" class="{'' if full else 'hint'}">{label}</text>
{"".join(cells)}
</svg>
'''


def issue_link(col):
    title = quote(f"connect4|drop|{col}", safe="")
    body = quote("Just click **Create** — the bot will drop your disc and close this issue in about a minute.")
    return f"https://github.com/{REPO}/issues/new?title={title}&body={body}"


def readme_block(state):
    v = state["moves"]
    turn = TEAMS[state["turn"]]
    dot = {"cyan": "🔵", "violet": "🟣"}
    cols = "".join(
        f'<a href="{issue_link(c + 1)}"><img src="./assets/connect4/col{c + 1}.svg?v={v}" width="9%" alt="Drop in column {c + 1}"/></a>'
        for c in range(COLS)
    )
    rows = "\n".join(
        f"| {dot[h['team']]} {TEAMS[h['team']]['label']} | {h['col']} | [@{h['by']}](https://github.com/{h['by']}) |"
        for h in state["history"]
    ) or "| — | — | Be the first! |"
    result = f"<br/><sub>{state['result']}</sub>" if state["result"] else ""
    w = state["wins"]
    return f"""{START}
<p align="center">
  <b>Anyone can play.</b> It's {dot[state['turn']]} <b>{turn['label']}</b>'s turn — click a column to drop a disc.{result}
</p>

<p align="center">{cols}</p>

<p align="center">
  <sub>🎯 {state['moves']} moves · 🏁 {state['games']} games · 👥 {len(state['players'])} players · 🔵 {w['cyan']} : {w['violet']} 🟣</sub>
</p>

<details>
<summary>Recent moves &amp; how it works</summary>

| Team | Column | Player |
| :-- | :-: | :-- |
{rows}

Clicking a column opens a pre-filled issue. A GitHub Action reads the title, drops the disc, redraws the board and closes the issue.

</details>
{END}"""


def render(state):
    ASSETS.mkdir(parents=True, exist_ok=True)
    for c in range(COLS):
        (ASSETS / f"col{c + 1}.svg").write_text(render_column(state, c), encoding="utf-8")
    text = README.read_text(encoding="utf-8")
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    if not pattern.search(text):
        raise SystemExit("README is missing the CONNECT4 markers")
    README.write_text(pattern.sub(lambda _: readme_block(state), text), encoding="utf-8")


def main(argv):
    state = load()
    if argv[1:2] == ["render"]:
        save(state)
        render(state)
        return 0
    if argv[1:2] == ["move"] and len(argv) == 4:
        ok, msg = apply_move(state, argv[2], argv[3])
        print(msg)
        if not ok:
            return 3
        save(state)
        render(state)
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
