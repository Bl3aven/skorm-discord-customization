#!/usr/bin/env python3
"""Build standalone BetterDiscord theme files from the shared SKORM core."""

from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "Bl3aven/skorm-discord-customization"
REPOSITORY_URL = f"https://github.com/{REPOSITORY}"
RAW_BASE = f"https://raw.githubusercontent.com/{REPOSITORY}/main"
LIVE_BASE = "https://skormdemo.tournayre.ovh/theme-live"
VERSION = "2.0.0"

FIXED_THEMES = {
    "SkormCyberpunk.theme.css": (
        "SkormCyberpunk",
        "Cyberpunk",
        "Neon magenta and cyan SKORM theme.",
        "cyberpunk",
    ),
    "SkormGalaxy.theme.css": (
        "SkormGalaxy",
        "Galaxy",
        "Violet deep-space SKORM theme.",
        "galaxy",
    ),
    "SkormGreek.theme.css": (
        "SkormGreek",
        "Greek",
        "Marble and Olympian-gold SKORM theme.",
        "greek",
    ),
    "SkormHell.theme.css": (
        "SkormHell",
        "Hell",
        "Obsidian, lava and ember SKORM theme.",
        "hell",
    ),
    "SkormTropical.theme.css": (
        "SkormTropical",
        "Tropical",
        "Dark emerald jungle SKORM theme.",
        "tropical",
    ),
}


def metadata(name: str, description: str, filename: str) -> str:
    return f"""/**
 * @name {name}
 * @author Bleaven
 * @description {description}
 * @version {VERSION}
 * @source {REPOSITORY_URL}/blob/main/{filename}
 * @website {REPOSITORY_URL}
 */
"""


def root_assets(background_url: str, logo_url: str) -> str:
    return f"""
:root {{
    --skorm-image: url("{background_url}");
    --skorm-server-icon: url("{logo_url}");
}}
"""


def render_fixed(
    filename: str,
    addon_name: str,
    display_name: str,
    description: str,
    slug: str,
    core: str,
) -> str:
    del display_name
    palette = (ROOT / "assets" / "palettes" / f"{slug}.css").read_text(
        encoding="utf-8"
    ).strip()
    assets = root_assets(
        f"{RAW_BASE}/assets/backgrounds/{slug}.png",
        f"{RAW_BASE}/assets/logos/{slug}.webp",
    )
    return (
        metadata(addon_name, description, filename)
        + "\n/* Generated as standalone CSS: remote CSS imports are intentionally avoided. */\n"
        + palette
        + "\n"
        + assets
        + "\n"
        + core.strip()
        + "\n"
    )


def render_dynamic(filename: str, addon_name: str, core: str, palette: str) -> str:
    background_url = f"{LIVE_BASE}/background.png"
    logo_url = f"{LIVE_BASE}/logo.webp"
    assets = root_assets(background_url, logo_url)
    description = (
        "Live SKORM theme synchronized from Nextcloud by SkormThemeSync."
        if addon_name == "SkormDynamic"
        else "Legacy live SKORM theme; use with SkormThemeSync for instant updates."
    )
    return (
        metadata(addon_name, description, filename)
        + "\n/* Generated as standalone CSS: remote CSS imports are intentionally avoided. */\n"
        + palette.strip()
        + "\n"
        + assets
        + "\n"
        + core.strip()
        + "\n"
    )


def expected_files() -> dict[Path, str]:
    core = (ROOT / "SkormCore.css").read_text(encoding="utf-8")
    active_palette = (ROOT / "assets" / "active-palette.css").read_text(
        encoding="utf-8"
    )
    output: dict[Path, str] = {}
    for filename, values in FIXED_THEMES.items():
        output[ROOT / filename] = render_fixed(filename, *values, core)
    output[ROOT / "SkormDynamic.theme.css"] = render_dynamic(
        "SkormDynamic.theme.css",
        "SkormDynamic",
        core,
        active_palette,
    )
    output[ROOT / "TropicalSkorm.theme.css"] = render_dynamic(
        "TropicalSkorm.theme.css",
        "TropicalSkorm",
        core,
        active_palette,
    )
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if generated theme files are not current.",
    )
    args = parser.parse_args()

    stale: list[str] = []
    for path, content in expected_files().items():
        if path.exists() and path.read_text(encoding="utf-8") == content:
            continue
        if args.check:
            stale.append(path.name)
        else:
            path.write_text(content, encoding="utf-8", newline="\n")
            print(f"generated {path.name}")

    if stale:
        print("stale generated themes: " + ", ".join(stale))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
