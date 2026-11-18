#!/usr/bin/env python3
"""
Render Mohammed9620's GitHub profile README cards as animated SVGs into cards/.

Follows Avi Vashishta's method:
- Standalone SVGs embedded via <img> in README.md (no JS, no external CSS).
- Inline <style> with CSS @keyframes + SMIL (<animateTransform>, <animate>).
- Fonts subsetted with pyftsubset and embedded as base64 WOFF data URIs.
- Uniform calm dark-navy design system (#0A1128, #6C8EEF, #E8ECF7), generous
  line-height, soft readable contrast, and no tiny text (< 13px).
- Staggered top-to-bottom animation delays; disabled under prefers-reduced-motion.
- STATIC=1 renders the final frame for headless Chrome layout verification.
"""
import base64
import datetime
import json
import os
import re
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data", "contributions.json")
OUT = os.path.join(ROOT, "cards")
FONTS = os.path.join(ROOT, "fonts")

# ---- uniform identity & design tokens ----------------------------------------
BG = "#0A1128"
BG_CELL = "#142042"
BORDER = "#1B2A4A"
ACCENT = "#6C8EEF"
ACCENT_SOFT = "#8FA9F3"
TEXT = "#E8ECF7"
TEXT_SOFT = "#C4CFE8"
MUTED = "#8A9BC4"

W = 880
GAP = 12
BOTTOM = 12

SERIF = "'Instrument Serif', Georgia, serif"
SANS = "Geist, system-ui, -apple-system, sans-serif"
MONO = "'Geist Mono', ui-monospace, SFMono-Regular, Menlo, monospace"

FONT_FILES = {
    "serif": ("Instrument Serif", "normal", 400, "serif-400.woff"),
    "serif-i": ("Instrument Serif", "italic", 400, "serif-italic.woff"),
    "sans": ("Geist", "normal", 400, "geist-400.woff"),
    "sans-b": ("Geist", "normal", 600, "geist-600.woff"),
    "mono": ("Geist Mono", "normal", 400, "geistmono-400.woff"),
}

BASE_CSS = """
@keyframes rise{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes grow{from{transform:scaleY(0)}to{transform:scaleY(1)}}
@keyframes pop{from{opacity:0;transform:scale(.85)}to{opacity:1;transform:none}}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}
@keyframes nudge{0%,100%{transform:none}50%{transform:translateX(3px)}}
@keyframes nudgeup{0%,100%{transform:none}50%{transform:translate(2px,-2px)}}
.r{opacity:0;animation:rise .75s cubic-bezier(.2,.7,.2,1) both;transform-box:fill-box}
.f{opacity:0;animation:fade .8s ease-out both}
.g{transform-box:fill-box;transform-origin:bottom;transform:scaleY(0);animation:grow .75s cubic-bezier(.2,.7,.2,1) both}
.p{opacity:0;transform-box:fill-box;transform-origin:center;animation:pop .35s ease-out both}
.live{animation:pulse 2.2s ease-in-out infinite}
.n{transform-box:fill-box;animation:nudge 2.2s ease-in-out infinite}
.nu{transform-box:fill-box;animation:nudgeup 2.2s ease-in-out infinite}
@keyframes sign{from{stroke-dashoffset:1000}to{stroke-dashoffset:0}}
.sig{fill:none;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:1000;stroke-dashoffset:1000;animation:sign .6s cubic-bezier(.35,0,.2,1) forwards}
@media (prefers-reduced-motion: reduce){.r,.f,.g,.p,.live,.n,.nu,.sig{animation:none!important;opacity:1!important;transform:none!important;stroke-dashoffset:0!important}}
"""


def font_face(keys):
    out = []
    for k in keys:
        fam, style, weight, fn = FONT_FILES[k]
        with open(os.path.join(FONTS, fn), "rb") as f:
            b64 = base64.b64encode(f.read()).decode("ascii")
        out.append(
            f"@font-face{{font-family:'{fam}';font-style:{style};font-weight:{weight};"
            f"src:url(data:font/woff;base64,{b64}) format('woff')}}"
        )
    return "".join(out)


