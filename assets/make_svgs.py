#!/usr/bin/env python3
"""Generates the animated SVGs for the yvursol GitHub profile README (dark + light)."""
import math
import random
import sys
from pathlib import Path
from xml.sax.saxutils import escape as esc

OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)

SANS = "'Segoe UI', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Inter, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'Cascadia Mono', Consolas, 'DejaVu Sans Mono', Menlo, monospace"
MONO_W = 0.62  # generous average glyph width (em) for monospace fonts

THEMES = {
    "dark": dict(
        bg0="#0a111f", bg1="#0d1b2e", panel="#0f1a2b", panel2="#13223a", stroke="#1f3049",
        text="#e6edf3", muted="#8da2b8", faint="#4a5d78",
        cyan="#22d3ee", blue="#3b9eff", deep="#0077b5", green="#34d399", amber="#fbbf24",
        rose="#fb7185", violet="#a78bfa",
        rack="#121c2c", rack2="#0c1420", unit="#16233a", unit2="#1b2b46", led_off="#22324a",
        glow_op="0.55", grid_op="0.05", shine_op=".07",
    ),
    "light": dict(
        bg0="#ffffff", bg1="#eef6fb", panel="#f6fafd", panel2="#eaf3fa", stroke="#d3e1ec",
        text="#0d1b2a", muted="#52637a", faint="#9aabbf",
        cyan="#0091b0", blue="#0077b5", deep="#005792", green="#059669", amber="#b45309",
        rose="#e11d48", violet="#7c3aed",
        rack="#26354d", rack2="#1b273a", unit="#2f4160", unit2="#384d70", led_off="#4a5d7c",
        glow_op="0.30", grid_op="0.06", shine_op=".9",
    ),
}

def text_w(s, size):
    """Generous width estimate for proportional sans text (Segoe UI / SF / Inter / DejaVu)."""
    w = 0.0
    for ch in s:
        if ch in "MWmw@":
            w += 0.86
        elif ch.isupper() or ch.isdigit() or ch in "&#%":
            w += 0.68
        elif ch in "iljtfr .,:;!|'·()-":
            w += 0.34
        else:
            w += 0.57
    return w * size * 1.04


REDUCED = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"


def svg(w, h, body, title, desc=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" aria-labelledby="t d" fill="none">\n'
        f'<title id="t">{esc(title)}</title><desc id="d">{esc(desc or title)}</desc>\n{body}\n</svg>\n'
    )


def panel_defs(t, w, h, pid="p"):
    return f"""
  <linearGradient id="{pid}bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{t['bg0']}"/><stop offset="1" stop-color="{t['bg1']}"/>
  </linearGradient>
  <linearGradient id="{pid}edge" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{t['cyan']}" stop-opacity="0"/>
    <stop offset=".5" stop-color="{t['cyan']}" stop-opacity=".9"/>
    <stop offset="1" stop-color="{t['blue']}" stop-opacity="0"/>
  </linearGradient>
  <pattern id="{pid}grid" width="32" height="32" patternUnits="userSpaceOnUse">
    <path d="M32 0H0V32" stroke="{t['text']}" stroke-opacity="{t['grid_op']}" stroke-width="1"/>
  </pattern>
  <clipPath id="{pid}clip"><rect width="{w}" height="{h}" rx="22"/></clipPath>"""


def panel(t, w, h, pid="p", grid=True):
    g = f'<rect width="{w}" height="{h}" fill="url(#{pid}grid)"/>' if grid else ""
    return (
        f'<rect width="{w}" height="{h}" rx="22" fill="url(#{pid}bg)"/>'
        f'<g clip-path="url(#{pid}clip)">{g}'
        f'<rect class="edge" x="-{w}" y="0" width="{w}" height="2" fill="url(#{pid}edge)"/></g>'
        f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="21.5" stroke="{t["stroke"]}"/>'
    )


EDGE_CSS = ".edge{animation:edge 6s linear infinite}@keyframes edge{to{transform:translateX(200%)}}"


