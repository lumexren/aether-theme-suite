#!/usr/bin/env python3
"""Sync and validate Aether Theme Suite targets against palette/palette.json."""

from __future__ import annotations

import argparse
import configparser
import json
import re
import sys
import tomllib
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PALETTE_PATH = ROOT / "palette" / "palette.json"


def load_palette() -> dict:
    if not PALETTE_PATH.is_file():
        raise FileNotFoundError(f"Missing {PALETTE_PATH}")
    with PALETTE_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def hex_to_rgb_csv(hex_color: str) -> str:
    h = hex_color.lstrip("#")
    return f"{int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)}"


def render_konsole(pal: dict) -> str:
    c = pal["colors"]
    ansi = pal["ansi"]
    pairs = [
        ("Background", c["base"]["hex"]),
        ("BackgroundFaint", c["surface0"]["hex"]),
        ("BackgroundIntense", c["crust"]["hex"]),
        ("Color0", ansi["normal"]["black"]),
        ("Color0Faint", ansi["dim"]["black"]),
        ("Color0Intense", ansi["bright"]["black"]),
        ("Color1", ansi["normal"]["red"]),
        ("Color1Faint", ansi["dim"]["red"]),
        ("Color1Intense", ansi["bright"]["red"]),
        ("Color2", ansi["normal"]["green"]),
        ("Color2Faint", ansi["dim"]["green"]),
        ("Color2Intense", ansi["bright"]["green"]),
        ("Color3", ansi["normal"]["yellow"]),
        ("Color3Faint", ansi["dim"]["yellow"]),
        ("Color3Intense", ansi["bright"]["yellow"]),
        ("Color4", ansi["normal"]["blue"]),
        ("Color4Faint", ansi["dim"]["blue"]),
        ("Color4Intense", ansi["bright"]["blue"]),
        ("Color5", ansi["normal"]["magenta"]),
        ("Color5Faint", ansi["dim"]["magenta"]),
        ("Color5Intense", ansi["bright"]["magenta"]),
        ("Color6", ansi["normal"]["cyan"]),
        ("Color6Faint", ansi["dim"]["cyan"]),
        ("Color6Intense", ansi["bright"]["cyan"]),
        ("Color7", ansi["normal"]["white"]),
        ("Color7Faint", ansi["dim"]["white"]),
        ("Color7Intense", ansi["bright"]["white"]),
        ("Foreground", c["textBright"]["hex"]),
        ("ForegroundFaint", c["text"]["hex"]),
        ("ForegroundIntense", c["white"]["hex"]),
    ]
    lines = []
    for section, color in pairs:
        lines.append(f"[{section}]")
        lines.append(f"Color={hex_to_rgb_csv(color)}")
        lines.append("")
    lines.extend(
        [
            "[General]",
            "Anchor=0.5,0.5",
            "Blur=true",
            "ColorRandomization=false",
            "Description=Aether Dark",
            "FillStyle=Tile",
            "Opacity=0.85",
            "Wallpaper=",
            "WallpaperOpacity=1",
        ]
    )
    return "\n".join(lines) + "\n"


def render_btop(pal: dict) -> str:
    c = pal["colors"]
    base = c["base"]["hex"]
    surface0 = c["surface0"]["hex"]
    overlay0 = c["overlay0"]["hex"]
    text_bright = c["textBright"]["hex"]
    white = c["white"]["hex"]
    comment = c["comment"]["hex"]
    blue = c["blue"]["hex"]
    cyan = c["cyan"]["hex"]
    teal = c["teal"]["hex"]
    red = c["red"]["hex"]

    return f"""# Theme: Aether Dark
# Deep Obsidian ({base}) with Electric Royal Blue ({blue}) & Cyan ({cyan})

# Main bg
theme[main_bg]="{base}"

# Main text color
theme[main_fg]="{text_bright}"

# Title color for boxes
theme[title]="{blue}"

# Highlight color for keyboard shortcuts
theme[hi_fg]="{cyan}"

# Background color of selected item in processes box
theme[selected_bg]="{surface0}"

# Foreground color of selected item in processes box
theme[selected_fg]="{white}"

# Color of inactive/disabled text
theme[inactive_fg]="{comment}"

# Misc colors for processes box
theme[proc_misc]="{cyan}"

# Box outline colors
theme[cpu_box]="{overlay0}"
theme[mem_box]="{overlay0}"
theme[net_box]="{overlay0}"
theme[proc_box]="{overlay0}"

# Box divider line
theme[div_line]="{overlay0}"

# Temperature graph colors
theme[temp_start]="{teal}"
theme[temp_mid]="{blue}"
theme[temp_end]="{red}"

# CPU graph colors
theme[cpu_start]="{blue}"
theme[cpu_mid]="{cyan}"
theme[cpu_end]="{red}"

# Mem/Disk free meter
theme[free_start]="{teal}"
theme[free_mid]="{blue}"
theme[free_end]="{red}"

# Mem/Disk cached meter
theme[cached_start]="{cyan}"
theme[cached_mid]="{blue}"
theme[cached_end]="{red}"

# Mem/Disk available meter
theme[available_start]="{teal}"
theme[available_mid]="{blue}"
theme[available_end]="{red}"

# Mem/Disk used meter
theme[used_start]="{blue}"
theme[used_mid]="{cyan}"
theme[used_end]="{red}"

# Download graph colors
theme[download_start]="{cyan}"
theme[download_mid]="{blue}"
theme[download_end]="{red}"

# Upload graph colors
theme[upload_start]="{blue}"
theme[upload_mid]="{cyan}"
theme[upload_end]="{red}"

# Process box gradient colors
theme[process_start]="{blue}"
theme[process_mid]="{cyan}"
theme[process_end]="{red}"
"""