def svg(w, h, body, fonts, label, extra_css="", left=0, right=0, bottom=BOTTOM):
    """Wrap card markup inside an optionally padded SVG canvas."""
    if left:
        body = f'<g transform="translate({left:.3f} 0)">{body}</g>'
    w, h = w + left + right, h + bottom
    css = font_face(fonts) + BASE_CSS + extra_css
    if os.environ.get("STATIC"):
        css += (
            ".r,.f,.g,.p,.live,.n,.nu,.sig{animation:none!important;"
            "opacity:1!important;transform:none!important;stroke-dashoffset:0!important}"
        )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.3f}" height="{h}" '
        f'viewBox="0 0 {w:.3f} {h}" role="img" aria-label="{escape(label)}">'
        f"<title>{escape(label)}</title><style>{css}</style>{body}</svg>"
    )


def write(name, content):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"wrote cards/{name} ({len(content) // 1024} KB)")


def d(s):
    return f'style="animation-delay:{s:.2f}s"'


def wrap(text, n):
    lines, line = [], ""
    for word in text.split():
        if line and len(line) + 1 + len(word) > n:
            lines.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    return lines + [line] if line else lines


def text_lines(x, y, lines, lh, attrs):
    return "".join(
        f'<text x="{x}" y="{y + i * lh}" {attrs}>{escape(l)}</text>'
        for i, l in enumerate(lines)
    )


# ---- 1 · hero -----------------------------------------------------------------
def hero():
    h = 252
    sig_strokes = [
        # M
        (
            "M 48,133 C 56,112 64,88 72,73 C 74,69 76,72 76,78 C 78,94 80,109 84,119 "
            "C 92,102 101,85 110,73 C 113,69 115,72 115,79 C 115,101 116,121 120,134 "
            "C 123,138 129,132 135,124",
            TEXT,
            3.5,
            1.0,
            0.15,
            0.60,
        ),
        # oh
        (
            "M 135,124 C 141,114 147,108 153,109 C 145,106 135,113 135,125 "
            "C 135,134 143,137 151,134 C 159,130 161,117 156,110 C 163,106 177,85 184,71 "
            "C 186,67 181,67 178,73 C 174,85 172,113 171,135 C 173,121 180,108 189,108 "
            "C 196,108 198,116 197,128 C 197,135 203,134 209,126",
            TEXT,
            3.2,
            1.0,
            0.72,
            0.48,
        ),
        # amm
        (
            "M 209,126 C 216,113 224,108 231,109 C 222,107 212,115 212,126 "
            "C 212,135 220,137 227,132 C 232,128 235,117 235,109 C 234,120 233,130 236,134 "
            "C 239,136 244,129 248,120 C 249,113 249,108 249,108 C 248,119 248,130 248,135 "
            "C 250,121 257,108 264,108 C 269,108 270,117 269,135 "
            "C 271,121 278,108 285,108 C 290,108 291,118 290,132 C 291,136 296,131 300,121 "
            "C 301,113 301,108 301,108 C 300,119 300,130 300,135 "
            "C 302,121 309,108 316,108 C 321,108 322,117 321,135 "
            "C 323,121 330,108 337,108 C 342,108 343,118 342,131 C 343,136 348,132 353,125",
            TEXT,
            3.2,
            1.0,
            1.16,
            0.68,
        ),
        # ed
        (
            "M 353,125 C 362,122 368,116 367,110 C 366,106 358,107 355,115 "
            "C 352,124 355,134 363,135 C 370,135 376,129 382,121 "
            "C 387,114 393,108 398,109 C 390,107 381,115 381,126 "
            "C 381,134 388,136 394,132 C 400,127 404,106 408,72 "
            "C 406,96 403,120 404,132 C 405,137 414,133 423,125",
            TEXT,
            3.2,
            1.0,
            1.80,
            0.50,
        ),
        # subtle signature underline
        (
            "M 48,150 C 148,145 278,144 416,149",
            ACCENT,
            2.2,
            0.85,
            2.26,
            0.38,
        ),
    ]
    sig_paths = "".join(
        f'<path class="sig" pathLength="1000" d="{path}" stroke="{color}" '
        f'stroke-width="{sw}" stroke-opacity="{op}" '
        f'style="animation-delay:{delay:.2f}s;animation-duration:{dur:.2f}s"/>'
        for path, color, sw, op, delay, dur in sig_strokes
    )

    body = f"""
<rect x=".5" y=".5" width="{W - 1}" height="{h - 1}" rx="14" fill="{BG}" stroke="{BORDER}" stroke-width="1"/>
<g class="f" {d(0.0)}>
  <rect class="live" x="44" y="40" width="8" height="8" rx="2" fill="{ACCENT}"/>
  <text x="62" y="48" font-family="{MONO}" font-size="13" letter-spacing="1.2" fill="{MUTED}">SOFTWARE ENGINEER &#183; BACKEND &amp; CLOUD</text>
</g>
<g aria-label="Mohammed">
  {sig_paths}
</g>
<g class="r" {d(0.32)}>
  <text x="44" y="182" font-family="{SANS}" font-size="19" fill="{TEXT_SOFT}">Software Engineer &#8212; building backend systems &amp; cloud infrastructure</text>
</g>
<rect class="f" {d(0.45)} x="44" y="204" width="792" height="1" fill="{BORDER}"/>
<g class="f" {d(0.52)}>
  <text x="44" y="228" font-family="{MONO}" font-size="13" letter-spacing="0.6" fill="{MUTED}">Python  &#183;  .NET / C#  &#183;  Azure  &#183;  Docker  &#183;  Bicep</text>
</g>
"""
    write(
        "hero.svg",
        svg(
            W,
            h,
            body,
            ["sans", "mono"],
            "Mohammed — Software Engineer — building backend systems & cloud infrastructure",
        ),
    )


