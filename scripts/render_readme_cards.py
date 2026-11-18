#!/usr/bin/env python3
"""
Render Mohammed9620's GitHub profile README cards as animated SVGs into cards/.

Follows Avi Vashishta's method:
- Standalone SVGs embedded via <img> in README.md (no JS, no external CSS).
- Inline <style> with CSS @keyframes + SMIL (<animateTransform>, <set>).
- Fonts subsetted with pyftsubset and embedded as base64 WOFF data URIs.
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

# ---- identity & design tokens ------------------------------------------------
BG = "#0A1128"
BG_ELEVATED = "#101B3B"
BG_CELL = "#152246"
BORDER = "#1E2F5D"
ACCENT = "#6C8EEF"
ACCENT_BRIGHT = "#9BB3F7"
TEXT = "#E8ECF7"
TEXT_SOFT = "#B8C4E0"
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
@keyframes rise{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes grow{from{transform:scaleY(0)}to{transform:scaleY(1)}}
@keyframes pop{0%{opacity:0;transform:scale(.3)}70%{opacity:1;transform:scale(1.15)}100%{opacity:1;transform:none}}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.25}}
@keyframes nudge{0%,100%{transform:none}50%{transform:translateX(4px)}}
@keyframes nudgeup{0%,100%{transform:none}50%{transform:translate(3px,-3px)}}
.r{opacity:0;animation:rise .8s cubic-bezier(.2,.7,.2,1) both;transform-box:fill-box}
.f{opacity:0;animation:fade .9s ease-out both}
.g{transform-box:fill-box;transform-origin:bottom;transform:scaleY(0);animation:grow .8s cubic-bezier(.2,.7,.2,1) both}
.p{opacity:0;transform-box:fill-box;transform-origin:center;animation:pop .4s ease-out both}
.live{animation:pulse 1.6s ease-in-out infinite}
.n{transform-box:fill-box;animation:nudge 1.8s ease-in-out infinite}
.nu{transform-box:fill-box;animation:nudgeup 1.8s ease-in-out infinite}
@keyframes tilein{0%{opacity:0;transform:translateY(90px) scale(.6) rotate(-9deg)}55%{opacity:1;transform:translateY(-10px) scale(1.05) rotate(2deg)}75%{transform:translateY(3px) scale(.98) rotate(-.8deg)}90%{transform:translateY(-1px) scale(1.01) rotate(.2deg)}100%{opacity:1;transform:none}}
@keyframes slidein{from{opacity:0;transform:translateX(-26px)}to{opacity:1;transform:none}}
@keyframes arrowin{0%{opacity:0;transform:translateX(-30px)}60%{opacity:1;transform:translateX(6px)}100%{opacity:1;transform:none}}
@keyframes roll{from{transform:translateY(60px)}to{transform:none}}
@keyframes sheen{0%{transform:translateX(-260px) skewX(-20deg)}22%,100%{transform:translateX(420px) skewX(-20deg)}}
@keyframes ring{0%{opacity:.7;transform:scale(.2)}100%{opacity:0;transform:scale(2.4)}}
.ti{opacity:0;transform-box:fill-box;transform-origin:50% 60%;animation:tilein 1.1s cubic-bezier(.2,.8,.2,1) both}
.sl{opacity:0;transform-box:fill-box;animation:slidein .6s cubic-bezier(.2,.7,.2,1) both}
.ai{opacity:0;transform-box:fill-box;animation:arrowin .7s cubic-bezier(.2,.7,.2,1) both}
.ro{transform-box:fill-box;animation:roll .8s cubic-bezier(.15,.8,.2,1) both}
.sh{animation:sheen 5s ease-in-out infinite}
.rg{opacity:0;transform-box:fill-box;transform-origin:center;animation:ring 1s ease-out both}
@media (prefers-reduced-motion: reduce){.r,.f,.g,.p,.live,.n,.nu,.ti,.sl,.ai,.ro,.rg{animation:none!important;opacity:1!important;transform:none!important}.sh,.rg{display:none}}
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
            ".r,.f,.g,.p,.live,.n,.nu,.ti,.sl,.ai,.ro{animation:none!important;"
            "opacity:1!important;transform:none!important}.sh,.rg{display:none}"
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
    h = 260
    is_static = bool(os.environ.get("STATIC"))

    # Upper-right architectural grid motif (kept cleanly within x=640..836, y=30..146)
    motif_cells = []
    gx0, gy0 = 644, 34
    for row in range(5):
        for col in range(8):
            cx = gx0 + col * 24
            cy = gy0 + row * 22
            # Subtle diagonal / wave accent pattern in navy & blue
            is_accent = (row + col) % 4 == 0 or (row == 2 and col in (3, 4, 5))
            fill = ACCENT if is_accent else BG_CELL
            opacity = "0.85" if (row == 2 and col in (3, 4, 5)) else ("0.45" if is_accent else "0.75")
            delay = 0.25 + col * 0.04 + row * 0.03
            motif_cells.append(
                f'<rect class="p" style="animation-delay:{delay:.2f}s" x="{cx}" y="{cy}" '
                f'width="16" height="16" rx="4" fill="{fill}" fill-opacity="{opacity}"/>'
            )

    shine_anim = ""
    if not is_static:
        shine_anim = (
            '<animateTransform attributeName="gradientTransform" type="translate" '
            'values="-500 0;500 0;500 0" keyTimes="0;.45;1" dur="7s" begin="1.4s" '
            'repeatCount="indefinite"/>'
        )
    grad_x1, grad_x2 = ("-100", "460") if is_static else ("0", "500")

    body = f"""
