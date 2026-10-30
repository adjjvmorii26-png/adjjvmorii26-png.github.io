#!/usr/bin/env python3
"""Generate the site's raster icons and social card from the same geometry as
assets/icon.svg (concentric rings + meridian).

No third-party imaging library is required: pixels are rasterised here and
encoded as PNG with zlib from the standard library.

    python3 scripts/make-icons.py

Outputs:
    favicon-32.png          32x32   browser tab
    apple-touch-icon.png    180x180 iOS home screen
    assets/og-card.png      1200x630 social preview
"""
from __future__ import annotations

import struct
import zlib
from pathlib import Path

BLACK = (0x0B, 0x0B, 0x0D)
VIOLET = (0xC8, 0xA8, 0xFF)
GOLD = (0xFF, 0xF3, 0xA0)


def over(dst, src, alpha):
    """Source-over compositing of src at the given alpha onto dst (both RGB)."""
    return tuple(round(s * alpha + d * (1 - alpha)) for s, d in zip(src, dst))


def write_png(path: Path, width: int, height: int, pixels: list[list[tuple]]) -> None:
    raw = bytearray()
    for row in pixels:
        raw.append(0)  # filter type 0 (None)
        for r, g, b, a in row:
            raw += bytes((r, g, b, a))

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png)


def rounded_rect_coverage(x, y, size, radius):
    """1.0 inside the rounded square, 0.0 outside (hard edge, supersampled)."""
    cx = cy = size / 2
    dx, dy = abs(x - cx), abs(y - cy)
    half = size / 2
    if dx > half or dy > half:
        return 0.0
    if dx <= half - radius or dy <= half - radius:
        return 1.0
    corner_x, corner_y = half - radius, half - radius
    dist = ((dx - corner_x) ** 2 + (dy - corner_y) ** 2) ** 0.5
    return 1.0 if dist <= radius else 0.0


def ring_coverage(dist, radius, width):
    return 1.0 if abs(dist - radius) <= width / 2 else 0.0


def render_icon(size: int, samples: int = 3):
    radius = size * 0.22
    rings = [(size * 0.33, size * 0.031, VIOLET, 0.5), (size * 0.22, size * 0.031, VIOLET, 0.5)]
    inner = (size * 0.11, size * 0.031, GOLD, 0.85)
    meridian_w = size * 0.031
    cx = cy = size / 2

    rows = []
    step = 1.0 / samples
    for py in range(size):
        row = []
        for px in range(size):
            bg_cov = ring_cov = 0.0
            gold_cov = 0.0
            for sy in range(samples):
                for sx in range(samples):
                    x = px + (sx + 0.5) * step
                    y = py + (sy + 0.5) * step
                    inside = rounded_rect_coverage(x, y, size, radius)
                    bg_cov += inside
                    if inside:
                        d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
                        if any(ring_coverage(d, r, w) for r, w, _, _ in rings):
                            ring_cov += 1.0
                        if ring_coverage(d, inner[0], inner[1]) or abs(x - cx) <= meridian_w / 2:
                            gold_cov += 1.0
            total = samples * samples
            bg_a, ring_a, gold_a = bg_cov / total, ring_cov / total, gold_cov / total
            if bg_a == 0:
                row.append((0, 0, 0, 0))
                continue
            colour = over(BLACK, VIOLET, rings[0][3] * ring_a)
            colour = over(colour, GOLD, inner[3] * gold_a)
            row.append((*colour, round(bg_a * 255)))
        rows.append(row)
    return rows


def render_og(width: int = 1200, height: int = 630, samples: int = 2):
    cx, cy = width / 2, height / 2
    rows = []
    step = 1.0 / samples
    for py in range(height):
        row = []
        for px in range(width):
            glow = 0.0
            ring = 0.0
            gold = 0.0
            for sy in range(samples):
                for sx in range(samples):
                    x = px + (sx + 0.5) * step
                    y = py + (sy + 0.5) * step
                    dx, dy = x - cx, y - cy
                    d = (dx * dx + dy * dy) ** 0.5
                    glow += max(0.0, 1 - d / (width * 0.55))
                    if ring_coverage(d, height * 0.42, 14) or ring_coverage(d, height * 0.29, 14):
                        ring += 1.0
                    if ring_coverage(d, height * 0.155, 14) or (
                        abs(dx) <= 7 and abs(dy) <= height * 0.45
                    ):
                        gold += 1.0
            total = samples * samples
            colour = over(BLACK, VIOLET, 0.16 * (glow / total))
            colour = over(colour, VIOLET, 0.55 * (ring / total))
            colour = over(colour, GOLD, 0.9 * (gold / total))
            row.append((*colour, 255))
        rows.append(row)
    return rows


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    targets = [
        (root / "favicon-32.png", 32, lambda: render_icon(32, samples=4)),
        (root / "apple-touch-icon.png", 180, lambda: render_icon(180, samples=2)),
        (root / "assets" / "og-card.png", 1200, render_og),
    ]
    for path, size, maker in targets:
        rows = maker()
        write_png(path, len(rows[0]), len(rows), rows)
        print(f"wrote {path.relative_to(root)} ({len(rows[0])}x{len(rows)})")


if __name__ == "__main__":
    main()