# ---- 2 · three linked tiles ---------------------------------------------------
TILE_W, TILE_H = 880 / 3 - 8, 200  # 285.333 each; 3 across with 12px gaps


def tile(name, label, heading, lines, delay, pos):
    is_static = bool(os.environ.get("STATIC"))
    accent_anim = (
        ""
        if is_static
        else '<animate attributeName="opacity" values="0.65;1;0.65" dur="4s" repeatCount="indefinite"/>'
    )
    clip_id = f"card-{name}"
    body = f"""
<defs>
  <clipPath id="{clip_id}"><rect width="{TILE_W:.3f}" height="{TILE_H}" rx="14"/></clipPath>
</defs>
<g class="r" {d(delay)}>
  <g clip-path="url(#{clip_id})">
    <rect width="{TILE_W:.3f}" height="{TILE_H}" fill="{BG}"/>
    <rect x="0" y="0" width="{TILE_W:.3f}" height="2" fill="{ACCENT}">{accent_anim}</rect>
  </g>
  <rect x=".5" y=".5" width="{TILE_W - 1:.3f}" height="{TILE_H - 1}" rx="14" fill="none" stroke="{BORDER}" stroke-width="1"/>
  <text class="f" {d(delay + 0.12)} x="26" y="40" font-family="{MONO}" font-size="13" letter-spacing="1.4" fill="{ACCENT}">{escape(label)}</text>
  <text class="n" style="animation-delay:{delay + 0.6:.2f}s" x="{TILE_W - 38:.1f}" y="40" font-family="{MONO}" font-size="14" fill="{ACCENT}">&#8594;</text>
  <text class="r" {d(delay + 0.20)} x="26" y="86" font-family="{SERIF}" font-size="24" fill="{TEXT}">{escape(heading)}</text>
  <g class="r" {d(delay + 0.28)}>
    {text_lines(26, 126, lines, 25, f'font-family="{SANS}" font-size="15" fill="{TEXT_SOFT}"')}
  </g>
</g>
"""
    blurb = " ".join(lines)
    write(
        f"{name}.svg",
        svg(
            TILE_W,
            TILE_H,
            body,
            ["serif", "sans", "mono"],
            f"{label}: {heading}. {blurb}",
            left=4 * pos,
            right=8 - 4 * pos,
        ),
    )