<defs>
  <linearGradient id="shine" gradientUnits="userSpaceOnUse" x1="{grad_x1}" y1="0" x2="{grad_x2}" y2="0">
    <stop offset="0" stop-color="{TEXT}"/>
    <stop offset=".42" stop-color="{TEXT}"/>
    <stop offset=".5" stop-color="{ACCENT}"/>
    <stop offset=".58" stop-color="{TEXT}"/>
    <stop offset="1" stop-color="{TEXT}"/>
    {shine_anim}
  </linearGradient>
</defs>
<rect x=".5" y=".5" width="{W - 1}" height="{h - 1}" rx="14" fill="{BG}" stroke="{BORDER}" stroke-width="1"/>
<g class="f" {d(0.0)}>
  <rect class="live" x="44" y="42" width="8" height="8" rx="2" fill="{ACCENT}"/>
  <text x="62" y="50" font-family="{MONO}" font-size="12" letter-spacing="1.2" fill="{MUTED}">SOFTWARE ENGINEER · BACKEND &amp; CLOUD</text>
</g>
<text class="r" {d(0.15)} x="42" y="142" font-family="{SERIF}" font-size="92" letter-spacing="-1.5" fill="url(#shine)">Mohammed</text>
<g class="r" {d(0.35)}>
  <text x="44" y="186" font-family="{SANS}" font-size="18" fill="{TEXT_SOFT}">Software Engineer &#8212; building backend systems &amp; cloud infrastructure</text>
</g>
<g class="f" {d(0.55)}>
  <text x="44" y="226" font-family="{MONO}" font-size="12" letter-spacing="0.8" fill="{MUTED}">PYTHON  &#183;  .NET / C#  &#183;  AZURE  &#183;  DOCKER  &#183;  BICEP</text>
  <text class="nu" x="412" y="226" font-family="{MONO}" font-size="13" fill="{ACCENT}">&#8599;</text>
</g>
<g>{''.join(motif_cells)}</g>
"""
    write(
        "hero.svg",
        svg(
            W,
            h,
            body,
            ["serif", "sans", "mono"],
            "Mohammed — Software Engineer — building backend systems & cloud infrastructure",
        ),
    )


# ---- 2 · three linked tiles ---------------------------------------------------
TILE_W, TILE_H = 880 / 3 - 8, 210  # 285.333 each; 3 across with 12px gaps


def count_up(num, word, x, y, attrs, begin, dur=1.1, frames=18):
    """Count up from 0 using SMIL <set> frames inside <img>; static shows final frame."""
    m = re.match(r"([\d.]+)(.*)", num)
    val, suf = float(m.group(1)), m.group(2)
    dec = len(m.group(1).split(".")[1]) if "." in m.group(1) else 0
    tail = f' <tspan font-style="italic">{escape(word)}</tspan>'
    if os.environ.get("STATIC"):
        return f'<text x="{x}" y="{y}" {attrs}>{escape(num)}{tail}</text>'
    out = []
    for i in range(frames + 1):
        e = 1 - (1 - i / frames) ** 3
        txt = num if i == frames else f"{val * e:.{dec}f}{suf}"
        on = begin + dur * i / frames
        off = "" if i == frames else f'<set attributeName="opacity" to="0" begin="{begin + dur * (i + 1) / frames:.3f}s"/>'
        out.append(
            f'<text x="{x}" y="{y}" {attrs} opacity="0">{escape(txt)}{tail}'
            f'<set attributeName="opacity" to="1" begin="{on:.3f}s"/>{off}</text>'
        )
    return "".join(out)


def tile(name, label, fill, border, accent, num, word, blurb, delay, pos):
    lines = wrap(blurb, 34)
    blurb_svg = "".join(
        f'<text class="r" {d(delay + 0.75 + i * 0.1)} x="22" y="{148 + i * 21}" font-family="{SANS}" '
        f'font-size="14" fill="{TEXT_SOFT}">{escape(l)}</text>'
        for i, l in enumerate(lines)
    )
    clip_id = f"card-{name}"
    slot_id = f"slot-{name}"
    gl_id = f"gl-{name}"
    body = f"""
