"""Generate SVG path data for font glyphs.

One-time script: extracts glyph outlines from a TTF font using fonttools and
writes them as a Python module suitable for embedding in the renderer.

Usage:
    python scripts/generate_glyphs.py /path/to/Font.ttf > app/services/render/glyphs.py
"""
from __future__ import annotations

import sys
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen


CHARS_NEEDED = (
    "0123456789+-. &"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz"
)


def extract_glyphs(font_path: str) -> dict:
    font = TTFont(font_path)
    glyf = font["glyf"]
    cmap = font.getBestCmap()
    glyph_set = font.getGlyphSet()

    # Font metrics
    units_per_em = font["head"].unitsPerEm
    ascent = font["OS/2"].sTypoAscender
    descent = font["OS/2"].sTypoDescender

    glyphs = {}
    advances = {}

    for char in CHARS_NEEDED:
        code = ord(char)
        if code not in cmap:
            continue
        glyph_name = cmap[code]

        pen = SVGPathPen(glyph_set)
        glyph_set[glyph_name].draw(pen)
        path_d = pen.getCommands()

        # Get advance width
        if glyph_name in glyf and hasattr(glyf[glyph_name], "numberOfContours"):
            width = glyph_set[glyph_name].width
        else:
            width = glyph_set[glyph_name].width

        if path_d:  # skip empty glyphs (like space)
            glyphs[char] = path_d
        advances[char] = width

    return {
        "glyphs": glyphs,
        "advances": advances,
        "units_per_em": units_per_em,
        "ascent": ascent,
        "descent": descent,
    }


def format_output(data: dict) -> str:
    lines = [
        '"""Pre-generated SVG glyph paths for Cricut text-to-path conversion.',
        '',
        'Generated from a TTF font by scripts/generate_glyphs.py.',
        'Each glyph is an SVG path `d` attribute in the font\'s coordinate system',
        '(units_per_em). Y-axis points UP in font coordinates; the renderer must',
        'flip Y when converting to SVG (where Y points DOWN).',
        '"""',
        'from __future__ import annotations',
        '',
        f'UNITS_PER_EM = {data["units_per_em"]}',
        f'ASCENT = {data["ascent"]}',
        f'DESCENT = {data["descent"]}',
        '',
        '# SVG path d-strings per character (font coordinate system, Y-up)',
        'GLYPH_PATHS: dict[str, str] = {',
    ]
    for char, path in sorted(data["glyphs"].items()):
        escaped = repr(char)
        lines.append(f'    {escaped}: "{path}",')
    lines.append('}')
    lines.append('')
    lines.append('# Advance widths per character (in font units)')
    lines.append('GLYPH_ADVANCES: dict[str, int] = {')
    for char, adv in sorted(data["advances"].items()):
        escaped = repr(char)
        lines.append(f'    {escaped}: {adv},')
    lines.append('}')
    lines.append('')
    return '\n'.join(lines)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_glyphs.py <font.ttf>", file=sys.stderr)
        sys.exit(1)
    data = extract_glyphs(sys.argv[1])
    print(format_output(data))