# ---- 3 · contribution graph in blue (#6C8EEF) ---------------------------------
BLUE = [BG_CELL, "#21356B", "#355199", "#4F6EC6", ACCENT, ACCENT_SOFT]


def level_for(c):
    if c == 0:
        return 0
    if c <= 2:
        return 1
    if c <= 5:
        return 2
    if c <= 9:
        return 3
    if c <= 13:
        return 4
    return 5


def heatmap(data):
    days = data["days"]
    first = datetime.date.fromisoformat(days[0]["date"])
    lead = (first.weekday() + 1) % 7  # Sunday = 0
    cell, step, gx, gy = 12, 15, 44, 92
    cells, months, seen = [], [], set()
    for i, day in enumerate(days):
        k = i + lead
        col, row = divmod(k, 7)
        dt = datetime.date.fromisoformat(day["date"])
        if dt.day <= 7 and (dt.year, dt.month) not in seen and row == 0:
            seen.add((dt.year, dt.month))
            months.append((col, dt.strftime("%b")))
        c = day["count"]
        delay = 1.4 + col * 0.018 + row * 0.012
        cells.append(
            f'<rect class="p" style="animation-delay:{delay:.2f}s" x="{gx + col * step}" y="{gy + row * step}" '
            f'width="{cell}" height="{cell}" rx="3" fill="{BLUE[level_for(c)]}">'
            f'<title>{day["date"]}: {c} contribution{"s" if c != 1 else ""}</title></rect>'
        )
    ncols = (len(days) + lead + 6) // 7
    right = gx + ncols * step - 3
    legend_x = right - len(BLUE) * 14 - 46
    labels = "".join(
        f'<text x="{gx + col * step}" y="{gy + 7 * step + 22}" font-family="{MONO}" font-size="13" fill="{MUTED}">{m}</text>'
        for col, m in months
        if gx + col * step + 30 < legend_x - 46
    )
    legend = "".join(
        f'<rect x="{legend_x + i * 14}" y="{gy + 7 * step + 12}" width="11" height="11" rx="2.5" fill="{c}"/>'
        for i, c in enumerate(BLUE)
    )
    h = gy + 7 * step + 48
    body = f"""
<rect x=".5" y=".5" width="{W - 1}" height="{h - 1}" rx="14" fill="{BG}" stroke="{BORDER}" stroke-width="1"/>
<text class="r" {d(1.3)} x="44" y="58" font-family="{SERIF}" font-size="36" fill="{TEXT}">Every day, <tspan font-style="italic" fill="{ACCENT}">in blue</tspan></text>
<text class="f" {d(1.35)} x="{right}" y="56" text-anchor="end" font-family="{MONO}" font-size="13" letter-spacing="1" fill="{MUTED}">REFRESHED DAILY</text>
{''.join(cells)}
<g class="f" {d(2.35)}>
  {labels}
  <text x="{legend_x - 10}" y="{gy + 7 * step + 22}" text-anchor="end" font-family="{MONO}" font-size="13" fill="{MUTED}">less</text>
  {legend}
  <text x="{legend_x + len(BLUE) * 14 + 6}" y="{gy + 7 * step + 22}" font-family="{MONO}" font-size="13" fill="{MUTED}">more</text>
</g>
"""
    write(
        "heatmap.svg",
        svg(
            W,
            h,
            body,
            ["serif", "serif-i", "mono"],
            f'Contribution graph in blue: {data["total_contributions"]:,} contributions in the last year',
        ),
    )