def render_tmtheme(pal: dict) -> str:
    c = pal["colors"]
    syn = pal["semantic"]["syntax"]
    s = lambda k: c[syn[k]]["hex"]

    rules = [
        ("Comments", "comment, punctuation.definition.comment", s("comment"), None, "italic"),
        ("Doc Comments", "comment.block.documentation, comment.line.documentation", s("docComment"), None, "italic"),
        ("Strings", "string, string.quoted, punctuation.definition.string", s("string"), None, None),
        ("String Escape &amp; Regexp", "constant.character.escape, string.regexp", s("stringEscape"), None, None),
        (
            "Numbers &amp; Constants",
            "constant.numeric, constant.language, constant.character, support.constant, variable.other.constant",
            s("number"),
            None,
            None,
        ),
        ("Keywords &amp; Storage", "keyword, keyword.control, storage.type, storage.modifier", s("keyword"), None, None),
        ("Operators &amp; Accessors", "keyword.operator, punctuation.accessor", s("operator"), None, None),
        ("Functions &amp; Methods", "entity.name.function, meta.function-call, support.function", s("function"), None, None),
        (
            "Classes, Types &amp; Interfaces",
            "entity.name.type, entity.name.class, entity.other.inherited-class, support.type, support.class",
            s("type"),
            None,
            None,
        ),
        ("Variables &amp; Parameters", "variable, variable.other.readwrite, variable.parameter", s("variable"), None, None),
        (
            "Properties, Fields &amp; Tags",
            "variable.other.property, variable.other.object.property, variable.language, support.variable.property, entity.name.tag",
            s("property"),
            None,
            None,
        ),
        ("Attributes", "entity.other.attribute-name", s("constant"), None, None),
        ("CSS Properties", "support.type.property-name.css, support.type.property-name.scss", s("operator"), None, None),
        ("JSON / YAML / TOML Keys", "support.type.property-name.json, entity.name.tag.yaml, keyword.key.toml", s("property"), None, None),
        ("Markdown Headings", "markup.heading, entity.name.section", s("function"), None, "bold"),
        ("Markdown Bold", "markup.bold", s("constant"), None, "bold"),
        ("Markdown Italic", "markup.italic", s("keyword"), None, "italic"),
        ("Markdown Inline Code", "markup.inline.raw", s("string"), None, None),
        ("Diff Inserted", "markup.inserted", c["teal"]["hex"], None, None),
        ("Diff Deleted", "markup.deleted", c["red"]["hex"], None, None),
        ("Diff Changed", "markup.changed", c["cyan"]["hex"], None, None),
        ("Punctuation &amp; Brackets", "punctuation.separator, punctuation.terminator, meta.brace", s("punctuation"), None, None),
        ("Invalid", "invalid, invalid.illegal", c["white"]["hex"], c["red"]["hex"], None),
    ]

    rule_blocks = []
    for name, scope, fg, bg, font_style in rules:
        settings = [f"        <key>foreground</key>\n        <string>{fg}</string>"]
        if bg:
            settings.append(f"        <key>background</key>\n        <string>{bg}</string>")
        if font_style:
            settings.append(f"        <key>fontStyle</key>\n        <string>{font_style}</string>")
        rule_blocks.append(
            f"""    <dict>
      <key>name</key>
      <string>{name}</string>
      <key>scope</key>
      <string>{scope}</string>
      <key>settings</key>
      <dict>
{chr(10).join(settings)}
      </dict>
    </dict>"""
        )

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>name</key>
  <string>Aether Dark</string>
  <key>author</key>
  <string>{pal["author"]}</string>
  <key>semanticClass</key>
  <string>theme.dark.aether</string>
  <key>colorSpaceName</key>
  <string>sRGB</string>
  <key>settings</key>
  <array>
    <dict>
      <key>settings</key>
      <dict>
        <key>background</key>
        <string>{c["base"]["hex"]}</string>
        <key>foreground</key>
        <string>{c["text"]["hex"]}</string>
        <key>caret</key>
        <string>{c["blue"]["hex"]}</string>
        <key>lineHighlight</key>
        <string>{c["surface1"]["hex"]}</string>
        <key>selection</key>
        <string>{pal["semantic"]["accent"]["selectionBgAlpha"]}</string>
        <key>selectionBorder</key>
        <string>{c["blue"]["hex"]}</string>
        <key>findHighlight</key>
        <string>{c["cyan"]["hex"]}</string>
        <key>findHighlightForeground</key>
        <string>{c["base"]["hex"]}</string>
        <key>gutter</key>
        <string>{c["base"]["hex"]}</string>
        <key>gutterForeground</key>
        <string>{c["comment"]["hex"]}</string>
        <key>guide</key>
        <string>{c["overlay0"]["hex"]}</string>
        <key>activeGuide</key>
        <string>{c["blue"]["hex"]}</string>
      </dict>
    </dict>
{chr(10).join(rule_blocks)}
  </array>