# --------------------------------------------------------------------------- hero
def hero(t, name):
    W, H = 1280, 420
    rnd = random.Random(7)
    css = [EDGE_CSS, REDUCED]

    # network graph background
    nodes = []
    while len(nodes) < 30:
        x, y = rnd.uniform(30, W - 30), rnd.uniform(30, H - 30)
        if all(math.hypot(x - a, y - b) > 95 for a, b in nodes):
            nodes.append((x, y))
    edges = []
    for i, (x1, y1) in enumerate(nodes):
        near = sorted(range(len(nodes)), key=lambda j: math.hypot(nodes[j][0] - x1, nodes[j][1] - y1))[1:3]
        for j in near:
            if (j, i) not in edges:
                edges.append((i, j))
    net = []
    for k, (i, j) in enumerate(edges):
        (x1, y1), (x2, y2) = nodes[i], nodes[j]
        net.append(f'<path id="e{k}" d="M{x1:.0f} {y1:.0f}L{x2:.0f} {y2:.0f}" stroke="{t["cyan"]}" stroke-opacity=".14"/>')
    for k, (x, y) in enumerate(nodes):
        d = rnd.uniform(2.5, 5.5)
        dl = rnd.uniform(0, 4)
        net.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rnd.choice([2, 2.5, 3])}" fill="{t["cyan"]}" '
                   f'class="np" style="animation-duration:{d:.1f}s;animation-delay:-{dl:.1f}s"/>')
    for k in rnd.sample(range(len(edges)), 9):
        dur = rnd.uniform(2.6, 5.0)
        col = rnd.choice([t["cyan"], t["blue"], t["green"]])
        net.append(f'<circle r="2.6" fill="{col}" filter="url(#soft)"><animateMotion dur="{dur:.1f}s" '
                   f'repeatCount="indefinite" begin="-{rnd.uniform(0, dur):.1f}s"><mpath href="#e{k}"/></animateMotion></circle>')
    css.append(".np{animation:np 4s ease-in-out infinite;opacity:.35}"
               "@keyframes np{50%{opacity:.9}}")

    # left text block
    phrases = [
        "VMware vSphere · Windows Server",
        "FireBird · Oracle · Data Pump",
        "backups that actually restore",
        "PowerShell & Python automation",
        "Zabbix · Grafana monitoring",
    ]
    slot = 4.0
    total = slot * len(phrases)
    fx, fy, fw, fh = 72, 286, 600, 52
    tx, ty, fs = fx + 46, fy + 34, 21
    cw = fs * MONO_W
    typer = []
    for i, p in enumerate(phrases):
        L = len(p)
        wpx = math.ceil(L * cw) + 6
        s = i * slot / total * 100
        a = (i * slot + 1.6) / total * 100     # typed
        b = (i * slot + 3.2) / total * 100     # start delete
        c = (i * slot + 3.7) / total * 100     # deleted
        e = (i + 1) * slot / total * 100
        eps = 0.01
        kf_vis = (f"@keyframes v{i}{{0%{{opacity:0}}{max(s-eps,0):.3f}%{{opacity:0}}{s:.3f}%{{opacity:1}}"
                  f"{e-eps:.3f}%{{opacity:1}}{e:.3f}%{{opacity:0}}100%{{opacity:0}}}}")
        kf_cov = (f"@keyframes c{i}{{0%{{transform:translateX(0)}}"
                  f"{s:.3f}%{{transform:translateX(0);animation-timing-function:steps({L},end)}}"
                  f"{a:.3f}%{{transform:translateX({wpx}px)}}"
                  f"{b:.3f}%{{transform:translateX({wpx}px);animation-timing-function:steps({max(L//2,1)},end)}}"
                  f"{c:.3f}%{{transform:translateX(0)}}100%{{transform:translateX(0)}}}}")
        css.append(kf_vis + kf_cov)
        css.append(f".v{i}{{animation:v{i} {total}s linear infinite}}.c{i}{{animation:c{i} {total}s linear infinite}}")
        typer.append(
            f'<g class="v{i}" opacity="0"><text x="{tx}" y="{ty}" font-family="{MONO}" font-size="{fs}" '
            f'fill="{t["text"]}">{esc(p)}</text>'
            f'<g class="c{i}"><rect x="{tx}" y="{fy+8}" width="{wpx+4}" height="{fh-16}" fill="{t["panel"]}"/>'
            f'<rect class="cur" x="{tx+1}" y="{fy+13}" width="11" height="{fh-26}" rx="1.5" fill="{t["cyan"]}"/></g></g>')
    css.append(".cur{animation:cur 1s steps(1) infinite}@keyframes cur{50%{opacity:0}}")

    left = f"""
  <text x="72" y="96" font-family="{MONO}" font-size="18" fill="{t['cyan']}">PS C:\\&gt; whoami</text>
  <text x="68" y="178" font-family="{SANS}" font-size="78" font-weight="800" fill="url(#title)" letter-spacing="-1.5">Hi, I&#8217;m {esc(name)}</text>
  <text x="72" y="222" font-family="{SANS}" font-size="30" font-weight="600" fill="{t['text']}">Systems Engineer</text>
  <text x="72" y="258" font-family="{SANS}" font-size="18" fill="{t['muted']}">I keep infrastructure running — and make sure it can be restored when it breaks.</text>
  <rect x="{fx}" y="{fy}" width="{fw}" height="{fh}" rx="12" fill="{t['panel']}" stroke="{t['stroke']}"/>
  <text x="{fx+18}" y="{ty}" font-family="{MONO}" font-size="{fs}" fill="{t['green']}">&gt;</text>
  <clipPath id="fieldclip"><rect x="{fx+40}" y="{fy+2}" width="{fw-46}" height="{fh-4}" rx="10"/></clipPath>
  <g clip-path="url(#fieldclip)">{''.join(typer)}</g>
  <g font-family="{MONO}" font-size="13" fill="{t['muted']}">
    <circle cx="80" cy="371" r="4" fill="{t['green']}" class="pulse"/>
    <text x="92" y="376">all systems nominal · last restore test: passed</text>
  </g>"""
    css.append(".pulse{animation:pulse 2s ease-in-out infinite;transform-box:fill-box;transform-origin:center}"
               "@keyframes pulse{50%{opacity:.35;transform:scale(1.6)}}")

    # server rack (right)
    rx0, ry0, rw, rh = 900, 44, 300, 332
    units = [("esxi-01", 2), ("esxi-02", 2), ("fb-db", 1), ("ora-db", 1), ("backup", 1), ("nas-01", 1)]
    rack = [
        f'<ellipse cx="{rx0+rw/2}" cy="{ry0+rh+18}" rx="190" ry="14" fill="{t["cyan"]}" opacity=".10" filter="url(#blur)"/>',
        f'<rect x="{rx0-14}" y="{ry0-14}" width="{rw+28}" height="{rh+28}" rx="16" fill="url(#rackg)" stroke="{t["stroke"]}"/>',
        f'<rect x="{rx0-4}" y="{ry0-4}" width="{rw+8}" height="{rh+8}" rx="8" fill="{t["rack2"]}"/>',
    ]
    for k in range(0, rh, 14):
        rack.append(f'<circle cx="{rx0-8}" cy="{ry0+k+7}" r="1.4" fill="{t["led_off"]}"/>'
                    f'<circle cx="{rx0+rw+8}" cy="{ry0+k+7}" r="1.4" fill="{t["led_off"]}"/>')
    blink = []
    for b in range(8):
        d = rnd.choice([0.45, 0.7, 0.9, 1.3, 1.7, 2.4])
        blink.append(f".b{b}{{animation:bk {d}s steps(1) infinite;animation-delay:-{rnd.uniform(0, 2):.2f}s}}")
    css.append("@keyframes bk{0%{opacity:1}50%{opacity:.15}}")
    css += blink
    y = ry0 + 4
    u1 = 40
    for label, size in units:
        uh = u1 * size - 6
        ux, uw = rx0 + 6, rw - 12
        rack.append(f'<rect x="{ux}" y="{y}" width="{uw}" height="{uh}" rx="5" fill="url(#unitg)" stroke="{t["stroke"]}" stroke-opacity=".6"/>')
        rack.append(f'<text x="{ux+12}" y="{y+21}" font-family="{MONO}" font-size="11.5" fill="#9fb3c8">{label}</text>')
        # status LEDs
        rack.append(f'<circle cx="{ux+uw-14}" cy="{y+17}" r="3.2" fill="{t["green"]}" class="b{rnd.randrange(8)}" filter="url(#soft)"/>')
        rack.append(f'<circle cx="{ux+uw-26}" cy="{y+17}" r="3.2" fill="{t["cyan"]}" class="b{rnd.randrange(8)}" filter="url(#soft)"/>')
        if label == "backup":
            rack.append(f'<circle cx="{ux+uw-38}" cy="{y+17}" r="3.2" fill="{t["amber"]}" class="b{rnd.randrange(8)}"/>')
        # drive bays
        bays = 6 if size == 1 else 7
        bw = 18
        for bi in range(bays):
            bx = ux + 84 + bi * (bw + 5)
            rack.append(f'<rect x="{bx}" y="{y+7}" width="{bw}" height="{uh-14}" rx="2.5" fill="{t["rack2"]}" stroke="{t["stroke"]}" stroke-opacity=".5"/>')
            rack.append(f'<rect x="{bx+4}" y="{y+uh-14}" width="{bw-8}" height="2.5" rx="1" fill="{rnd.choice([t["cyan"], t["green"]])}" class="b{rnd.randrange(8)}"/>')
        # activity bars on 2U units
        if size == 2:
            for bi in range(5):
                bx = ux + 12 + bi * 11
                dur = rnd.uniform(0.6, 1.4)
                rack.append(f'<rect x="{bx}" y="{y+30}" width="7" height="{uh-36}" rx="1.5" fill="{t["cyan"]}" opacity=".85" '
                            f'class="eq" style="animation-duration:{dur:.2f}s;animation-delay:-{rnd.uniform(0,1):.2f}s"/>')
        y += u1 * size
    css.append(".eq{transform-box:fill-box;transform-origin:bottom;animation:eq 1s ease-in-out infinite alternate}"
               "@keyframes eq{0%{transform:scaleY(.15)}100%{transform:scaleY(1)}}")
    # rack top label
    rack.append(f'<text x="{rx0+rw/2}" y="{ry0-22+4}" text-anchor="middle" font-family="{MONO}" font-size="11" fill="{t["muted"]}" opacity="0">rack</text>')

    defs = panel_defs(t, W, H) + f"""
  <linearGradient id="title" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{t['text']}"/><stop offset=".55" stop-color="{t['cyan']}"/><stop offset="1" stop-color="{t['blue']}"/>
  </linearGradient>
  <linearGradient id="rackg" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{t['rack']}"/><stop offset="1" stop-color="{t['rack2']}"/>
  </linearGradient>
  <linearGradient id="unitg" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{t['unit2']}"/><stop offset="1" stop-color="{t['unit']}"/>
  </linearGradient>
  <radialGradient id="glow" cx=".5" cy=".5" r=".5">
    <stop offset="0" stop-color="{t['cyan']}" stop-opacity="{t['glow_op']}"/><stop offset="1" stop-color="{t['cyan']}" stop-opacity="0"/>
  </radialGradient>
  <filter id="soft" x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="1.6" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <filter id="blur" x="-50%" y="-200%" width="200%" height="500%"><feGaussianBlur stdDeviation="10"/></filter>"""

    body = (f"<defs>{defs}</defs><style>{''.join(css)}</style>"
            f"{panel(t, W, H)}"
            f'<g clip-path="url(#pclip)"><circle cx="1050" cy="210" r="300" fill="url(#glow)"/>{"".join(net)}</g>'
            f"{left}{''.join(rack)}")
    return svg(W, H, body, f"Hi, I'm {name} — Systems Engineer",
               "Virtualization, databases, backup and recovery, monitoring and automation.")