# ---- 4 · monthly contributions bar chart (no streak) -------------------------
def activity(data):
    h = 330
    monthly = data["monthly"][-12:]
    best = max(monthly[:-1] or monthly, key=lambda m: m["total"])
    top = max(1, best["total"])
    x0, x1, base, maxh, gap = 44, 584, 280, 132, 10
    bw = (x1 - x0 - gap * (len(monthly) - 1)) / len(monthly)
    bars = []
    for i, m in enumerate(monthly):
        partial = i == len(monthly) - 1
        is_best = m is best and m["total"] > 0
        bh = max(4, round(m["total"] / top * maxh))
        x = x0 + i * (bw + gap)
        if is_best:
            fill = ACCENT
        elif m["total"] == 0:
            fill = "#17254C"
        elif partial:
            fill = "#2A4380"
        else:
            fill = "#355199"
        label = datetime.date.fromisoformat(m["month"] + "-01").strftime("%b")
        bars.append(
            f'<rect class="g" style="animation-delay:{2.5 + i * 0.05:.2f}s" x="{x:.1f}" y="{base - bh}" '
            f'width="{bw:.1f}" height="{bh}" rx="4" fill="{fill}"><title>{label}: {m["total"]:,}</title></rect>'
            f'<text class="f" style="animation-delay:{2.5 + i * 0.05:.2f}s" x="{x + bw / 2:.1f}" y="{base + 24}" '
            f'text-anchor="middle" font-family="{MONO}" font-size="13" fill="{MUTED}">{label}</text>'
        )
        if is_best:
            bars.append(
                f'<text class="p" style="animation-delay:3.15s" x="{x + bw / 2:.1f}" y="{base - bh - 10}" '
                f'text-anchor="middle" font-family="{MONO}" font-size="13" fill="{ACCENT_SOFT}">{m["total"]:,}</text>'
            )

    total_days = len(data["days"])
    best_date_raw = data["best_day"]["date"]
    best_date_str = (
        datetime.date.fromisoformat(best_date_raw).strftime("%b %d").replace(" 0", " ")
        if best_date_raw
        else "n/a"
    )
    stats = [
        (f'{data["active_days"]}<tspan fill="{MUTED}"> / {total_days}</tspan>', "active days in the last year"),
        (f'{data["best_day"]["count"]} <tspan font-style="italic" fill="{ACCENT}">commits</tspan>', f"busiest day ({best_date_str})"),
    ]
    side = []
    for i, (big, small) in enumerate(stats):
        y = 152 + i * 104
        side.append(
            f'<g class="r" {d(2.8 + i * 0.16)}>'
            f'<text x="632" y="{y}" font-family="{SERIF}" font-size="42" fill="{TEXT}">{big}</text>'
            f'<text x="632" y="{y + 28}" font-family="{SANS}" font-size="15" fill="{TEXT_SOFT}">{escape(small)}</text></g>'
        )
        if i == 0:
            side.append(
                f'<rect class="f" {d(2.8)} x="632" y="206" width="204" height="1" fill="{BORDER}"/>'
            )

    body = f"""
<rect x=".5" y=".5" width="{W - 1}" height="{h - 1}" rx="14" fill="{BG}" stroke="{BORDER}" stroke-width="1"/>
<text class="f" {d(2.4)} x="44" y="50" font-family="{MONO}" font-size="13" letter-spacing="1.2" fill="{MUTED}">THE LAST 12 MONTHS ON GITHUB</text>
<text class="r" {d(2.45)} x="44" y="102" font-family="{SERIF}" font-size="46" fill="{TEXT}">{data["total_contributions"]:,} <tspan font-style="italic" fill="{ACCENT}">contributions</tspan></text>
{''.join(bars)}
{''.join(side)}
"""
    write(
        "activity.svg",
        svg(
            W,
            h,
            body,
            ["serif", "serif-i", "sans", "mono"],
            f'{data["total_contributions"]:,} contributions in the last year, {data["active_days"]} active days, {data["best_day"]["count"]} on the busiest day',
        ),
    )