</dict>
</plist>
"""


def sync_or_check_file(path: Path, expected: str, write: bool, errors: list[str]) -> None:
    current = path.read_text(encoding="utf-8") if path.is_file() else None
    if current != expected:
        if write:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(expected, encoding="utf-8")
            print(f"updated: {path.relative_to(ROOT)}")
        else:
            errors.append(f"{path.relative_to(ROOT)} is out of sync with palette.json")


def validate_repo(pal: dict, write: bool) -> list[str]:
    errors: list[str] = []
    c = pal["colors"]
    known_hexes = {v["hex"].lower() for v in c.values()}

    # 1. Generated/synced files
    sync_or_check_file(ROOT / "konsole" / "Aether.colorscheme", render_konsole(pal), write, errors)
    sync_or_check_file(ROOT / "btop" / "aether.theme", render_btop(pal), write, errors)
    sync_or_check_file(ROOT / "bat" / "themes" / "Aether Dark.tmTheme", render_tmtheme(pal), write, errors)

    # 2. Starship TOML validation & hex check
    starship_path = ROOT / "starship" / "starship.toml"
    with starship_path.open("rb") as f:
        tomllib.load(f)
    for hx in set(re.findall(r"#[0-9a-fA-F]{6}", starship_path.read_text(encoding="utf-8"))):
        if hx.lower() not in known_hexes:
            errors.append(f"starship/starship.toml uses non-palette color {hx}")

    # 3. Fontconfig XML & tmTheme XML validation
    for xml_path in [
        ROOT / "fontconfig" / "fonts.conf",
        ROOT / "fontconfig" / "local.conf",
        ROOT / "bat" / "themes" / "Aether Dark.tmTheme",
    ]:
        try:
            ET.parse(xml_path)
        except ET.ParseError as exc:
            errors.append(f"Invalid XML in {xml_path.relative_to(ROOT)}: {exc}")

    # 4. Plasma metadata JSON & desktoptheme/colorscheme checks
    for meta_path in [
        ROOT / "plasma" / "look-and-feel" / "Aether" / "metadata.json",
        ROOT / "plasma" / "desktoptheme" / "Aether" / "metadata.json",
        ROOT / "plasma" / "aurorae" / "Aether" / "metadata.json",
        ROOT / "plasma" / "wallpaper" / "Aether" / "metadata.json",
    ]:
        with meta_path.open("r", encoding="utf-8") as f:
            meta = json.load(f)
        if meta_path.parent.name == "Aether" and meta_path.parent.parent.name in {
            "look-and-feel",
            "desktoptheme",
            "aurorae",
        }:
            if "KPackageStructure" not in meta:
                errors.append(f"{meta_path.relative_to(ROOT)} missing KPackageStructure")

    for kde_colors in [
        ROOT / "plasma" / "color-schemes" / "Aether.colors",
        ROOT / "plasma" / "desktoptheme" / "Aether" / "colors",
    ]:
        cp = configparser.ConfigParser(interpolation=None)
        cp.optionxform = str
        cp.read(kde_colors, encoding="utf-8")
        if cp.get("Colors:Window", "BackgroundNormal", fallback="") != hex_to_rgb_csv(c["base"]["hex"]):
            errors.append(f"{kde_colors.relative_to(ROOT)} Window.BackgroundNormal != base")
        if cp.get("Colors:Window", "ForegroundNormal", fallback="") != hex_to_rgb_csv(c["textBright"]["hex"]):
            errors.append(f"{kde_colors.relative_to(ROOT)} Window.ForegroundNormal != textBright")
        if cp.get("Colors:Selection", "BackgroundNormal", fallback="") != hex_to_rgb_csv(c["blue"]["hex"]):
            errors.append(f"{kde_colors.relative_to(ROOT)} Selection.BackgroundNormal != blue")

    # 5. Kvantum GeneralColors check
    kv_text = (ROOT / "plasma" / "kvantum" / "Aether" / "Aether.kvconfig").read_text(encoding="utf-8")
    for legacy in ("#edf0f2", "#eefcff", "#556064", "#47535a"):
        if legacy in kv_text.lower():
            errors.append(f"plasma/kvantum/Aether/Aether.kvconfig still contains legacy color {legacy}")

    # 6. GTK tokens check
    gtk_css = (ROOT / "gtk" / "gtk.css").read_text(encoding="utf-8")
    for token, pal_key in [
        ("accent_color", "blue"),
        ("window_bg_color", "base"),
        ("window_fg_color", "textBright"),
        ("headerbar_bg_color", "surface0"),
        ("destructive_color", "red"),
        ("success_color", "teal"),
    ]:
        expected_line = f"@define-color {token} {c[pal_key]['hex']};"
        if expected_line not in gtk_css:
            errors.append(f"gtk/gtk.css missing '{expected_line}'")

    # 7. Zed & VS Code JSON validation & key palette checks
    zed_path = ROOT / "zed" / "aether.json"
    with zed_path.open("r", encoding="utf-8") as f:
        zed = json.load(f)
    zed_style = zed["themes"][0]["style"]
    for key, pal_key in [
        ("background", "base"),
        ("surface.background", "surface0"),
        ("border", "overlay0"),
        ("text", "text"),
        ("text.accent", "blue"),
        ("error", "red"),
        ("created", "teal"),
        ("warning", "yellow"),
    ]:
        if zed_style.get(key) != c[pal_key]["hex"]:
            errors.append(f"zed/aether.json style['{key}'] != {c[pal_key]['hex']}")

    vsc_ext = ROOT / "vscode" / "aether-dark-extension"
    vsc_pkg = json.loads((vsc_ext / "package.json").read_text(encoding="utf-8"))
    vsc_theme = json.loads((vsc_ext / "themes" / "aether-dark-color-theme.json").read_text(encoding="utf-8"))
    if vsc_theme["colors"].get("editor.background") != c["base"]["hex"]:
        errors.append("VS Code editor.background != base")
    if vsc_theme["colors"].get("focusBorder") != c["blue"]["hex"]:
        errors.append("VS Code focusBorder != blue")

    # 8. VSIX matches source extension
    vsix_path = ROOT / "vscode" / f"{vsc_pkg['name']}-{vsc_pkg['version']}.vsix"
    if not vsix_path.is_file():
        errors.append(f"Missing packaged VSIX: {vsix_path.relative_to(ROOT)}")
    else:
        with zipfile.ZipFile(vsix_path, "r") as zf:
            for rel in ["package.json", "README.md", "icon.png", "themes/aether-dark-color-theme.json"]:
                arc_name = f"extension/{rel}"
                if arc_name not in zf.namelist():
                    errors.append(f"{vsix_path.name} missing {arc_name}")
                elif zf.read(arc_name) != (vsc_ext / rel).read_bytes():
                    errors.append(f"{vsix_path.name}:{arc_name} differs from source (run scripts/package-vscode.sh)")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="Verify all files match palette.json (default)")
    mode.add_argument("--write", action="store_true", help="Regenerate palette-derived files")
    args = parser.parse_args()

    pal = load_palette()
    errors = validate_repo(pal, write=args.write)
    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        return 1

    print("All Aether theme targets are valid and in sync with palette/palette.json.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