<defs>
  <clipPath id="{clip_id}"><rect width="{TILE_W:.3f}" height="{TILE_H}" rx="14"/></clipPath>
  <clipPath id="{slot_id}"><rect x="0" y="56" width="{TILE_W:.3f}" height="64"/></clipPath>
  <linearGradient id="{gl_id}" x1="0" x2="1">
    <stop offset="0" stop-color="{ACCENT_BRIGHT}" stop-opacity="0"/>
    <stop offset=".5" stop-color="{ACCENT_BRIGHT}" stop-opacity=".22"/>
    <stop offset="1" stop-color="{ACCENT_BRIGHT}" stop-opacity="0"/>
  </linearGradient>
</defs>
<g class="ti" {d(delay)}>
  <g clip-path="url(#{clip_id})">
    <rect width="{TILE_W:.3f}" height="{TILE_H}" fill="{fill}"/>
    <rect x="0" y="0" width="{TILE_W:.3f}" height="3" fill="{accent}"/>
    <circle class="rg" {d(delay + 0.5)} cx="{TILE_W - 40:.1f}" cy="{TILE_H - 40}" r="58" fill="none" stroke="{accent}" stroke-opacity=".45" stroke-width="2"/>
    <rect class="sh" style="animation-delay:{delay + 1.4:.2f}s" x="0" y="-20" width="90" height="{TILE_H + 40}" fill="url(#{gl_id})" transform="translate(-260 0)"/>
  </g>
  <rect x=".5" y=".5" width="{TILE_W - 1:.3f}" height="{TILE_H - 1}" rx="14" fill="none" stroke="{border}" stroke-width="1"/>
  <text class="sl" {d(delay + 0.35)} x="22" y="38" font-family="{MONO}" font-size="12" letter-spacing="1.4" fill="{accent}">{escape(label)}</text>
  <g class="ai" {d(delay + 0.5)}><text class="n" style="animation-delay:{delay + 1.3:.2f}s" x="{TILE_W - 34:.1f}" y="38" font-family="{MONO}" font-size="14" fill="{accent}">&#8594;</text></g>
  <g clip-path="url(#{slot_id})"><g class="ro" {d(delay + 0.45)}>
    {count_up(num, word, 22, 108, f'font-family="{SERIF}" font-size="40" fill="{TEXT}"', delay + 0.45)}
  </g></g>
  {blurb_svg}
</g>
"""
    write(
        f"{name}.svg",
        svg(
            TILE_W,
            TILE_H,
            body,
            ["serif", "serif-i", "sans", "mono"],
            f"{label}: {num} {word}. {blurb}",
            left=4 * pos,
            right=8 - 4 * pos,
        ),
    )


# ---- 3 · contribution graph in blue (#6C8EEF) ---------------------------------
BLUE = [BG_CELL, "#21356B", "#355199", "#4F6EC6", ACCENT, ACCENT_BRIGHT]


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
    cell, step, gx, gy = 12, 15, 44, 96
    cells, months, seen = [], [], set()
    for i, day in enumerate(days):
        k = i + lead
        col, row = divmod(k, 7)
        dt = datetime.date.fromisoformat(day["date"])
        if dt.day <= 7 and (dt.year, dt.month) not in seen and row == 0:
            seen.add((dt.year, dt.month))
            months.append((col, dt.strftime("%b")))
        c = day["count"]
        delay = 1.6 + col * 0.02 + row * 0.015
        cells.append(
            f'<rect class="p" style="animation-delay:{delay:.2f}s" x="{gx + col * step}" y="{gy + row * step}" '
            f'width="{cell}" height="{cell}" rx="3" fill="{BLUE[level_for(c)]}">'
            f'<title>{day["date"]}: {c} contribution{"s" if c != 1 else ""}</title></rect>'
        )
    ncols = (len(days) + lead + 6) // 7
    right = gx + ncols * step - 3
    legend_x = right - len(BLUE) * 14 - 38
    labels = "".join(
        f'<text x="{gx + col * step}" y="{gy + 7 * step + 18}" font-family="{MONO}" font-size="11" fill="{MUTED}">{m}</text>'
        for col, m in months
        if gx + col * step + 26 < legend_x - 42
    )
    legend = "".join(
        f'<rect x="{legend_x + i * 14}" y="{gy + 7 * step + 8}" width="11" height="11" rx="2.5" fill="{c}"/>'
        for i, c in enumerate(BLUE)
    )
    h = gy + 7 * step + 44
    body = f"""