# ---- 5 · featured repository cards --------------------------------------------
REPO_W, REPO_H = 880 / 3 - 8, 200
REPOS = [
    (
        "repo-aspnet-guide",
        "-Zero-to-live-aspnet-guide",
        "Zero-to-Live ASP.NET",
        "Interactive 13-chapter ASP.NET Core guide from server basics to production.",
        "ASP.NET CORE",
        "GUIDE",
    ),
    (
        "repo-qa-playwright",
        "QA-Playwright-Project-Original",
        "QA Playwright Engine",
        "Automated QA testing engine with Playwright, Flask UI, OTP auth & reports.",
        "PYTHON",
        "PLAYWRIGHT",
    ),
    (
        "repo-system-health",
        "System-Health-Monitor",
        "System Health Monitor",
        "Real-time CPU & RAM monitor with incident logging and SMTP email alerts.",
        "PYTHON",
        "MONITORING",
    ),
]


def repo_stars():
    stars = {}
    try:
        import requests

        for _, repo_name, *_ in REPOS:
            r = requests.get(f"https://api.github.com/repos/Mohammed9620/{repo_name}", timeout=10)
            if r.ok:
                stars[repo_name] = r.json().get("stargazers_count", 0)
    except Exception as e:
        print(f"stars unavailable: {e}")
    return stars


def repo_card(i, card_slug, repo_name, title, desc, lang, tag, stars):
    delay = 3.3 + i * 0.14
    meta = f"{lang}  \u00b7  \u2605 {stars}" if stars else f"{lang}  \u00b7  {tag}"
    body = f"""
<rect x=".5" y=".5" width="{REPO_W - 1:.3f}" height="{REPO_H - 1}" rx="14" fill="{BG}" stroke="{BORDER}" stroke-width="1"/>
<g class="r" {d(delay)}>
  <rect x="26" y="31" width="8" height="8" rx="2" fill="{ACCENT}"/>
  <text x="42" y="40" font-family="{MONO}" font-size="13" letter-spacing="0.8" fill="{MUTED}">{escape(meta)}</text>
  <text class="nu" x="{REPO_W - 38:.1f}" y="40" font-family="{MONO}" font-size="14" fill="{ACCENT}">&#8599;</text>
  <text x="26" y="82" font-family="{SERIF}" font-size="26" fill="{TEXT}">{escape(title)}</text>
  {text_lines(26, 118, wrap(desc, 29), 25, f'font-family="{SANS}" font-size="15" fill="{TEXT_SOFT}"')}
</g>
"""
    write(
        f"{card_slug}.svg",
        svg(
            REPO_W,
            REPO_H,
            body,
            ["serif", "sans", "mono"],
            f"{title} ({repo_name}): {desc}",
            left=4 * i,
            right=8 - 4 * i,
        ),
    )


# ---- 6 · about me -------------------------------------------------------------
ABOUT_LEFT = [
    ("I'm currently working on:", "Building backend and cloud infrastructure"),
    ("I'm looking to collaborate on:", "Backend development and cloud architecture projects"),
    ("I'm looking for help with:", "Cloud native patterns and best practices"),
]
ABOUT_RIGHT = [
    ("I'm currently learning:", "Docker and cloud services"),
    ("Ask me about:", "Python, .NET, and C# development"),
    ("Fun fact:", "I turn coffee and code into reliable cloud systems"),
]


