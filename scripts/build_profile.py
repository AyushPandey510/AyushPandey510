#!/usr/bin/env python3
"""
Profile builder for github.com/<username>.

Pulls every public repo + commit history from the GitHub REST API, then:
  * renders neon SVG widgets into assets/ (header, project cards, timeline,
    commit radar, language bar)
  * rewrites the auto-generated blocks in README.md between
    <!-- AUTO:<NAME>:START --> and <!-- AUTO:<NAME>:END --> markers.

Standard library only. Run locally with:
    GH_TOKEN=<token> python scripts/build_profile.py
"""
from __future__ import annotations

import datetime as dt
import html
import json
import os
import re
import sys
import urllib.error
import urllib.request
from zoneinfo import ZoneInfo
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
CARDS = ASSETS / "cards"
README = ROOT / "README.md"
CONFIG = json.loads((ROOT / "profile.config.json").read_text())

USER = CONFIG["username"]
API = "https://api.github.com"
NOW = dt.datetime.now(dt.timezone.utc)
TZ = ZoneInfo(CONFIG.get("timezone", "UTC"))

# ── palette ────────────────────────────────────────────────────────────────
BG, PANEL, GRID = "#0D1117", "#161B22", "#21262D"
TEXT, MUTED, DIM = "#E6EDF3", "#8B949E", "#6E7681"
ACCENT = "#6E8CA8"  # single steel-blue accent
CAT = {  # category → muted solid tone
    "realtime": "#6E8CA8",
    "ai": "#8A7FA8",
    "mobile": "#6F9A82",
    "security": "#A86B6B",
    "backend": "#A8906A",
    "web": "#7A92A8",
    "tools": "#8C956A",
    "other": "#8B949E",
}
LANG_COLOR = {
    "Rust": "#DEA584", "Dart": "#00B4AB", "Python": "#3572A5",
    "TypeScript": "#3178C6", "JavaScript": "#F1E05A", "Go": "#00ADD8",
    "Kotlin": "#A97BFF", "Swift": "#F05138", "HTML": "#E34C26",
    "CSS": "#663399", "Shell": "#89E051", "C++": "#F34B7D", "C": "#555555",
    "Java": "#B07219", "Makefile": "#427819", "Dockerfile": "#384D54",
    "PLpgSQL": "#336790", "TeX": "#3D6117", "Jupyter Notebook": "#DA5B0B",
}
LANG_CAT = {"Dart": "mobile", "Kotlin": "mobile", "Swift": "mobile",
            "Rust": "backend", "Go": "backend", "Python": "ai",
            "TypeScript": "web", "JavaScript": "web", "HTML": "web",
            "Makefile": "tools", "Shell": "tools"}
IGNORED_LANGS = {"CMake", "C++", "Swift", "Objective-C", "Ruby", "HTML",
                 "Batchfile", "Procfile"}  # Flutter/iOS scaffolding noise
MONO = "'JetBrains Mono','Fira Code','SFMono-Regular',Consolas,'Liberation Mono',monospace"


# ── GitHub API ─────────────────────────────────────────────────────────────
class GitHub:
    def __init__(self, token: str | None):
        self.token = token

    def _req(self, url: str):
        req = urllib.request.Request(url, headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": f"{USER}-profile-builder",
            "X-GitHub-Api-Version": "2022-11-28",
            **({"Authorization": f"Bearer {self.token}"} if self.token else {}),
        })
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read() or b"null"), r.headers
        except urllib.error.HTTPError as e:
            if e.code in (404, 409):  # 409 = empty repository
                return None, e.headers
            raise

    def get(self, path: str):
        return self._req(path if path.startswith("http") else API + path)

    def paged(self, path: str, limit: int = 1000):
        out, url = [], API + path
        while url and len(out) < limit:
            data, headers = self._req(url)
            if not data:
                break
            out.extend(data)
            url = _next_link(headers.get("Link", ""))
        return out[:limit]

    def repos(self):
        return self.paged(f"/users/{USER}/repos?per_page=100&type=owner&sort=pushed")

    def commits(self, repo: str, limit: int = 100, since: str | None = None):
        q = f"&since={since}" if since else ""
        return self.paged(f"/repos/{USER}/{repo}/commits?per_page=100{q}", limit)

    def commit_total_and_first(self, repo: str):
        """Total commit count + oldest commit, using the Link header trick."""
        data, headers = self.get(f"/repos/{USER}/{repo}/commits?per_page=1")
        if not data:
            return 0, None
        last = _rel_link(headers.get("Link", ""), "last")
        if not last:
            return 1, data[0]
        total = int(re.search(r"[?&]page=(\d+)", last).group(1))
        oldest, _ = self.get(last)
        return total, (oldest or [None])[0]

    def languages(self, repo: str):
        data, _ = self.get(f"/repos/{USER}/{repo}/languages")
        return data or {}


def _rel_link(link: str, rel: str):
    m = re.search(rf'<([^>]+)>;\s*rel="{rel}"', link or "")
    return m.group(1) if m else None


