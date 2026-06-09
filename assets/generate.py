#!/usr/bin/env python3
"""
Generate a neofetch-style profile SVG: a colored ASCII-art portrait (left)
rendered from a photo, next to a 'system info' panel (right).

Inspired by the layout of github.com/Andrew6rant/Andrew6rant, adapted for a
cybersecurity profile. Pure static output — no GitHub Actions / API needed.
"""
import sys, html
from PIL import Image, ImageEnhance

SRC = sys.argv[1] if len(sys.argv) > 1 else "avatar.jpg"
OUT = sys.argv[2] if len(sys.argv) > 2 else "profile.svg"
PREVIEW = "preview.png"

# ---- tunables -------------------------------------------------------------
# crop box as fractions of the source (left, top, right, bottom) -> the subject
CROP = (0.30, 0.36, 0.68, 0.99)
COLS = 44                 # art width in characters
CHAR_ASPECT = 0.50        # monospace glyph w/h
SAT_BOOST = 1.28          # pop the colors on the dark bg
CONTRAST = 1.12
MIN_V = 70                # floor brightness of any drawn (non-space) glyph
RAMP = " .'`^\",:;Il!i~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"

# ---- palette (matches the CV landing page) --------------------------------
BG      = "#0a0d0b"
BAR     = "#0e1210"
GREEN   = "#5be39a"
ORANGE  = "#e0843c"
INK     = "#d9e0d9"
MUT     = "#8a978d"
FAINT   = "#5d6a61"
RED     = "#ff5f57"; YELLOW = "#febc2e"; GRN = "#28c840"

def load_cells():
    im = Image.open(SRC).convert("RGB")
    W, H = im.size
    box = (int(CROP[0]*W), int(CROP[1]*H), int(CROP[2]*W), int(CROP[3]*H))
    im = im.crop(box)
    im = ImageEnhance.Color(im).enhance(SAT_BOOST)
    im = ImageEnhance.Contrast(im).enhance(CONTRAST)
    cw, ch = im.size
    rows = max(1, int(round(COLS * (ch/cw) * CHAR_ASPECT)))
    small = im.resize((COLS, rows), Image.LANCZOS)
    px = small.load()
    grid = []
    for y in range(rows):
        line = []
        for x in range(COLS):
            r, g, b = px[x, y]
            lum = 0.2126*r + 0.7152*g + 0.0722*b
            idx = int(lum/255 * (len(RAMP)-1))
            chs = RAMP[idx]
            if chs != " ":
                # lift very dark colors so the glyph is visible on dark bg
                m = max(r, g, b)
                if m < MIN_V and m > 0:
                    f = MIN_V/m
                    r, g, b = min(255,int(r*f)), min(255,int(g*f)), min(255,int(b*f))
            line.append((chs, (r, g, b)))
        grid.append(line)
    return grid

def save_preview(grid):
    """Upscaled block render of the chosen cells, to eyeball recognizability."""
    rows, cols = len(grid), len(grid[0])
    scale = 10
    img = Image.new("RGB", (cols*scale, rows*scale), BG)
    p = img.load()
    for y, line in enumerate(grid):
        for x, (chs, col) in enumerate(line):
            c = col if chs != " " else (10, 13, 11)
            for dy in range(scale):
                for dx in range(scale):
                    p[x*scale+dx, y*scale+dy] = c
    img.save(PREVIEW)

# ---- info panel content ---------------------------------------------------
HEADER = ("peter", "㉿", "PeterGabaldon")
INFO = [
    ("Host",      "ITRESIT — Murcia, Spain"),
    ("Role",      "Cybersecurity Coordinator & Engineer"),
    ("Kernel",    "Offensive Security · Vulnerability Research"),
    ("Uptime",    "5 yrs professional · 10+ self-taught"),
    ("Education", "BSc Computer Engineering — Univ. of Murcia"),
    None,
    ("Code",      "C · C++ · C# · Java · Python · PHP · Bash · SQL"),
    ("Reversing", "IDA Pro · Ghidra · WinDbg · gdb · OllyDbg"),
    ("Offense",   "Burp Suite · Impacket · Malware & Exploit Dev"),
    ("Defense",   "CrowdStrike · Azure Sentinel · Defender"),
    ("Network",   "Fortinet · FortiGate hardening · Secure design"),
    ("Certs",     "OSED · OSEP · OSCP · CrowdStrike CFA · NSE 1-3"),
    None,
    ("Blog",            "https://pgj11.com"),
    ("Labs @ ITRESIT",  "https://labs.itresit.es"),
    ("LinkedIn",        "in/pedro-gabaldon-julia"),
]
PALETTE = [RED, ORANGE, YELLOW, GREEN, "#3aa0ff", "#b06bff", "#3ad6c8", INK]