<rect x=".5" y=".5" width="{W - 1}" height="{h - 1}" rx="14" fill="{BG}" stroke="{BORDER}" stroke-width="1"/>
<text class="r" {d(1.5)} x="44" y="58" font-family="{SERIF}" font-size="34" fill="{TEXT}">Every day, <tspan font-style="italic" fill="{ACCENT}">in blue</tspan></text>
<text class="f" {d(1.55)} x="{right}" y="56" text-anchor="end" font-family="{MONO}" font-size="12" letter-spacing="1" fill="{MUTED}">REFRESHED DAILY</text>
{''.join(cells)}
<g class="f" {d(2.6)}>
  {labels}
  <text x="{legend_x - 8}" y="{gy + 7 * step + 18}" text-anchor="end" font-family="{MONO}" font-size="11" fill="{MUTED}">less</text>
  {legend}
  <text x="{legend_x + len(BLUE) * 14 + 4}" y="{gy + 7 * step + 18}" font-family="{MONO}" font-size="11" fill="{MUTED}">more</text>
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


# ---- 4 · monthly contributions bar chart & activity stats ---------------------
def activity(data):
    h = 340
    monthly = data["monthly"][-12:]
    best = max(monthly[:-1] or monthly, key=lambda m: m["total"])
    top = max(1, best["total"])
    x0, x1, base, maxh, gap = 40, 600, 292, 140, 10
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
            fill = "#192A56"
        elif partial:
            fill = "#2C4278"
        else:
            fill = "#3B5598"
        label = datetime.date.fromisoformat(m["month"] + "-01").strftime("%b")
        bars.append(
            f'<rect class="g" style="animation-delay:{2.7 + i * 0.06:.2f}s" x="{x:.1f}" y="{base - bh}" '
            f'width="{bw:.1f}" height="{bh}" rx="4" fill="{fill}"><title>{label}: {m["total"]:,}</title></rect>'
            f'<text class="f" style="animation-delay:{2.7 + i * 0.06:.2f}s" x="{x + bw / 2:.1f}" y="{base + 22}" '
            f'text-anchor="middle" font-family="{MONO}" font-size="11" fill="{MUTED}">{label}</text>'
        )
        if is_best:
            bars.append(
                f'<text class="p" style="animation-delay:3.5s" x="{x + bw / 2:.1f}" y="{base - bh - 10}" '
                f'text-anchor="middle" font-family="{MONO}" font-size="11" fill="{ACCENT_BRIGHT}">{m["total"]:,}</text>'
            )

    cs = data["current_streak"]["length"]
    ls = data["longest_streak"]["length"]
    day_word = "day" if cs == 1 else "days"
    streak_note = (
        "current streak, and the longest"
        if cs > 0 and cs >= ls
        else f"current streak, longest {ls} {'day' if ls == 1 else 'days'}"
    )
    total_days = len(data["days"])
    best_date_raw = data["best_day"]["date"]
    best_date_str = (
        datetime.date.fromisoformat(best_date_raw).strftime("%b %d").replace(" 0", " ")
        if best_date_raw
        else "n/a"
    )
    stats = [
        (f'{cs} <tspan font-style="italic">{day_word}</tspan>', streak_note),
        (f'{data["active_days"]}<tspan fill="{MUTED}"> / {total_days}</tspan>', "active days in the last year"),
        (f'{data["best_day"]["count"]} <tspan font-style="italic">commits</tspan>', f"busiest day ({best_date_str})"),
    ]
    side = []
    for i, (big, small) in enumerate(stats):
        y = 104 + i * 92
        side.append(
            f'<g class="r" {d(3.0 + i * 0.15)}>'
            f'<text x="645" y="{y}" font-family="{SERIF}" font-size="40" fill="{TEXT}">{big}</text>'
            f'<text x="645" y="{y + 24}" font-family="{SANS}" font-size="13" fill="{MUTED}">{escape(small)}</text></g>'
        )
        if i < 2:
            side.append(
                f'<rect class="f" {d(3.0)} x="645" y="{y + 44}" width="195" height="1" fill="{BORDER}"/>'
            )

    body = f"""
<rect x=".5" y=".5" width="{W - 1}" height="{h - 1}" rx="14" fill="{BG}" stroke="{BORDER}" stroke-width="1"/>
<text class="f" {d(2.6)} x="40" y="56" font-family="{MONO}" font-size="12" letter-spacing="1.2" fill="{MUTED}">THE LAST 12 MONTHS ON GITHUB</text>
<text class="r" {d(2.65)} x="38" y="112" font-family="{SERIF}" font-size="52" fill="{TEXT}">{data["total_contributions"]:,} <tspan font-style="italic" fill="{ACCENT}">contributions</tspan></text>
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
            f'{data["total_contributions"]:,} contributions in the last year, {cs}-day current streak, {ls}-day longest streak',
        ),
    )


# ---- 5 · featured repository cards --------------------------------------------
REPO_W, REPO_H = 880 / 3 - 8, 182
REPOS = [
    (
        "repo-aspnet-guide",
        "-Zero-to-live-aspnet-guide",
        "Zero-to-Live ASP.NET",
        "Interactive 13-chapter ASP.NET Core guide from server basics to production.",
        ".NET / HTML",
        "guide",
        ACCENT,
    ),
    (
        "repo-qa-playwright",
        "QA-Playwright-Project-Original",
        "QA Playwright Engine",
        "Automated QA testing engine with Playwright, Flask UI, OTP auth & reports.",
        "Python",
        "Playwright",
        "#58A6FF",
    ),
    (
        "repo-system-health",
        "System-Health-Monitor",
        "System Health Monitor",
        "Real-time CPU & RAM monitor with incident logging and SMTP email alerts.",
        "Python",
        "monitoring",
        "#7AA2F7",
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


def repo_card(i, card_slug, repo_name, title, desc, lang, tag, color, stars):
    delay = 3.7 + i * 0.14
    meta = f"{lang}  \u00b7  \u2605 {stars}" if stars else f"{lang}  \u00b7  {tag}"
    body = f"""