# --------------------------------------------------------------------------- terminal
def terminal(t):
    W = 1280
    fs, lh = 17, 31
    top = 70
    K = t["cyan"]; M = t["muted"]; V = t["text"]; G = t["green"]; A = t["amber"]
    cmd = "Get-Engineer -Name yvursol | Format-List"
    rows = [
        ("Name", [("Yuri", V)]),
        ("Role", [("Systems Engineer", V)]),
        ("Focus", [("virtualization · databases · backup & recovery · monitoring", V)]),
        ("Platforms", [("VMware vSphere, Windows Server, FireBird, Oracle", V)]),
        ("Automates", [("PowerShell, Python, batch ", V), ("# twice by hand = a script", M)]),
        ("Monitors", [("Zabbix, Grafana", V)]),
        ("Learning", [("Linux, Docker, Ansible, German (A2 → B1)", A)]),
        ("Speaks", [("Russian · German · English · Serbian", V)]),
        ("Motto", [("A backup only counts if it can be restored.", G)]),
    ]
    H = top + 40 + lh * (len(rows) + 3) + 24
    cw = fs * MONO_W
    css = [REDUCED, ".cur{animation:cur 1s steps(1) infinite}@keyframes cur{50%{opacity:0}}"]
    total = 16.0
    type_end = 2.2
    # command typing via sliding cover
    L = len(cmd)
    px0 = 40 + math.ceil(len("PS C:\\> ") * cw)
    wpx = math.ceil(L * cw) + 8
    te = type_end / total * 100
    css.append(f"@keyframes ty{{0%{{transform:translateX(0);animation-timing-function:steps({L},end)}}"
               f"{te:.2f}%{{transform:translateX({wpx}px)}}{te+9:.2f}%{{transform:translateX({wpx}px)}}"
               f"{te+9.01:.2f}%{{transform:translateX(3000px)}}100%{{transform:translateX(3000px)}}}}"
               f".ty{{animation:ty {total}s linear infinite}}")
    lines = []
    y0 = top + 36
    lines.append(f'<text x="40" y="{y0}" font-family="{MONO}" font-size="{fs}"><tspan fill="{G}">PS C:\\&gt;</tspan>'
                 f'<tspan fill="{V}"> {esc(cmd)}</tspan></text>')
    lines.append(f'<g class="ty"><rect x="{px0}" y="{y0-fs-2}" width="{wpx+20}" height="{lh}" fill="{t["panel"]}"/>'
                 f'<rect class="cur" x="{px0+2}" y="{y0-fs+1}" width="10" height="{fs+3}" fill="{K}"/></g>')
    keyw = max(len(k) for k, _ in rows)
    for i, (k, vals) in enumerate(rows):
        y = y0 + lh * (i + 2)
        st = (type_end + 0.35 + i * 0.32) / total * 100
        css.append(f"@keyframes r{i}{{0%,{st:.2f}%{{opacity:0;transform:translateX(-8px)}}"
                   f"{st+1.2:.2f}%,96%{{opacity:1;transform:translateX(0)}}100%{{opacity:0}}}}"
                   f".r{i}{{animation:r{i} {total}s ease-out infinite}}")
        spans = "".join(f'<tspan fill="{c}">{esc(s)}</tspan>' for s, c in vals)
        lines.append(f'<text class="r{i}" x="40" y="{y}" font-family="{MONO}" font-size="{fs}" xml:space="preserve">'
                     f'<tspan fill="{K}">{esc(k.ljust(keyw))}</tspan><tspan fill="{M}"> : </tspan>{spans}</text>')
    yl = y0 + lh * (len(rows) + 3)
    st = (type_end + 0.35 + len(rows) * 0.32 + 0.3) / total * 100
    css.append(f"@keyframes fin{{0%,{st:.2f}%{{opacity:0}}{st+0.5:.2f}%,96%{{opacity:1}}100%{{opacity:0}}}}"
               f".fin{{animation:fin {total}s linear infinite}}")
    lines.append(f'<g class="fin"><text x="40" y="{yl}" font-family="{MONO}" font-size="{fs}" fill="{G}">PS C:\\&gt;</text>'
                 f'<rect class="cur" x="{40 + math.ceil(9*cw)}" y="{yl-fs+1}" width="10" height="{fs+3}" fill="{K}"/></g>')

    # neofetch-style pixel monogram on the right
    glyph = ["XX.....XX", "XX.....XX", ".XX...XX.", "..XX.XX..", "...XXX...",
             "...XXX...", "...XXX...", "...XXX...", "...XXX..."]
    cell, gap = 17, 4
    mx0, my0 = W - 60 - 9 * (cell + gap), top + 16
    st = (type_end + 0.3) / total * 100
    css.append(f"@keyframes mx{{0%,{st:.2f}%{{opacity:0}}{st+3:.2f}%,96%{{opacity:1}}100%{{opacity:0}}}}"
               f".mx{{animation:mx {total}s ease-out infinite}}"
               ".px{animation:px 2.8s ease-in-out infinite}@keyframes px{0%,100%{opacity:1}50%{opacity:.45}}")
    rowcols = [t["cyan"], t["cyan"], t["cyan"], t["blue"], t["blue"], t["blue"], t["deep"], t["deep"], t["deep"]]
    mx = []
    for r, row in enumerate(glyph):
        for c, ch in enumerate(row):
            x, y = mx0 + c * (cell + gap), my0 + r * (cell + gap)
            if ch == "X":
                mx.append(f'<rect class="px" style="animation-delay:{(r + c) * 0.09:.2f}s" x="{x}" y="{y}" '
                          f'width="{cell}" height="{cell}" rx="3" fill="{rowcols[r]}"/>')
            else:
                mx.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" fill="{t["panel2"]}"/>')
    pal = [t["rose"], t["amber"], t["green"], t["cyan"], t["blue"], t["violet"], t["muted"], t["text"]]
    py = my0 + 9 * (cell + gap) + 18
    pw = (9 * (cell + gap) - gap - 7 * 5) / 8
    for i, col in enumerate(pal):
        mx.append(f'<rect x="{mx0 + i * (pw + 5):.1f}" y="{py}" width="{pw:.1f}" height="14" rx="3" fill="{col}"/>')
    mx.append(f'<text x="{mx0 + (9 * (cell + gap) - gap) / 2:.0f}" y="{py + 40}" text-anchor="middle" font-family="{MONO}" '
              f'font-size="14" fill="{M}">yvursol@github</text>')
    lines.append(f'<g class="mx">{"".join(mx)}</g>')

    chrome = f"""
  <rect x="0" y="0" width="{W}" height="{H}" rx="18" fill="{t['panel']}"/>
  <path d="M18 0H{W-18}A18 18 0 0 1 {W} 18V46H0V18A18 18 0 0 1 18 0Z" fill="{t['panel2']}"/>
  <circle cx="30" cy="23" r="7" fill="#ff5f57"/><circle cx="54" cy="23" r="7" fill="#febc2e"/><circle cx="78" cy="23" r="7" fill="#28c840"/>
  <text x="{W/2}" y="28" text-anchor="middle" font-family="{MONO}" font-size="13" fill="{M}">pwsh — yvursol@github</text>
  <rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="17.5" stroke="{t['stroke']}"/>"""
    body = f"<style>{''.join(css)}</style>{chrome}{''.join(lines)}"
    desc = "; ".join(f"{k}: {''.join(s for s, _ in v)}" for k, v in rows)
    return svg(W, H, body, "Get-Engineer yvursol", desc)