def esc(s): return html.escape(s, quote=True)

def build_svg(grid):
    rows, cols = len(grid), len(grid[0])
    # geometry
    art_fs   = 12.5
    art_lh   = 13.0
    art_cw   = art_fs * 0.60
    pad      = 26
    art_x    = pad
    art_top  = 70
    art_w    = cols * art_cw
    info_x   = art_x + art_w + 56          # clear gap so art can't touch the panel
    info_fs  = 14
    info_lh  = 22.5
    info_top = 96
    key_w    = 140                         # wide enough for "Labs @ ITRESIT:"

    art_h = art_top + rows*art_lh
    info_h = info_top + (len(INFO)+4)*info_lh
    width  = int(info_x + 600)
    height = int(max(art_h, info_h) + pad)

    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
               f'viewBox="0 0 {width} {height}" font-family="\'JetBrains Mono\',\'Cascadia Code\',\'Fira Code\',Consolas,Menlo,monospace">')
    # window
    out.append(f'<rect x="0" y="0" width="{width}" height="{height}" rx="14" fill="{BG}" stroke="rgba(255,255,255,.12)"/>')
    out.append(f'<rect x="0" y="0" width="{width}" height="40" rx="14" fill="{BAR}"/>')
    out.append(f'<rect x="0" y="26" width="{width}" height="14" fill="{BAR}"/>')
    for i, c in enumerate((RED, YELLOW, GRN)):
        out.append(f'<circle cx="{24+i*20}" cy="20" r="6" fill="{c}"/>')
    out.append(f'<text x="{width/2}" y="24.5" fill="{FAINT}" font-size="12.5" text-anchor="middle">'
               f'zsh — ssh peter@PeterGabaldon</text>')

    # ascii art — each glyph is pinned to an explicit (x, y) on a fixed grid,
    # so column alignment never depends on the renderer's font advance width.
    # That is what keeps the portrait inside art_w and stops it drifting into
    # the info panel. Space cells are simply skipped (they show the bg).
    out.append(f'<g font-size="{art_fs}" text-anchor="middle">')
    half = art_cw / 2
    for y, line in enumerate(grid):
        ry = art_top + y * art_lh
        for x, (chs, col) in enumerate(line):
            if chs == " ":
                continue
            cx = art_x + x * art_cw + half
            out.append(f'<text x="{cx:.1f}" y="{ry:.1f}" fill="rgb{col}">{esc(chs)}</text>')
    out.append('</g>')

    # info panel
    iy = info_top
    out.append(f'<text x="{info_x}" y="{iy}" font-size="{info_fs+1}" font-weight="700">'
               f'<tspan fill="{GREEN}">{HEADER[0]}</tspan>'
               f'<tspan fill="{ORANGE}">{HEADER[1]}</tspan>'
               f'<tspan fill="{GREEN}">{HEADER[2]}</tspan></text>')
    iy += info_lh*0.7
    dashes = "─" * 38
    out.append(f'<text x="{info_x}" y="{iy}" font-size="{info_fs}" fill="{FAINT}">{dashes}</text>')
    for item in INFO:
        iy += info_lh
        if item is None:
            continue
        k, v = item
        is_url = v.startswith("http")
        vfill = ORANGE if is_url else INK
        out.append(f'<text x="{info_x}" y="{iy}" font-size="{info_fs}">'
                   f'<tspan fill="{GREEN}" font-weight="600">{esc(k)}</tspan>'
                   f'<tspan fill="{FAINT}">:</tspan></text>')
        out.append(f'<text x="{info_x+key_w}" y="{iy}" font-size="{info_fs}" fill="{vfill}">{esc(v)}</text>')

    # palette blocks (neofetch colour bar)
    iy += info_lh*1.4
    bw = 22
    for i, c in enumerate(PALETTE):
        out.append(f'<rect x="{info_x + i*bw}" y="{iy}" width="{bw-3}" height="12" rx="2" fill="{c}"/>')

    out.append('</svg>')
    return "\n".join(out)

if __name__ == "__main__":
    grid = load_cells()
    save_preview(grid)
    svg = build_svg(grid)
    with open(OUT, "w") as f:
        f.write(svg)
    print(f"wrote {OUT} ({len(svg)} bytes), {PREVIEW}, grid {len(grid)}x{len(grid[0])}")
