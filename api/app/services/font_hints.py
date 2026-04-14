"""Font hints — maps well-known courses to suggested fonts."""
from __future__ import annotations

COURSE_FONTS = {
    "pebble beach": "Playfair Display",
    "augusta national": "Cormorant Garamond",
    "st andrews": "EB Garamond",
    "pinehurst": "Libre Baskerville",
    "bethpage": "Oswald",
    "torrey pines": "Montserrat",
    "sawgrass": "Lora",
    "whistling straits": "Merriweather",
    "kiawah island": "Raleway",
    "bandon dunes": "Source Serif Pro",
    "chambers bay": "Roboto Slab",
    "shinnecock hills": "Playfair Display",
    "oakmont": "Crimson Text",
    "winged foot": "Cormorant Garamond",
    "merion": "EB Garamond",
}


def get_font_hint(course_name: str) -> str | None:
    """Get a font suggestion for a course name.

    Returns None if no font hint is available.
    """
    if not course_name:
        return None
    normalized = course_name.strip().lower()
    # Check exact match first
    if normalized in COURSE_FONTS:
        return COURSE_FONTS[normalized]
    # Check partial match
    for key, font in COURSE_FONTS.items():
        if key in normalized or normalized in key:
            return font
    return None