# --------------------------------------------------------------------------- stats
def stats(t):
    W, H = 1280, 150
    tiles = [
        ("50+", "virtual machines in my care", t["cyan"]),
        ("2022", "running production infra since", t["blue"]),
        ("24/7", "monitoring with Zabbix & Grafana", t["green"]),
        ("105", "tests in my backup toolkit", t["violet"]),
    ]
    gap = 20
    tw = (W - gap * 3) / 4
    css = [REDUCED, ".sh{animation:sh 5s ease-in-out infinite}@keyframes sh{0%{transform:translateX(-120px)}60%,100%{transform:translateX(420px)}}"]
    parts = [f"""<defs><linearGradient id="shine" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#ffffff" stop-opacity="0"/><stop offset=".5" stop-color="#ffffff" stop-opacity="{t['shine_op']}"/>
      <stop offset="1" stop-color="#ffffff" stop-opacity="0"/></linearGradient></defs>"""]
    for i, (num, label, col) in enumerate(tiles):
        x = i * (tw + gap)
        css.append(f"@keyframes in{i}{{0%{{opacity:0;transform:translateY(10px)}}100%{{opacity:1;transform:none}}}}"
                   f".in{i}{{animation:in{i} .7s {0.15*i:.2f}s ease-out both}}")
        parts.append(f"""
  <g class="in{i}">
    <clipPath id="tc{i}"><rect x="{x:.0f}" y="0" width="{tw:.0f}" height="{H}" rx="18"/></clipPath>
    <rect x="{x:.0f}" y="0" width="{tw:.0f}" height="{H}" rx="18" fill="{t['panel']}" stroke="{t['stroke']}"/>
    <rect x="{x+24:.0f}" y="0" width="56" height="3" rx="1.5" fill="{col}"/>
    <g clip-path="url(#tc{i})"><rect class="sh" style="animation-delay:{i*0.4:.1f}s" x="{x:.0f}" y="0" width="140" height="{H}" fill="url(#shine)"/></g>
    <text x="{x+24:.0f}" y="82" font-family="{SANS}" font-size="50" font-weight="800" fill="{col}" letter-spacing="-1">{esc(num)}</text>
    <text x="{x+24:.0f}" y="116" font-family="{SANS}" font-size="16" fill="{t['muted']}">{esc(label)}</text>
  </g>""")
    body = f"<style>{''.join(css)}</style>{''.join(parts)}"
    return svg(W, H, body, "By the numbers", "; ".join(f"{n} {l}" for n, l, _ in tiles))