<rect x=".5" y=".5" width="{REPO_W - 1:.3f}" height="{REPO_H - 1}" rx="14" fill="{BG}" stroke="{BORDER}" stroke-width="1"/>
<g class="r" {d(delay)}>
  <rect x="22" y="29" width="8" height="8" rx="2" fill="{color}"/>
  <text x="38" y="38" font-family="{SANS}" font-weight="600" font-size="17" fill="{TEXT}">{escape(title)}</text>
  {text_lines(22, 72, wrap(desc, 34), 21, f'font-family="{SANS}" font-size="14" fill="{TEXT_SOFT}"')}
  <text x="22" y="{REPO_H - 22}" font-family="{MONO}" font-size="12" fill="{MUTED}">{escape(meta)}</text>
  <text class="nu" x="{REPO_W - 34:.1f}" y="{REPO_H - 22}" font-family="{MONO}" font-size="13" fill="{ACCENT}">&#8599;</text>
</g>
"""
    write(
        f"{card_slug}.svg",
        svg(
            REPO_W,
            REPO_H,
            body,
            ["sans", "sans-b", "mono"],
            f"{title} ({repo_name}): {desc}",
            left=4 * i,
            right=8 - 4 * i,
        ),
    )


if __name__ == "__main__":
    with open(DATA, encoding="utf-8") as f:
        data = json.load(f)
    hero()
    tile(
        "build",
        "BUILD",
        "#101D42",
        "#2A4380",
        ACCENT,
        "12+",
        "services",
        "Backend APIs & Services — FastAPI, Flask, REST & SQL systems.",
        0.90,
        0,
    )
    tile(
        "learn",
        "LEARN",
        "#0E1938",
        "#243B70",
        ACCENT,
        "3",
        "core stacks",
        "Docker, Python, .NET / C# — clean architecture & automation.",
        1.10,
        1,
    )
    tile(
        "cloud",
        "CLOUD",
        "#12204A",
        "#2F4B8A",
        ACCENT,
        "100%",
        "cloud IaC",
        "Azure, Bicep, Infrastructure — CI/CD & cloud-native delivery.",
        1.30,
        2,
    )
    heatmap(data)
    activity(data)
    stars = repo_stars()
    for i, (slug, repo_name, title, desc, lang, tag, color) in enumerate(REPOS):
        repo_card(i, slug, repo_name, title, desc, lang, tag, color, stars.get(repo_name, 0))