def about():
    h = 304
    items = []
    for col_x, rows, base_delay in ((36, ABOUT_LEFT, 3.75), (468, ABOUT_RIGHT, 3.90)):
        for i, (heading, body_text) in enumerate(rows):
            y = 52 + i * 88
            delay = base_delay + i * 0.10
            items.append(
                f'<g class="r" {d(delay)}>'
                f'<rect x="{col_x}" y="{y - 12}" width="8" height="8" rx="2" fill="{ACCENT}"/>'
                f'<text x="{col_x + 18}" y="{y}" font-family="{SERIF}" font-size="23" fill="{TEXT}">{escape(heading)}</text>'
                f'<text x="{col_x}" y="{y + 28}" font-family="{SANS}" font-size="15" fill="{TEXT_SOFT}">{escape(body_text)}</text>'
                f"</g>"
            )
            if i < 2:
                items.append(
                    f'<rect class="f" {d(delay)} x="{col_x}" y="{y + 50}" width="376" height="1" fill="{BORDER}"/>'
                )

    body = f"""
<rect x=".5" y=".5" width="{W - 1}" height="{h - 1}" rx="14" fill="{BG}" stroke="{BORDER}" stroke-width="1"/>
<rect class="f" {d(3.75)} x="440" y="28" width="1" height="248" fill="{BORDER}"/>
{''.join(items)}
"""
    write(
        "about.svg",
        svg(
            W,
            h,
            body,
            ["serif", "sans"],
            "About Me — building backend and cloud infrastructure; learning Docker and cloud services; ask me about Python, .NET, and C#",
        ),
    )


# ---- 7 · tech stack -----------------------------------------------------------
STACK_ROWS = [
    ["Python", "C++", "Flask", "FastAPI"],
    ["Azure", "Bicep", "Docker", "PostgreSQL", "MySQL"],
    ["Git", "GitHub Actions", "Postman", "Figma"],
]


def tech_stack():
    h = 212
    x0, inner_w, gap, bh = 32, 816, 12, 46
    pills = []
    idx = 0
    for r_idx, row in enumerate(STACK_ROWS):
        ry = 26 + r_idx * 57
        n = len(row)
        bw = (inner_w - (n - 1) * gap) / n
        for c_idx, tool in enumerate(row):
            bx = x0 + c_idx * (bw + gap)
            delay = 4.15 + idx * 0.04
            pills.append(
                f'<g class="r" {d(delay)}>'
                f'<rect x="{bx:.1f}" y="{ry}" width="{bw:.1f}" height="{bh}" rx="10" fill="#0F1A3A" stroke="{BORDER}" stroke-width="1"/>'
                f'<rect x="{bx + 18:.1f}" y="{ry + 19}" width="8" height="8" rx="2" fill="{ACCENT}"/>'
                f'<text x="{bx + 36:.1f}" y="{ry + 28}" font-family="{SANS}" font-weight="600" font-size="15" fill="{TEXT}">{escape(tool)}</text>'
                f"</g>"
            )
            idx += 1

    body = f"""
<rect x=".5" y=".5" width="{W - 1}" height="{h - 1}" rx="14" fill="{BG}" stroke="{BORDER}" stroke-width="1"/>
{''.join(pills)}
"""
    write(
        "tech-stack.svg",
        svg(
            W,
            h,
            body,
            ["sans", "sans-b"],
            "Tech Stack — Python, C++, Flask, FastAPI, Azure, Bicep, Docker, PostgreSQL, MySQL, Git, GitHub Actions, Postman, Figma",
        ),
    )


if __name__ == "__main__":
    with open(DATA, encoding="utf-8") as f:
        data = json.load(f)
    hero()
    tile(
        "build",
        "BUILD",
        "Backend APIs & Services",
        ["Designing reliable REST APIs,", "backend services & data layers."],
        0.75,
        0,
    )
    tile(
        "learn",
        "LEARN",
        "Docker, Python, .NET / C#",
        ["Containerized workflows, clean", "architecture & backend tooling."],
        0.92,
        1,
    )
    tile(
        "cloud",
        "CLOUD",
        "Azure, Bicep, Infrastructure",
        ["Declarative cloud infrastructure,", "deployments & CI/CD delivery."],
        1.09,
        2,
    )
    heatmap(data)
    activity(data)
    stars = repo_stars()
    for i, (slug, repo_name, title, desc, lang, tag) in enumerate(REPOS):
        repo_card(i, slug, repo_name, title, desc, lang, tag, stars.get(repo_name, 0))
    about()
    tech_stack()