# --------------------------------------------------------------------------- stack
def stack(t):
    W = 1280
    rows = [
        ("Virtualization", t["violet"], ["VMware vSphere", "vCenter", "ESXi", "PowerCLI"], False),
        ("Systems", t["blue"], ["Windows Server", "RAID & hardware", "Scheduled automation"], False),
        ("Databases", t["rose"], ["FireBird", "Oracle", "Data Pump", "gbak"], False),
        ("Networking", t["amber"], ["Cisco", "MikroTik", "D-Link"], False),
        ("Automation", t["cyan"], ["PowerShell", "Python", "Batch", "Pester", "GitHub Actions"], False),
        ("Monitoring", t["green"], ["Zabbix", "Grafana", "Windows Event Log"], False),
        ("Learning now", t["muted"], ["Linux", "Docker", "Ansible", "Terraform", "Bash"], True),
    ]
    rh = 56
    top = 34
    H = top + rh * len(rows) + 22
    fs = 15
    cwp = 8.9  # sans px per char at 15px, generous
    css = [REDUCED, EDGE_CSS,
           ".dot{animation:dot 2.4s ease-in-out infinite;transform-box:fill-box;transform-origin:center}"
           "@keyframes dot{50%{transform:scale(1.5);opacity:.6}}",
           "@keyframes chip{0%{opacity:0;transform:translateY(6px)}100%{opacity:1;transform:none}}"]
    parts = [f"<defs>{panel_defs(t, W, H)}</defs>", panel(t, W, H)]
    n = 0
    for r, (cat, col, chips, learning) in enumerate(rows):
        y = top + r * rh
        cy = y + 22
        parts.append(f'<circle class="dot" style="animation-delay:{r*0.3:.1f}s" cx="48" cy="{cy}" r="5" fill="{col}"/>')
        parts.append(f'<text x="64" y="{cy+5}" font-family="{MONO}" font-size="14" letter-spacing="1" fill="{t["muted"]}">{esc(cat.upper())}</text>')
        x = 270
        for c in chips:
            w = math.ceil(text_w(c, fs) + 36)
            dash = ' stroke-dasharray="5 4"' if learning else ""
            fill = "none" if learning else t["panel2"]
            parts.append(
                f'<g style="animation:chip .5s {0.04*n:.2f}s ease-out both">'
                f'<rect x="{x}" y="{y+4}" width="{w}" height="36" rx="18" fill="{fill}" stroke="{col}" stroke-opacity="{0.9 if learning else 0.45}"{dash}/>'
                f'<circle cx="{x+16}" cy="{cy}" r="3.5" fill="{col}"/>'
                f'<text x="{x+27}" y="{cy+5}" font-family="{SANS}" font-size="{fs}" fill="{t["text"]}">{esc(c)}</text></g>')
            x += w + 12
            n += 1
        if r < len(rows) - 1:
            parts.append(f'<path d="M40 {y+rh-4}H{W-40}" stroke="{t["stroke"]}" stroke-opacity=".6"/>')
    body = f"<style>{''.join(css)}</style>{''.join(parts)}"
    desc = "; ".join(f"{c}: {', '.join(ch)}" for c, _, ch, _ in rows)
    return svg(W, H, body, "Toolbox", desc)


