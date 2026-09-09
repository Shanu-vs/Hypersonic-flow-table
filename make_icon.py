"""
Build the application icon (shock.ico) without any external library.

The picture is a blunt body in a supersonic stream with its detached bow
shock:  the shock stands off ahead of the nose and sweeps downstream.
Everything is drawn analytically, supersampled 4x4 for smooth edges, and
written out as a multi-size Windows .ICO file.

Run:   python make_icon.py
"""

import math
import struct

OUT = "shock.ico"
SIZES = [16, 24, 32, 48, 64, 128, 256]
SS = 4                                   # supersampling factor per axis

# colours (r, g, b)
BG_IN = (13, 39, 71)                     # deep navy, centre
BG_OUT = (6, 18, 36)                     # darker navy, corners
SHOCK = (86, 214, 255)                   # cyan shock front
BODY = (232, 238, 244)                   # light grey body
STREAM = (120, 150, 185)                 # faint upstream streamlines


def shock_x(y):
    """x position of the bow shock at height y (both in 0..1)."""
    return 0.30 + 1.35 * (y - 0.5) ** 2


def body_sdf(x, y):
    """Negative inside the blunt-nosed body."""
    # rounded nose (circle) merged with a wedge that opens downstream
    nose = math.hypot(x - 0.56, y - 0.5) - 0.115
    wedge = max(0.50 - x, abs(y - 0.5) - (0.115 + 0.42 * max(x - 0.56, 0.0)),
                x - 0.90)
    return min(nose, wedge)


def sample(x, y):
    """Colour (r, g, b, a) of the icon at normalised point (x, y)."""
    # ---- rounded-square background ----
    r = 0.16                                    # corner radius
    dx = max(abs(x - 0.5) - (0.5 - r), 0.0)
    dy = max(abs(y - 0.5) - (0.5 - r), 0.0)
    if math.hypot(dx, dy) > r:
        return (0, 0, 0, 0)                     # outside the rounded square

    t = min(math.hypot(x - 0.5, y - 0.5) / 0.7, 1.0)
    col = [BG_IN[i] + (BG_OUT[i] - BG_IN[i]) * t for i in range(3)]

    # ---- upstream streamlines ----
    for sy in (0.30, 0.70):
        if 0.06 < x < shock_x(sy) - 0.03 and abs(y - sy) < 0.018:
            col = list(STREAM)

    # ---- bow shock ----
    if abs(x - shock_x(y)) < 0.035 and 0.06 < y < 0.94:
        col = list(SHOCK)

    # ---- body ----
    if body_sdf(x, y) < 0.0:
        col = list(BODY)

    return (int(col[0]), int(col[1]), int(col[2]), 255)


def render(n):
    """Return n*n BGRA pixels, top row first, supersampled."""
    px = []
    inv = 1.0 / (n * SS)
    for j in range(n):
        for i in range(n):
            r = g = b = a = 0
            for sj in range(SS):
                for si in range(SS):
                    x = (i * SS + si + 0.5) * inv
                    y = (j * SS + sj + 0.5) * inv
                    cr, cg, cb, ca = sample(x, y)
                    r += cr * ca; g += cg * ca; b += cb * ca; a += ca
            k = SS * SS
            if a == 0:
                px.append((0, 0, 0, 0))
            else:
                px.append((b // a, g // a, r // a, a // k))   # BGRA
    return px


def bmp_entry(n, px):
    """One .ICO image: BITMAPINFOHEADER + bottom-up BGRA + AND mask."""
    hdr = struct.pack("<IiiHHIIiiII", 40, n, 2 * n, 1, 32, 0, n * n * 4,
                      0, 0, 0, 0)
    body = bytearray()
    for j in range(n - 1, -1, -1):                    # bottom-up rows
        for i in range(n):
            body += bytes(px[j * n + i])
    mask_row = ((n + 31) // 32) * 4                   # 1 bpp, 4-byte aligned
    return hdr + bytes(body) + bytes(mask_row * n)


def main():
    images = [(n, bmp_entry(n, render(n))) for n in SIZES]

    out = bytearray(struct.pack("<HHH", 0, 1, len(images)))
    offset = 6 + 16 * len(images)
    for n, data in images:
        out += struct.pack("<BBBBHHII", n % 256, n % 256, 0, 0, 1, 32,
                           len(data), offset)
        offset += len(data)
    for _n, data in images:
        out += data

    with open(OUT, "wb") as f:
        f.write(bytes(out))
    print("wrote %s  (%d sizes, %d bytes)" % (OUT, len(images), len(out)))


if __name__ == "__main__":
    main()