def _next_link(link: str):
    return _rel_link(link, "next")


# ── helpers ────────────────────────────────────────────────────────────────
def esc(s: str) -> str:
    return html.escape(s or "", quote=True)


def parse_ts(s: str) -> dt.datetime:
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def ago(t: dt.datetime) -> str:
    s = int((NOW - t).total_seconds())
    for unit, n in (("y", 31536000), ("mo", 2592000), ("w", 604800),
                    ("d", 86400), ("h", 3600), ("m", 60)):
        if s >= n:
            return f"{s // n}{unit} ago"
    return "just now"


def clip(s: str, n: int) -> str:
    s = " ".join((s or "").split())
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def wrap(s: str, width: int, lines: int) -> list[str]:
    words, out, cur = (s or "").split(), [], ""
    for w in words:
        if len(cur) + len(w) + (1 if cur else 0) > width:
            out.append(cur)
            cur = w
            if len(out) == lines:
                break
        else:
            cur = f"{cur} {w}".strip()
    else:
        if cur:
            out.append(cur)
    if len(out) > lines:
        out = out[:lines]
    if len(out) == lines and " ".join(out) != " ".join(words):
        out[-1] = clip(out[-1] + " …", width)
    return out


def is_mine(c: dict) -> bool:
    login = ((c.get("author") or {}).get("login") or "").lower()
    email = ((c.get("commit") or {}).get("author") or {}).get("email", "").lower()
    emails = {e.lower() for e in CONFIG.get("author_emails", [])}
    return login == USER.lower() or email in emails or (
        email.endswith("@users.noreply.github.com") and USER.lower() in email)


def status_of(last: dt.datetime | None, archived: bool):
    if archived:
        return "ARCHIVED", DIM
    if not last:
        return "EMPTY", DIM
    days = (NOW - last).days
    if days <= 14:
        return "ACTIVE", "#6F9A82"
    if days <= 120:
        return "STABLE", "#6E8CA8"
    return "DORMANT", "#8B949E"