# --------------------------------------------------------------------------- project cards
def card(t, kind):
    W, H = 620, 270
    css = [REDUCED, EDGE_CSS]
    pid = "k"
    parts = [f"<defs>{panel_defs(t, W, H, pid)}"
             f'<filter id="soft" x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="2" result="b"/>'
             f'<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>',
             panel(t, W, H, pid)]
    if kind == "backup":
        title = "Backup-FireBird-und-Oracle"
        lines = ["Nightly backups for FireBird, Oracle & VMware:",
                 "test-restored, encrypted, checksummed, sent offsite."]
        tags = [("PowerShell", t["blue"]), ("Pester · 105 tests", t["violet"]), ("AES-256 + HMAC", t["green"]), ("CI", t["cyan"])]
        icon = f'<path d="M0 -14L12 -9V0C12 8 6 13 0 15C-6 13 -12 8 -12 0V-9Z" stroke="{t["cyan"]}" stroke-width="2"/><path d="M-5 0L-1 4L6 -4" stroke="{t["green"]}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>'
        # pipeline mini animation
        steps = ["backup", "verify", "encrypt", "hash", "offsite"]
        x0, x1, py = 50, 570, 222
        anim = [f'<path d="M{x0} {py}H{x1}" stroke="{t["stroke"]}" stroke-width="2"/>',
                f'<path class="prog" d="M{x0} {py}H{x1}" stroke="{t["cyan"]}" stroke-width="2.5" stroke-dasharray="{x1-x0}" stroke-dashoffset="{x1-x0}"/>']
        D = 5.0
        css.append(f".prog{{animation:prog {D}s ease-in-out infinite}}@keyframes prog{{0%{{stroke-dashoffset:{x1-x0}}}75%{{stroke-dashoffset:0}}90%{{stroke-dashoffset:0;opacity:1}}100%{{stroke-dashoffset:0;opacity:0}}}}")
        for i, s in enumerate(steps):
            x = x0 + i * (x1 - x0) / (len(steps) - 1)
            at = i / (len(steps) - 1) * 75
            css.append(f"@keyframes n{i}{{0%,{max(at-1,0):.1f}%{{fill:{t['panel2']};stroke:{t['faint']}}}{at+2:.1f}%,92%{{fill:{t['cyan']};stroke:{t['cyan']}}}100%{{fill:{t['panel2']};stroke:{t['faint']}}}}}"
                       f".n{i}{{animation:n{i} {D}s ease-in-out infinite}}")
            anim.append(f'<circle class="n{i}" cx="{x:.0f}" cy="{py}" r="7" stroke-width="2" fill="{t["panel2"]}" stroke="{t["faint"]}"/>')
            anim.append(f'<text x="{x:.0f}" y="{py+28}" text-anchor="middle" font-family="{MONO}" font-size="12" fill="{t["muted"]}">{s}</text>')
    else:
        title = "itvursol.com"
        lines = ["Personal site with an animated network graph,",
                 "in four languages: DE · EN · RU · SR."]
        tags = [("HTML", t["rose"]), ("CSS", t["blue"]), ("JavaScript", t["amber"]), ("SVG animation", t["cyan"])]
        icon = f'<circle r="13" stroke="{t["cyan"]}" stroke-width="2"/><ellipse rx="6" ry="13" stroke="{t["cyan"]}" stroke-width="1.6"/><path d="M-13 0H13M-11 -6H11M-11 6H11" stroke="{t["cyan"]}" stroke-width="1.4"/>'
        rnd = random.Random(5)
        # cycling greeting in the four languages of the site
        greets = [("DE", "Hallo"), ("EN", "Hello"), ("RU", "Привет"), ("SR", "Zdravo")]
        D = 10.0
        anim = []
        for i, (code, word) in enumerate(greets):
            s0 = i * D / len(greets) / D * 100
            s1 = (i + 1) * D / len(greets) / D * 100
            css.append(f"@keyframes g{i}{{0%,{max(s0-0.01,0):.2f}%{{opacity:0;transform:translateY(8px)}}"
                       f"{s0+3:.2f}%,{s1-4:.2f}%{{opacity:1;transform:none}}{s1:.2f}%,100%{{opacity:0;transform:translateY(-8px)}}}}"
                       f".g{i}{{animation:g{i} {D}s ease-in-out infinite}}")
            anim.append(f'<g class="g{i}" opacity="0">'
                        f'<rect x="30" y="200" width="38" height="24" rx="6" fill="{t["panel2"]}" stroke="{t["cyan"]}" stroke-opacity=".6"/>'
                        f'<text x="49" y="217" text-anchor="middle" font-family="{MONO}" font-size="12" fill="{t["cyan"]}">{code}</text>'
                        f'<text x="80" y="224" font-family="{SANS}" font-size="32" font-weight="700" fill="url(#gt)">{esc(word)}</text></g>')
        parts[0] = parts[0].replace("</defs>", f'<linearGradient id="gt" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{t["cyan"]}"/>'
                                    f'<stop offset="1" stop-color="{t["blue"]}"/></linearGradient></defs>')
        # small network cluster on the right
        pts = []
        while len(pts) < 11:
            p = (rnd.uniform(330, 590), rnd.uniform(188, 252))
            if all(math.hypot(p[0] - a, p[1] - b) > 30 for a, b in pts):
                pts.append(p)
        k = 0
        for i, (a, b) in enumerate(pts):
            for j in sorted(range(len(pts)), key=lambda j: math.hypot(pts[j][0] - a, pts[j][1] - b))[1:4]:
                c, d = pts[j]
                anim.append(f'<path id="w{k}" d="M{a:.0f} {b:.0f}L{c:.0f} {d:.0f}" stroke="{t["cyan"]}" stroke-opacity=".3"/>')
                k += 1
        for a, b in pts:
            anim.append(f'<circle cx="{a:.0f}" cy="{b:.0f}" r="3.4" fill="{t["cyan"]}" class="np" style="animation-delay:-{rnd.uniform(0,3):.1f}s"/>')
        for i in range(0, k, 3):
            anim.append(f'<circle r="2.6" fill="{t["green"]}" filter="url(#soft)"><animateMotion dur="{rnd.uniform(1.4,2.4):.1f}s" '
                        f'repeatCount="indefinite" begin="-{rnd.uniform(0,1.8):.1f}s"><mpath href="#w{i}"/></animateMotion></circle>')
        css.append(".np{animation:np 3s ease-in-out infinite;opacity:.45}@keyframes np{50%{opacity:1}}")

    parts.append(f'<g transform="translate(46 50)">{icon}</g>')
    parts.append(f'<text x="74" y="58" font-family="{SANS}" font-size="25" font-weight="700" fill="{t["text"]}">{esc(title)}</text>')
    parts.append(f'<g transform="translate({W-44} 48)"><path class="arr" d="M-7 7L7 -7M-3 -7H7V3" stroke="{t["muted"]}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></g>')
    css.append(".arr{animation:arr 2.4s ease-in-out infinite}@keyframes arr{50%{transform:translate(3px,-3px)}}")
    for i, ln in enumerate(lines):
        parts.append(f'<text x="30" y="{98 + i*25}" font-family="{SANS}" font-size="17" fill="{t["muted"]}">{esc(ln)}</text>')
    x = 30
    for tag, col in tags:
        w = math.ceil(text_w(tag, 13.5) + 34)
        parts.append(f'<rect x="{x}" y="140" width="{w}" height="28" rx="14" fill="{t["panel2"]}" stroke="{col}" stroke-opacity=".5"/>'
                     f'<circle cx="{x+14}" cy="154" r="3.5" fill="{col}"/>'
                     f'<text x="{x+24}" y="159" font-family="{SANS}" font-size="13.5" fill="{t["text"]}">{esc(tag)}</text>')
        x += w + 9
    parts += anim
    body = f"<style>{''.join(css)}</style>{''.join(parts)}"
    return svg(W, H, body, title, " ".join(lines))


# --------------------------------------------------------------------------- footer
def footer(t):
    W, H = 1280, 170
    css = [REDUCED,
           ".w1{animation:wv 9s linear infinite}.w2{animation:wv 14s linear infinite reverse}.w3{animation:wv 20s linear infinite}"
           "@keyframes wv{to{transform:translateX(-640px)}}"]

    def wave(amp, y, phase):
        pts = []
        for x in range(0, W * 2 + 1, 16):
            pts.append(f"{x} {y + amp * math.sin(2 * math.pi * x / 640 + phase):.1f}")
        return "M" + " L".join(pts) + f" L{W*2} {H} L0 {H}Z"
    body = f"""<style>{''.join(css)}</style>
  <defs>
    <linearGradient id="fw" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{t['cyan']}" stop-opacity=".35"/><stop offset="1" stop-color="{t['cyan']}" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="fw2" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{t['blue']}" stop-opacity=".30"/><stop offset="1" stop-color="{t['blue']}" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="ftext" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{t['cyan']}"/><stop offset="1" stop-color="{t['blue']}"/>
    </linearGradient>
  </defs>
  <text x="{W/2}" y="52" text-anchor="middle" font-family="{SANS}" font-size="26" font-weight="700" fill="url(#ftext)">A backup only counts if it can be restored.</text>
  <text x="{W/2}" y="82" text-anchor="middle" font-family="{MONO}" font-size="14" fill="{t['muted']}">thanks for stopping by · exit 0</text>
  <path class="w3" d="{wave(8, 128, 1.3)}" fill="url(#fw2)"/>
  <path class="w2" d="{wave(10, 134, 0.4)}" fill="url(#fw)"/>
  <path class="w1" d="{wave(6, 142, 2.2)}" fill="url(#fw)"/>"""
    return svg(W, H, body, "A backup only counts if it can be restored.")


for theme, t in THEMES.items():
    files = {
        f"hero-{theme}.svg": hero(t, "Yuri"),
        f"whoami-{theme}.svg": terminal(t),
        f"stats-{theme}.svg": stats(t),
        f"stack-{theme}.svg": stack(t),
        f"card-backup-{theme}.svg": card(t, "backup"),
        f"card-site-{theme}.svg": card(t, "site"),
        f"footer-{theme}.svg": footer(t),
    }
    for name, content in files.items():
        (OUT / name).write_text(content, encoding="utf-8")
        print(f"{name:28s} {len(content)/1024:6.1f} KB")