# ── data collection ────────────────────────────────────────────────────────
def collect(gh: GitHub):
    hide = {h.lower() for h in CONFIG.get("hide", [])}
    projects = []
    for r in gh.repos():
        if r["fork"] or r["name"].lower() in hide or r.get("private"):
            continue
        name = r["name"]
        ov = CONFIG.get("overrides", {}).get(name, {})
        since = (NOW - dt.timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%SZ")
        commits = gh.commits(name, 1000, since=since) or gh.commits(name, 1)
        mine = [c for c in commits if is_mine(c)
                and parse_ts(c["commit"]["author"]["date"]) >= NOW - dt.timedelta(days=365)]
        total, oldest = gh.commit_total_and_first(name)
        raw_langs = gh.languages(name)
        langs = {k: v for k, v in raw_langs.items() if k not in IGNORED_LANGS} or raw_langs
        primary = max(langs, key=langs.get) if langs else (r.get("language") or "—")
        latest = (mine or commits or [None])[0]
        last_t = parse_ts(latest["commit"]["author"]["date"]) if latest else None
        first_t = parse_ts(oldest["commit"]["author"]["date"]) if oldest else last_t
        projects.append({
            "name": name,
            "title": ov.get("title", name),
            "tagline": ov.get("tagline") or r.get("description") or "No description yet.",
            "category": ov.get("category") or LANG_CAT.get(primary, "other"),
            "url": r["html_url"],
            "live": ov.get("live") or r.get("homepage") or "",
            "stars": r.get("stargazers_count", 0),
            "archived": r.get("archived", False),
            "langs": langs,
            "size": sum(raw_langs.values()),
            "primary": primary,
            "total": total,
            "first": first_t,
            "last": last_t,
            "last_msg": (latest or {}).get("commit", {}).get("message", "").split("\n")[0],
            "last_url": (latest or {}).get("html_url", r["html_url"]),
            "mine": [{
                "repo": name, "title": ov.get("title", name),
                "msg": c["commit"]["message"].split("\n")[0],
                "url": c["html_url"], "sha": c["sha"][:7],
                "t": parse_ts(c["commit"]["author"]["date"]),
            } for c in mine],
        })
    epoch = dt.datetime.min.replace(tzinfo=dt.timezone.utc)
    projects.sort(key=lambda p: p["last"] or epoch, reverse=True)
    return projects


# ── SVG widgets ────────────────────────────────────────────────────────────
def svg_open(w: int, h: int, extra: str = "") -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" font-family="{MONO}">{extra}')


def header_svg(projects, stats) -> str:
    W, H = 1000, 200
    cells = [("repositories", stats["repos"]), ("total commits", stats["commits"]),
             ("commits, 12 mo", stats["year"]), ("active days, 12 mo", stats["days"]),
             ("languages", stats["langs"]), ("active projects", stats["active"])]
    stat_svg = ""
    for i, (k, v) in enumerate(cells):
        x = 48 + i * 150
        stat_svg += (f'<text x="{x}" y="150" font-size="24" font-weight="700" fill="{TEXT}">{v}</text>'
                     f'<text x="{x}" y="170" font-size="12" fill="{MUTED}">{k}</text>')
    return (svg_open(W, H) +
            f'<rect width="{W}" height="{H}" rx="8" fill="{PANEL}"/>'
            f'<rect width="6" height="{H}" rx="3" fill="{ACCENT}"/>'
            f'<text x="48" y="68" font-size="40" font-weight="700" fill="{TEXT}">{esc(CONFIG["name"])}</text>'
            f'<text x="48" y="100" font-size="17" fill="{MUTED}">{esc(CONFIG.get("headline", ""))}</text>'
            f'<line x1="48" y1="118" x2="{W - 48}" y2="118" stroke="{GRID}"/>'
            + stat_svg +
            f'<text x="{W - 48}" y="68" font-size="11" text-anchor="end" fill="{DIM}">updated {NOW:%d %b %Y}</text>'
            '</svg>')


def card_svg(p: dict, idx: int) -> str:
    W, H = 480, 190
    c = CAT.get(p["category"], CAT["other"])
    st, sc = status_of(p["last"], p["archived"])
    langs = sorted(p["langs"].items(), key=lambda kv: -kv[1])[:4]
    total_b = sum(v for _, v in langs) or 1
    bar, x = "", 24
    for lang, b in langs:
        w = max(4, (W - 48) * b / total_b)
        bar += f'<rect x="{x:.1f}" y="112" width="{w:.1f}" height="6" fill="{LANG_COLOR.get(lang, MUTED)}"/>'
        x += w
    chips, cx = "", 24
    for lang, b in langs[:3]:
        label = f"{lang} {round(100 * b / total_b)}%"
        chips += (f'<circle cx="{cx + 4}" cy="136" r="4" fill="{LANG_COLOR.get(lang, MUTED)}"/>'
                  f'<text x="{cx + 13}" y="140" font-size="11" fill="{MUTED}">{esc(label)}</text>')
        cx += 22 + len(label) * 6.6
    tag = "".join(f'<text x="24" y="{72 + i * 18}" font-size="12.5" fill="{MUTED}">{esc(l)}</text>'
                  for i, l in enumerate(wrap(p["tagline"], 60, 2)))
    live = (f'<text x="{W - 24}" y="46" font-size="11" text-anchor="end" fill="{MUTED}">live ↗</text>'
            if p["live"] else "")
    when = ago(p["last"]) if p["last"] else "no commits"
    meta = f'{when} · {p["total"]} commits' + (f' · ★{p["stars"]}' if p["stars"] else "")
    return (svg_open(W, H) +
            f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="8" fill="{PANEL}" stroke="{GRID}"/>'
            f'<rect x="0" y="0" width="5" height="{H}" rx="2" fill="{c}"/>'
            f'<text x="24" y="28" font-size="10.5" letter-spacing="1" fill="{c}">{esc(p["category"].upper())}</text>'
            f'<circle cx="{W - 24 - len(st) * 7.4 - 10}" cy="24" r="3.5" fill="{sc}"/>'
            f'<text x="{W - 24}" y="28" font-size="10.5" text-anchor="end" letter-spacing="1" fill="{sc}">{st}</text>'
            f'<text x="24" y="50" font-size="20" font-weight="700" fill="{TEXT}">{esc(clip(p["title"], 30))}</text>'
            + live + tag +
            f'<rect x="24" y="112" width="{W - 48}" height="6" fill="{GRID}"/>{bar}{chips}'
            f'<line x1="24" y1="156" x2="{W - 24}" y2="156" stroke="{GRID}"/>'
            f'<text x="24" y="176" font-size="11.5" fill="{TEXT}">{esc(clip(p["last_msg"] or "—", 40))}</text>'
            f'<text x="{W - 24}" y="176" font-size="10.5" text-anchor="end" fill="{DIM}">{esc(meta)}</text>'
            '</svg>')


def timeline_svg(projects) -> str:
    rows = [p for p in projects if p["first"] and p["last"]][:14]
    if not rows:
        return svg_open(1000, 60) + "</svg>"
    start = min(p["first"] for p in rows).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    span = max((NOW - start).total_seconds(), 1)
    L, R, top, rh = 230, 970, 56, 26
    W, H = 1000, top + rh * len(rows) + 34
    X = lambda t: L + (R - L) * (t - start).total_seconds() / span
    axis, m = "", start
    step = 1 if (NOW - start).days < 400 else 2
    while m <= NOW:
        x = X(m)
        axis += (f'<line x1="{x:.1f}" y1="{top - 10}" x2="{x:.1f}" y2="{H - 30}" stroke="{GRID}" stroke-dasharray="2 4"/>'
                 f'<text x="{x:.1f}" y="{H - 12}" font-size="10" text-anchor="middle" fill="{DIM}">{m:%b %y}</text>')
        mo = m.month - 1 + step
        m = m.replace(year=m.year + mo // 12, month=mo % 12 + 1)
    bars = ""
    for i, p in enumerate(rows):
        y = top + i * rh
        c = CAT.get(p["category"], CAT["other"])
        x1, x2 = X(p["first"]), X(p["last"])
        bars += (f'<text x="{L - 14}" y="{y + 12}" font-size="12" text-anchor="end" fill="{TEXT}">{esc(clip(p["title"], 24))}</text>'
                 f'<rect x="{x1:.1f}" y="{y + 3}" width="{max(x2 - x1, 3):.1f}" height="10" rx="5" fill="{c}" opacity=".85"/>'
                 f'<circle cx="{x2:.1f}" cy="{y + 8}" r="4" fill="{c}"/>')
    nx = X(NOW)
    return (svg_open(W, H) +
            f'<rect width="{W}" height="{H}" rx="8" fill="{PANEL}"/>'
            f'<text x="24" y="30" font-size="13" fill="{TEXT}">Project timeline (first commit to latest)</text>'
            + axis + bars +
            f'<line x1="{nx:.1f}" y1="{top - 14}" x2="{nx:.1f}" y2="{H - 30}" stroke="{MUTED}" stroke-dasharray="3 3"/>'
            f'<text x="{nx - 4:.1f}" y="{top - 18}" font-size="10" text-anchor="end" fill="{MUTED}">today</text>'
            '</svg>')


def radar_svg(commits) -> str:
    W, H, weeks = 1000, 230, 26
    week0 = (NOW - dt.timedelta(days=NOW.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    buckets = [0] * weeks
    days = set()
    for c in commits:
        d = (week0 - c["t"].replace(hour=0, minute=0, second=0, microsecond=0)).days
        k = weeks - 1 - (d // 7 + (1 if d > 0 and d % 7 else 0)) if d > 0 else weeks - 1
        if 0 <= k < weeks:
            buckets[k] += 1
        days.add(c["t"].date())
    streak, d = 0, NOW.date()
    if d not in days:
        d -= dt.timedelta(days=1)
    while d in days:
        streak += 1
        d -= dt.timedelta(days=1)
    last30 = sum(1 for x in days if (NOW.date() - x).days < 30)
    peak = max(buckets) or 1
    L, R, top, bottom = 40, 700, 50, 190
    bw = (R - L) / weeks
    bars = ""
    for i, v in enumerate(buckets):
        h = (bottom - top) * v / peak
        x = L + i * bw + 2
        col = ACCENT
        bars += (f'<rect x="{x:.1f}" y="{bottom - h:.1f}" width="{bw - 4:.1f}" height="{h:.1f}" rx="2" fill="{col}" '
                 f'opacity="{0.45 + 0.55 * v / peak:.2f}"/>')
        if v and v == peak:
            bars += f'<text x="{x + bw / 2 - 2:.1f}" y="{bottom - h - 6:.1f}" font-size="10" text-anchor="middle" fill="{TEXT}">{v}</text>'
    top_repo = Counter(c["title"] for c in commits if (NOW - c["t"]).days < 30).most_common(1)
    kpis = [("current streak", f"{streak} day" + ("" if streak == 1 else "s")), ("active days, last 30", str(last30)),
            ("commits, 26 weeks", str(sum(buckets))), ("most active repo, 30 days", clip(top_repo[0][0], 18) if top_repo else "—")]
    kp = ""
    for i, (k, v) in enumerate(kpis):
        y = 62 + i * 38
        kp += (f'<text x="740" y="{y}" font-size="11" fill="{MUTED}">{k}</text>'
               f'<text x="740" y="{y + 20}" font-size="18" font-weight="700" fill="{TEXT}">{esc(v)}</text>')
    return (svg_open(W, H) +
            f'<rect width="{W}" height="{H}" rx="8" fill="{PANEL}"/>'
            f'<text x="24" y="30" font-size="13" fill="{TEXT}">Commits per week, last 26 weeks</text>'
            f'<line x1="{L}" y1="{bottom}" x2="{R}" y2="{bottom}" stroke="{GRID}"/>'
            f'<text x="{L}" y="{bottom + 18}" font-size="10" fill="{DIM}">-26w</text>'
            f'<text x="{R}" y="{bottom + 18}" font-size="10" text-anchor="end" fill="{DIM}">this week</text>'
            + bars + f'<line x1="720" y1="44" x2="720" y2="{bottom + 10}" stroke="{GRID}"/>' + kp + '</svg>')


def langs_svg(projects) -> str:
    agg = Counter()
    for p in projects:
        agg.update(p["langs"])
    top = agg.most_common(8)
    total = sum(v for _, v in top) or 1
    W, H = 1000, 110
    x, bar, legend = 24.0, "", ""
    for i, (lang, b) in enumerate(top):
        w = (W - 48) * b / total
        col = LANG_COLOR.get(lang, MUTED)
        bar += f'<rect x="{x:.1f}" y="44" width="{w:.1f}" height="12" fill="{col}"/>'
        x += w
        lx, ly = 24 + (i % 4) * 240, 80 + (i // 4) * 20
        legend += (f'<circle cx="{lx + 5}" cy="{ly - 4}" r="5" fill="{col}"/>'
                   f'<text x="{lx + 16}" y="{ly}" font-size="12" fill="{TEXT}">{esc(lang)} '
                   f'<tspan fill="{MUTED}">{100 * b / total:.1f}%</tspan></text>')
    return (svg_open(W, H + 10) +
            f'<rect width="{W}" height="{H + 10}" rx="8" fill="{PANEL}"/>'
            f'<text x="24" y="30" font-size="13" fill="{TEXT}">Languages across public repos</text>'
            f'<clipPath id="r"><rect x="24" y="44" width="{W - 48}" height="12" rx="6"/></clipPath>'
            f'<g clip-path="url(#r)">{bar}</g>{legend}</svg>')



HEAT = ["#1B222C", "#263A50", "#34536F", "#4A6F90", "#6E8CA8"]


def panel(W, H, title, sub=""):
    return (svg_open(W, H) + f'<rect width="{W}" height="{H}" rx="8" fill="{PANEL}"/>'
            f'<text x="24" y="30" font-size="13" fill="{TEXT}">{esc(title)}</text>'
            + (f'<text x="{W - 24}" y="30" font-size="11" text-anchor="end" fill="{MUTED}">{esc(sub)}</text>' if sub else ""))


def calendar_svg(commits) -> str:
    """GitHub-style 52-week heatmap of my commits (all public repos)."""
    today = NOW.astimezone(TZ).date()
    start = today - dt.timedelta(days=today.weekday() + 7 * 52)  # Monday, 52 weeks back
    per_day = Counter(c["t"].astimezone(TZ).date() for c in commits)
    peak = max(per_day.values() or [1])
    cell, gap, L, T = 13, 3, 56, 58
    W, H = 1000, T + 7 * (cell + gap) + 44
    out, months = [], set()
    d = start
    while d <= today:
        wk, wd = (d - start).days // 7, d.weekday()
        x, y = L + wk * (cell + gap), T + wd * (cell + gap)
        n = per_day.get(d, 0)
        lvl = 0 if n == 0 else min(4, 1 + int(3 * (n - 1) / max(peak - 1, 1)))
        out.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" fill="{HEAT[lvl]}"><title>{d:%d %b %Y}: {n} commits</title></rect>')
        if d.day <= 7 and wd == 0 and (d.year, d.month) not in months:
            months.add((d.year, d.month))
            out.append(f'<text x="{x}" y="{T - 8}" font-size="10" fill="{MUTED}">{d:%b}</text>')
        d += dt.timedelta(days=1)
    for wd, lab in ((0, "Mon"), (2, "Wed"), (4, "Fri")):
        out.append(f'<text x="{L - 8}" y="{T + wd * (cell + gap) + 10}" font-size="10" text-anchor="end" fill="{MUTED}">{lab}</text>')
    lx = W - 24 - 5 * (cell + gap) - 34
    legend = f'<text x="{lx - 6}" y="{H - 16}" font-size="10" text-anchor="end" fill="{MUTED}">less</text>'
    legend += "".join(f'<rect x="{lx + i * (cell + gap)}" y="{H - 26}" width="{cell}" height="{cell}" rx="2" fill="{c}"/>' for i, c in enumerate(HEAT))
    legend += f'<text x="{lx + 5 * (cell + gap) + 4}" y="{H - 16}" font-size="10" fill="{MUTED}">more</text>'
    days = len(per_day)
    return (panel(W, H, "Commit calendar, last 12 months", f"{len(commits)} commits on {days} days")
            + "".join(out) + legend + "</svg>")


def rhythm_svg(commits) -> str:
    """Day-of-week × hour punch card, in local time."""
    grid = Counter()
    for c in commits:
        t = c["t"].astimezone(TZ)
        grid[(t.weekday(), t.hour)] += 1
    peak = max(grid.values() or [1])
    L, T, cw, rh = 70, 60, 26.5, 26
    W, H = 1000, T + 7 * rh + 60
    out = []
    for h in range(24):
        if h % 3 == 0:
            out.append(f'<text x="{L + h * cw + cw / 2:.1f}" y="{T - 12}" font-size="10" text-anchor="middle" fill="{MUTED}">{h:02d}h</text>')
    for wd, name in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
        y = T + wd * rh + rh / 2
        out.append(f'<text x="{L - 12}" y="{y + 4:.1f}" font-size="11" text-anchor="end" fill="{MUTED}">{name}</text>')
        out.append(f'<line x1="{L}" y1="{y:.1f}" x2="{L + 24 * cw:.1f}" y2="{y:.1f}" stroke="{GRID}"/>')
        for h in range(24):
            n = grid.get((wd, h), 0)
            if n:
                r = 2.5 + 8.5 * (n / peak) ** 0.5
                out.append(f'<circle cx="{L + h * cw + cw / 2:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{ACCENT}" opacity="{0.5 + 0.5 * n / peak:.2f}"><title>{name} {h:02d}:00 · {n}</title></circle>')
    by_day = Counter(); by_hour = Counter()
    for (wd, h), n in grid.items():
        by_day[wd] += n; by_hour[h] += n
    total = sum(grid.values()) or 1
    night = sum(n for (wd, h), n in grid.items() if h >= 22 or h < 5)
    weekend = sum(n for (wd, h), n in grid.items() if wd >= 5)
    names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    facts = [("busiest day", names[by_day.most_common(1)[0][0]] if by_day else "—"),
             ("busiest hour", f"{by_hour.most_common(1)[0][0]:02d}:00" if by_hour else "—"),
             ("after 10 pm", f"{100 * night // total}%"), ("weekends", f"{100 * weekend // total}%")]
    fy = H - 24
    for i, (k, v) in enumerate(facts):
        x = L + i * 220
        out.append(f'<text x="{x}" y="{fy}" font-size="11" fill="{MUTED}">{k} <tspan fill="{TEXT}" font-weight="700">{esc(v)}</tspan></text>')
    return panel(W, H, "When I commit", f"local time · {CONFIG.get('timezone', 'UTC')}") + "".join(out) + "</svg>"


CONVENTIONAL = {"feat": "feature", "feature": "feature", "fix": "fix", "hotfix": "fix",
                "chore": "maintenance", "refactor": "maintenance", "perf": "maintenance",
                "docs": "docs", "doc": "docs", "ci": "ci / build", "build": "ci / build",
                "style": "ui / design", "ui": "ui / design", "test": "tests", "tests": "tests"}
KEYWORD_RULES = [  # checked in order against the whole message
    ("merge", r"^merge\b"),
    ("docs", r"readme|\bdocs?\b|documentation"),
    ("ci / build", r"\bci\b|workflow|deploy|release|gradle|\bsdk\b|\bndk\b|docker|cargo fmt|lint|analy[sz]e"
                   r"|environment|requirements|sitemap|config|pipeline"),
    ("fix", r"\bfix|bug|resolv|reslov|error|issue|crash"),
    ("ui / design", r"\bui\b|design|theme|style|css|layout|logo|splash|animation|dark mode|light mode"),
    ("maintenance", r"refactor|clean|remov|renam|simplif|comment out|restructur|dependenc|bump"),
    ("feature", r"\badd|implement|\bmvp\b|initial commit|\bnew\b|creat|ready|made|support|integrat|feat"),
    ("improvement", r"updat|enhanc|improv|revis|modif|upgrad|chang|final|prepar|polish"),
]


def commit_type(msg: str) -> str:
    m = msg.strip().lower()
    head = re.match(r"^(\w+)(\([^)]*\))?!?:", m)
    if head and head.group(1) in CONVENTIONAL and head.group(1) not in ("update",):
        return CONVENTIONAL[head.group(1)]
    for name, rx in KEYWORD_RULES:
        if re.search(rx, m):
            return name
    return "other"


def types_svg(commits) -> str:
    cnt = Counter(commit_type(c["msg"]) for c in commits)
    rows = cnt.most_common()
    total = sum(cnt.values()) or 1
    W, T, rh = 1000, 52, 28
    H = T + rh * max(len(rows), 1) + 24
    L, R = 150, 820
    out = []
    peak = rows[0][1] if rows else 1
    tone = {"feature": "#6F9A82", "fix": "#A86B6B", "maintenance": "#A8906A", "docs": "#7A92A8",
            "ui / design": "#8A7FA8", "ci / build": "#6E8CA8", "improvement": "#8C956A",
            "tests": "#7F9A9A", "merge": "#6E7681", "other": "#6E7681"}
    for i, (k, n) in enumerate(rows):
        y = T + i * rh
        w = (R - L) * n / peak
        out.append(f'<text x="{L - 12}" y="{y + 14}" font-size="12" text-anchor="end" fill="{TEXT}">{k}</text>'
                   f'<rect x="{L}" y="{y + 3}" width="{R - L}" height="14" rx="3" fill="{GRID}"/>'
                   f'<rect x="{L}" y="{y + 3}" width="{max(w, 2):.1f}" height="14" rx="3" fill="{tone.get(k, MUTED)}"/>'
                   f'<text x="{R + 14}" y="{y + 14}" font-size="12" fill="{MUTED}">{n} · {100 * n / total:.0f}%</text>')
    feat, fix = cnt.get("feature", 0), cnt.get("fix", 0)
    ratio = f"{feat}:{fix} feature-to-fix" if fix else f"{feat} features"
    return panel(W, H, "What kind of work (commit messages, last 12 months)", ratio) + "".join(out) + "</svg>"


def compare_svg(projects) -> str:
    rows = [p for p in projects if p["last"]][:12]
    year_days = {p["name"]: len({c["t"].astimezone(TZ).date() for c in p["mine"]}) for p in rows}
    cols = [("commits", lambda p: p["total"], lambda v: str(v)),
            ("active days (12m)", lambda p: year_days[p["name"]], lambda v: str(v)),
            ("code size", lambda p: p["size"], lambda v: f"{v / 1024:.0f} KB" if v < 1024 ** 2 else f"{v / 1024 ** 2:.1f} MB"),
            ("age", lambda p: (NOW - p["first"]).days if p["first"] else 0,
             lambda v: f"{v // 30} mo" if v >= 30 else f"{v} d")]
    W, T, rh = 1000, 74, 30
    H = T + rh * len(rows) + 20
    L, cw, mixw = 190, 150, 170
    out = []
    for j, (lab, _, _) in enumerate(cols):
        out.append(f'<text x="{L + j * cw}" y="{T - 16}" font-size="11" fill="{MUTED}">{lab}</text>')
    out.append(f'<text x="{L + 4 * cw}" y="{T - 16}" font-size="11" fill="{MUTED}">language mix</text>')
    maxes = [max((f(p) for p in rows), default=1) or 1 for _, f, _ in cols]
    for i, p in enumerate(rows):
        y = T + i * rh
        c = CAT.get(p["category"], CAT["other"])
        if i % 2 == 0:
            out.append(f'<rect x="12" y="{y - 4}" width="{W - 24}" height="{rh}" rx="4" fill="{BG}" opacity=".45"/>')
        out.append(f'<rect x="24" y="{y + 3}" width="4" height="16" rx="1" fill="{c}"/>'
                   f'<text x="36" y="{y + 15}" font-size="12" fill="{TEXT}">{esc(clip(p["title"], 20))}</text>')
        for j, (_, f, fmt) in enumerate(cols):
            v = f(p)
            bw = (cw - 64) * v / maxes[j]
            x = L + j * cw
            out.append(f'<rect x="{x}" y="{y + 5}" width="{max(bw, 1.5):.1f}" height="12" rx="2" fill="{c}"/>'
                       f'<text x="{x + max(bw, 1.5) + 6:.1f}" y="{y + 15}" font-size="11" fill="{MUTED}">{esc(fmt(v))}</text>')
        tot = sum(p["langs"].values()) or 1
        x = L + 4 * cw
        for lang, b in sorted(p["langs"].items(), key=lambda kv: -kv[1]):
            w = mixw * b / tot
            out.append(f'<rect x="{x:.1f}" y="{y + 5}" width="{w:.1f}" height="12" fill="{LANG_COLOR.get(lang, MUTED)}"><title>{esc(lang)} {100 * b / tot:.0f}%</title></rect>')
            x += w
    return panel(W, H, "Project comparison", "top 12 by latest activity") + "".join(out) + "</svg>"


def block_pie(projects) -> str:
    share = sorted(((p["title"], len(p["mine"])) for p in projects if p["mine"]), key=lambda kv: -kv[1])
    top, rest = share[:7], sum(n for _, n in share[7:])
    if rest:
        top.append(("others", rest))
    tones = ["#6E8CA8", "#6F9A82", "#A8906A", "#8A7FA8", "#A86B6B", "#7A92A8", "#8C956A", "#6E7681"]
    tv = ",".join(f'"pie{i + 1}":"{c}"' for i, c in enumerate(tones))
    lines = ["```mermaid",
             '%%{init: {"theme":"base","themeVariables":{' + tv + ',"pieStrokeColor":"#0D1117","pieStrokeWidth":"2px",'
             '"pieOuterStrokeColor":"#30363D","pieTitleTextColor":"#E6EDF3","pieSectionTextColor":"#0D1117",'
             '"pieLegendTextColor":"#E6EDF3","fontFamily":"monospace"}}}%%',
             "pie showData title Where my commits went, last 12 months"]
    lines += [f'    "{t}" : {n}' for t, n in top] or ['    "no commits yet" : 1']
    lines.append("```")
    return "\n".join(lines)


def block_compare_table(projects) -> str:
    rows = ["| Project | Commits | Active days (12m) | First commit | Latest commit | Main language | Size |",
            "|:--|--:|--:|:--|:--|:--|--:|"]
    for p in [p for p in projects if p["last"]]:
        days = len({c["t"].astimezone(TZ).date() for c in p["mine"]})
        size = p["size"]
        size_s = f"{size / 1024:.0f} KB" if size < 1024 ** 2 else f"{size / 1024 ** 2:.1f} MB"
        rows.append(f'| [{p["title"]}]({p["url"]}) | {p["total"]} | {days} | {p["first"]:%b %Y} | {p["last"]:%d %b %Y} | `{p["primary"]}` | {size_s} |')
    return "\n".join(rows)

# ── README blocks ──────────────────────────────────────────────────────────
def block_featured(projects) -> str:
    want = [n.lower() for n in CONFIG.get("featured", [])]
    feat = [p for p in projects if p["name"].lower() in want] if want else projects[:6]
    out = ['<p align="center">']
    for i, p in enumerate(feat, 1):
        out.append(f'  <a href="{p["url"]}"><img src="assets/cards/{p["name"]}.svg" width="49%" alt="{esc(p["title"])}"/></a>')
    out.append("</p>")
    return "\n".join(out)


def _repo_table(projects, offset=0) -> list[str]:
    rows = ["| # | Project | Stack | Last commit | Status |", "|:-:|:--|:--|:--|:-:|"]
    for i, p in enumerate(projects, offset + 1):
        st, _ = status_of(p["last"], p["archived"])
        live = f' · [live ↗]({p["live"]})' if p["live"] else ""
        msg = clip(p["last_msg"], 46).replace("|", "\\|") or "—"
        when = ago(p["last"]) if p["last"] else "—"
        rows.append(f'| {i:02d} | [**{p["title"]}**]({p["url"]}){live}<br><sub>{esc(clip(p["tagline"], 70))}</sub> '
                    f'| `{p["primary"]}` | [{esc(msg)}]({p["last_url"]})<br><sub>{when}</sub> | {st.lower()} |')
    return rows


def block_all(projects, visible: int = 12) -> str:
    out = _repo_table(projects[:visible])
    rest = projects[visible:]
    if rest:
        out += ["", f"<details><summary><b>+ {len(rest)} more repos</b></summary>", "",
                *_repo_table(rest, visible), "", "</details>"]
    return "\n".join(out)


def block_commits(commits, total: int = 10, per_repo: int = 3) -> str:
    """Latest commits, capped per repo so one busy project can't flood the feed."""
    picked, seen = [], Counter()
    for c in commits:
        if seen[c["repo"]] < per_repo:
            picked.append(c)
            seen[c["repo"]] += 1
        if len(picked) == total:
            break
    rows = ["| When | Repo | Commit |", "|:--|:--|:--|"]
    for c in picked:
        msg = clip(c["msg"], 70).replace("|", "\\|")
        rows.append(f'| <sub>{ago(c["t"])}</sub> | **{c["title"]}** | [`{c["sha"]}`]({c["url"]}) {esc(msg)} |')
    return "\n".join(rows)


def replace_block(text: str, name: str, body: str) -> str:
    pat = re.compile(rf"(<!-- AUTO:{name}:START -->)(.*?)(<!-- AUTO:{name}:END -->)", re.S)
    if not pat.search(text):
        print(f"warning: marker AUTO:{name} not found in README", file=sys.stderr)
        return text
    return pat.sub(lambda m: f"{m.group(1)}\n{body}\n{m.group(3)}", text)


# ── main ───────────────────────────────────────────────────────────────────
def build(projects):
    CARDS.mkdir(parents=True, exist_ok=True)
    commits = sorted((c for p in projects for c in p["mine"]), key=lambda c: c["t"], reverse=True)
    stats = {
        "repos": len(projects),
        "commits": sum(p["total"] for p in projects),
        "langs": len({l for p in projects for l in p["langs"]}),
        "active": sum(1 for p in projects if status_of(p["last"], p["archived"])[0] == "ACTIVE"),
        "year": len(commits),
        "days": len({c["t"].astimezone(TZ).date() for c in commits}),
    }
    (ASSETS / "header.svg").write_text(header_svg(projects, stats))
    (ASSETS / "timeline.svg").write_text(timeline_svg(projects))
    (ASSETS / "radar.svg").write_text(radar_svg(commits))
    (ASSETS / "stack.svg").write_text(langs_svg(projects))
    (ASSETS / "calendar.svg").write_text(calendar_svg(commits))
    (ASSETS / "rhythm.svg").write_text(rhythm_svg(commits))
    (ASSETS / "types.svg").write_text(types_svg(commits))
    (ASSETS / "compare.svg").write_text(compare_svg(projects))
    want = [n.lower() for n in CONFIG.get("featured", [])]
    feat = [p for p in projects if p["name"].lower() in want] if want else projects[:6]
    for i, p in enumerate(feat, 1):
        (CARDS / f'{p["name"]}.svg').write_text(card_svg(p, i))

    text = README.read_text()
    text = replace_block(text, "FEATURED", block_featured(projects))
    text = replace_block(text, "ALL", block_all(projects))
    text = replace_block(text, "COMMITS", block_commits(commits))
    text = replace_block(text, "PIE", block_pie(projects))
    text = replace_block(text, "COMPARE", block_compare_table(projects))
    text = replace_block(text, "UPDATED", f"<sub>Updated automatically · {NOW:%d %b %Y, %H:%M} UTC</sub>")
    README.write_text(text)
    print(f"built: {stats} · featured={[p['name'] for p in feat]}")


def main():
    gh = GitHub(os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN"))
    build(collect(gh))


if __name__ == "__main__":
    main()
