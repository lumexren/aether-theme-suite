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


def ansi_list(pal: dict) -> list[str]:
    n = pal["ansi"]["normal"]
    b = pal["ansi"]["bright"]
    order = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]
    return [n[k] for k in order] + [b[k] for k in order]


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


def render_ghostty(pal: dict) -> str:
    c = pal["colors"]
    colors = ansi_list(pal)
    lines = [
        "# Aether Dark — Ghostty Theme",
        f"background = {c['base']['hex']}",
        f"foreground = {c['textBright']['hex']}",
        f"cursor-color = {c['blue']['hex']}",
        f"cursor-text = {c['base']['hex']}",
        f"selection-background = {c['blue']['hex']}",
        f"selection-foreground = {c['white']['hex']}",
    ]
    for idx, hx in enumerate(colors):
        lines.append(f"palette = {idx}={hx}")
    return "\n".join(lines) + "\n"


def render_kitty(pal: dict) -> str:
    c = pal["colors"]
    colors = ansi_list(pal)
    lines = [
        "# vim:ft=kitty",
        "# Aether Dark — Kitty Theme",
        "",
        f"foreground              {c['textBright']['hex']}",
        f"background              {c['base']['hex']}",
        f"selection_foreground    {c['white']['hex']}",
        f"selection_background    {c['blue']['hex']}",
        "",
        f"cursor                  {c['blue']['hex']}",
        f"cursor_text_color       {c['base']['hex']}",
        "",
        f"url_color               {c['cyan']['hex']}",
        "",
        f"active_border_color     {c['blue']['hex']}",
        f"inactive_border_color   {c['overlay0']['hex']}",
        f"bell_border_color       {c['red']['hex']}",
        "",
        f"active_tab_foreground   {c['white']['hex']}",
        f"active_tab_background   {c['blue']['hex']}",
        f"inactive_tab_foreground {c['subtext1']['hex']}",
        f"inactive_tab_background {c['surface0']['hex']}",
        f"tab_bar_background      {c['mantle']['hex']}",
        "",
        f"mark1_foreground        {c['base']['hex']}",
        f"mark1_background        {c['blue']['hex']}",
        f"mark2_foreground        {c['base']['hex']}",
        f"mark2_background        {c['cyan']['hex']}",
        f"mark3_foreground        {c['base']['hex']}",
        f"mark3_background        {c['purple']['hex']}",
        "",
    ]
    for idx, hx in enumerate(colors):
        lines.append(f"color{idx:<18} {hx}")
    return "\n".join(lines) + "\n"


def render_alacritty(pal: dict) -> str:
    c = pal["colors"]
    n = pal["ansi"]["normal"]
    b = pal["ansi"]["bright"]
    d = pal["ansi"]["dim"]
    return f"""# Aether Dark — Alacritty Theme

[colors.primary]
background = "{c['base']['hex']}"
foreground = "{c['textBright']['hex']}"
dim_foreground = "{c['subtext2']['hex']}"
bright_foreground = "{c['white']['hex']}"

[colors.cursor]
text = "{c['base']['hex']}"
cursor = "{c['blue']['hex']}"

[colors.vi_mode_cursor]
text = "{c['base']['hex']}"
cursor = "{c['cyan']['hex']}"

[colors.selection]
text = "{c['white']['hex']}"
background = "{c['blue']['hex']}"

[colors.search.matches]
foreground = "{c['base']['hex']}"
background = "{c['cyan']['hex']}"

[colors.search.focused_match]
foreground = "{c['white']['hex']}"
background = "{c['blue']['hex']}"

[colors.footer_bar]
background = "{c['mantle']['hex']}"
foreground = "{c['text']['hex']}"

[colors.normal]
black = "{n['black']}"
red = "{n['red']}"
green = "{n['green']}"
yellow = "{n['yellow']}"
blue = "{n['blue']}"
magenta = "{n['magenta']}"
cyan = "{n['cyan']}"
white = "{n['white']}"

[colors.bright]
black = "{b['black']}"
red = "{b['red']}"
green = "{b['green']}"
yellow = "{b['yellow']}"
blue = "{b['blue']}"
magenta = "{b['magenta']}"
cyan = "{b['cyan']}"
white = "{b['white']}"

[colors.dim]
black = "{d['black']}"
red = "{d['red']}"
green = "{d['green']}"
yellow = "{d['yellow']}"
blue = "{d['blue']}"
magenta = "{d['magenta']}"
cyan = "{d['cyan']}"
white = "{d['white']}"
"""


def render_wezterm(pal: dict) -> str:
    c = pal["colors"]
    n = pal["ansi"]["normal"]
    b = pal["ansi"]["bright"]
    order = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]
    ansi_arr = ", ".join(f'"{n[k]}"' for k in order)
    bright_arr = ", ".join(f'"{b[k]}"' for k in order)
    return f"""# Aether Dark — WezTerm Color Scheme

[metadata]
name = "Aether Dark"
author = "{pal['author']}"

[colors]
foreground = "{c['textBright']['hex']}"
background = "{c['base']['hex']}"
cursor_bg = "{c['blue']['hex']}"
cursor_fg = "{c['base']['hex']}"
cursor_border = "{c['blue']['hex']}"
selection_fg = "{c['white']['hex']}"
selection_bg = "{c['blue']['hex']}"
scrollbar_thumb = "{c['overlay1']['hex']}"
split = "{c['overlay0']['hex']}"

ansi = [{ansi_arr}]
brights = [{bright_arr}]

[colors.tab_bar]
background = "{c['mantle']['hex']}"

[colors.tab_bar.active_tab]
bg_color = "{c['blue']['hex']}"
fg_color = "{c['white']['hex']}"

[colors.tab_bar.inactive_tab]
bg_color = "{c['surface0']['hex']}"
fg_color = "{c['subtext1']['hex']}"

[colors.tab_bar.inactive_tab_hover]
bg_color = "{c['overlay0']['hex']}"
fg_color = "{c['textBright']['hex']}"

[colors.tab_bar.new_tab]
bg_color = "{c['mantle']['hex']}"
fg_color = "{c['subtext1']['hex']}"

[colors.tab_bar.new_tab_hover]
bg_color = "{c['overlay0']['hex']}"
fg_color = "{c['cyan']['hex']}"
"""


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


def render_eza(pal: dict) -> str:
    c = pal["colors"]
    return f"""# Aether Dark — eza theme
colourful: true

filekinds:
  normal: {{ foreground: "{c['text']['hex']}" }}
  directory: {{ foreground: "{c['blue']['hex']}", is_bold: true }}
  symlink: {{ foreground: "{c['cyan']['hex']}" }}
  pipe: {{ foreground: "{c['comment']['hex']}" }}
  block_device: {{ foreground: "{c['yellow']['hex']}" }}
  char_device: {{ foreground: "{c['yellow']['hex']}" }}
  socket: {{ foreground: "{c['purple']['hex']}" }}
  special: {{ foreground: "{c['purple']['hex']}" }}
  executable: {{ foreground: "{c['teal']['hex']}", is_bold: true }}
  mount_point: {{ foreground: "{c['cyanBright']['hex']}", is_bold: true }}

perms:
  user_read: {{ foreground: "{c['text']['hex']}" }}
  user_write: {{ foreground: "{c['peach']['hex']}" }}
  user_execute_file: {{ foreground: "{c['teal']['hex']}" }}
  user_execute_other: {{ foreground: "{c['teal']['hex']}" }}
  user_sticky: {{ foreground: "{c['purple']['hex']}" }}
  user_setuid: {{ foreground: "{c['red']['hex']}" }}
  user_setgid: {{ foreground: "{c['red']['hex']}" }}
  group_read: {{ foreground: "{c['subtext1']['hex']}" }}
  group_write: {{ foreground: "{c['peach']['hex']}" }}
  group_execute: {{ foreground: "{c['teal']['hex']}" }}
  other_read: {{ foreground: "{c['comment']['hex']}" }}
  other_write: {{ foreground: "{c['red']['hex']}" }}
  other_execute: {{ foreground: "{c['tealDim']['hex']}" }}
  special_user_file: {{ foreground: "{c['purple']['hex']}" }}
  special_other: {{ foreground: "{c['comment']['hex']}" }}
  attribute: {{ foreground: "{c['subtext0']['hex']}" }}

size:
  major: {{ foreground: "{c['comment']['hex']}" }}
  minor: {{ foreground: "{c['cyan']['hex']}" }}
  number_byte: {{ foreground: "{c['text']['hex']}" }}
  number_kilo: {{ foreground: "{c['textBright']['hex']}" }}
  number_mega: {{ foreground: "{c['cyan']['hex']}" }}
  number_giga: {{ foreground: "{c['blue']['hex']}" }}
  number_huge: {{ foreground: "{c['purple']['hex']}" }}
  unit_byte: {{ foreground: "{c['subtext1']['hex']}" }}
  unit_kilo: {{ foreground: "{c['subtext1']['hex']}" }}
  unit_mega: {{ foreground: "{c['cyanDim']['hex']}" }}
  unit_giga: {{ foreground: "{c['blueDim']['hex']}" }}
  unit_huge: {{ foreground: "{c['purpleDim']['hex']}" }}

users:
  user_you: {{ foreground: "{c['blueBright']['hex']}", is_bold: true }}
  user_root: {{ foreground: "{c['red']['hex']}", is_bold: true }}
  user_other: {{ foreground: "{c['subtext1']['hex']}" }}
  group_yours: {{ foreground: "{c['cyan']['hex']}" }}
  group_other: {{ foreground: "{c['comment']['hex']}" }}
  group_root: {{ foreground: "{c['redDim']['hex']}" }}

links:
  normal: {{ foreground: "{c['subtext1']['hex']}" }}
  multi_link_file: {{ foreground: "{c['cyan']['hex']}" }}

git:
  new: {{ foreground: "{c['teal']['hex']}" }}
  modified: {{ foreground: "{c['cyan']['hex']}" }}
  deleted: {{ foreground: "{c['red']['hex']}" }}
  renamed: {{ foreground: "{c['blueBright']['hex']}" }}
  typechange: {{ foreground: "{c['purple']['hex']}" }}
  ignored: {{ foreground: "{c['comment']['hex']}" }}
  conflicted: {{ foreground: "{c['yellow']['hex']}", is_bold: true }}

git_repo:
  branch_main: {{ foreground: "{c['blue']['hex']}", is_bold: true }}
  branch_other: {{ foreground: "{c['cyan']['hex']}" }}
  git_clean: {{ foreground: "{c['teal']['hex']}" }}
  git_dirty: {{ foreground: "{c['red']['hex']}" }}

date: {{ foreground: "{c['subtext1']['hex']}" }}
punctuation: {{ foreground: "{c['overlay2']['hex']}" }}
"""


def render_lazygit(pal: dict) -> str:
    c = pal["colors"]
    return f"""# Aether Dark — Lazygit theme (include or merge into ~/.config/lazygit/config.yml)
gui:
  nerdFontsVersion: "3"
  border: rounded
  theme:
    activeBorderColor:
      - "{c['blue']['hex']}"
      - bold
    inactiveBorderColor:
      - "{c['overlay1']['hex']}"
    searchingActiveBorderColor:
      - "{c['cyan']['hex']}"
      - bold
    optionsTextColor:
      - "{c['cyan']['hex']}"
    selectedLineBgColor:
      - "{c['surface2']['hex']}"
    cherryPickedCommitBgColor:
      - "{c['diffAddBg']['hex']}"
    cherryPickedCommitFgColor:
      - "{c['cyanBright']['hex']}"
    markedBaseCommitBgColor:
      - "{c['diffWarnBg']['hex']}"
    markedBaseCommitFgColor:
      - "{c['yellow']['hex']}"
    unstagedChangesColor:
      - "{c['red']['hex']}"
    defaultFgColor:
      - "{c['text']['hex']}"
"""


def render_yazi(pal: dict) -> str:
    c = pal["colors"]
    return f"""# Aether Dark — Yazi theme

[mgr]
cwd = {{ fg = "{c['cyan']['hex']}" }}

hovered         = {{ fg = "{c['white']['hex']}", bg = "{c['blue']['hex']}", bold = true }}
preview_hovered = {{ underline = true }}

find_keyword  = {{ fg = "{c['yellow']['hex']}", bold = true, italic = true }}
find_position = {{ fg = "{c['purple']['hex']}", bg = "reset", bold = true }}

marker_copied   = {{ fg = "{c['teal']['hex']}", bg = "{c['teal']['hex']}" }}
marker_cut      = {{ fg = "{c['red']['hex']}", bg = "{c['red']['hex']}" }}
marker_marked   = {{ fg = "{c['cyan']['hex']}", bg = "{c['cyan']['hex']}" }}
marker_selected = {{ fg = "{c['blue']['hex']}", bg = "{c['blue']['hex']}" }}

count_copied   = {{ fg = "{c['base']['hex']}", bg = "{c['teal']['hex']}" }}
count_cut      = {{ fg = "{c['white']['hex']}", bg = "{c['red']['hex']}" }}
count_selected = {{ fg = "{c['white']['hex']}", bg = "{c['blue']['hex']}" }}

border_symbol = "│"
border_style  = {{ fg = "{c['overlay1']['hex']}" }}

[tabs]
active   = {{ fg = "{c['white']['hex']}", bg = "{c['blue']['hex']}", bold = true }}
inactive = {{ fg = "{c['subtext1']['hex']}", bg = "{c['surface0']['hex']}" }}

[mode]
normal_main = {{ fg = "{c['white']['hex']}", bg = "{c['blue']['hex']}", bold = true }}
normal_alt  = {{ fg = "{c['blueBright']['hex']}", bg = "{c['surface2']['hex']}" }}
select_main = {{ fg = "{c['base']['hex']}", bg = "{c['cyan']['hex']}", bold = true }}
select_alt  = {{ fg = "{c['cyan']['hex']}", bg = "{c['surface2']['hex']}" }}
unset_main  = {{ fg = "{c['white']['hex']}", bg = "{c['red']['hex']}", bold = true }}
unset_alt   = {{ fg = "{c['red']['hex']}", bg = "{c['surface2']['hex']}" }}

[status]
overall   = {{ fg = "{c['text']['hex']}", bg = "{c['mantle']['hex']}" }}
sep_left  = {{ open = "", close = "" }}
sep_right = {{ open = "", close = "" }}

progress_label  = {{ fg = "{c['white']['hex']}", bold = true }}
progress_normal = {{ fg = "{c['blue']['hex']}", bg = "{c['overlay0']['hex']}" }}
progress_error  = {{ fg = "{c['red']['hex']}", bg = "{c['overlay0']['hex']}" }}

perm_type  = {{ fg = "{c['blue']['hex']}" }}
perm_read  = {{ fg = "{c['yellow']['hex']}" }}
perm_write = {{ fg = "{c['red']['hex']}" }}
perm_exec  = {{ fg = "{c['teal']['hex']}" }}
perm_sep   = {{ fg = "{c['comment']['hex']}" }}

[which]
mask            = {{ bg = "{c['crust']['hex']}" }}
cand            = {{ fg = "{c['cyan']['hex']}" }}
rest            = {{ fg = "{c['comment']['hex']}" }}
desc            = {{ fg = "{c['text']['hex']}" }}
separator       = "  "
separator_style = {{ fg = "{c['overlay2']['hex']}" }}

[confirm]
border     = {{ fg = "{c['blue']['hex']}" }}
title      = {{ fg = "{c['cyan']['hex']}", bold = true }}
content    = {{ fg = "{c['textBright']['hex']}" }}
list       = {{ fg = "{c['text']['hex']}" }}
btn_yes    = {{ fg = "{c['white']['hex']}", bg = "{c['blue']['hex']}", bold = true }}
btn_no     = {{ fg = "{c['text']['hex']}", bg = "{c['surface2']['hex']}" }}
btn_labels = [ "  [Y]es  ", "  (N)o  " ]

[spot]
border   = {{ fg = "{c['blue']['hex']}" }}
title    = {{ fg = "{c['cyan']['hex']}", bold = true }}
tbl_col  = {{ fg = "{c['blueBright']['hex']}" }}
tbl_cell = {{ fg = "{c['white']['hex']}", bg = "{c['surface2']['hex']}" }}

[notify]
title_info  = {{ fg = "{c['blue']['hex']}" }}
title_warn  = {{ fg = "{c['yellow']['hex']}" }}
title_error = {{ fg = "{c['red']['hex']}" }}

[pick]
border   = {{ fg = "{c['blue']['hex']}" }}
active   = {{ fg = "{c['white']['hex']}", bg = "{c['blue']['hex']}", bold = true }}
inactive = {{ fg = "{c['text']['hex']}" }}

[input]
border   = {{ fg = "{c['blue']['hex']}" }}
title    = {{ fg = "{c['cyan']['hex']}" }}
value    = {{ fg = "{c['textBright']['hex']}" }}
selected = {{ reversed = true }}

[cmp]
border   = {{ fg = "{c['blue']['hex']}" }}
active   = {{ fg = "{c['white']['hex']}", bg = "{c['blue']['hex']}" }}
inactive = {{ fg = "{c['text']['hex']}" }}

[tasks]
border  = {{ fg = "{c['blue']['hex']}" }}
title   = {{ fg = "{c['cyan']['hex']}" }}
hovered = {{ fg = "{c['white']['hex']}", bg = "{c['surface2']['hex']}" }}

[help]
on      = {{ fg = "{c['cyan']['hex']}" }}
run     = {{ fg = "{c['purple']['hex']}" }}
desc    = {{ fg = "{c['text']['hex']}" }}
hovered = {{ bg = "{c['surface2']['hex']}", bold = true }}
footer  = {{ fg = "{c['subtext1']['hex']}", bg = "{c['mantle']['hex']}" }}

[filetype]
rules = [
  {{ mime = "image/*", fg = "{c['yellow']['hex']}" }},
  {{ mime = "{{audio,video}}/*", fg = "{c['purple']['hex']}" }},
  {{ mime = "application/{{zip,rar,7z*,tar,gzip,xz,zstd,bzip*}}", fg = "{c['red']['hex']}" }},
  {{ mime = "application/{{pdf,doc,rtf}}", fg = "{c['teal']['hex']}" }},
  {{ name = "*", is = "orphan", fg = "{c['red']['hex']}", bold = true }},
  {{ name = "*", is = "exec", fg = "{c['teal']['hex']}" }},
  {{ name = "*/", fg = "{c['blue']['hex']}", bold = true }},
  {{ name = "*", fg = "{c['text']['hex']}" }},
]
"""


def render_tmux(pal: dict) -> str:
    c = pal["colors"]
    return f"""# Aether Dark — Tmux theme
# Source from ~/.tmux.conf or ~/.config/tmux/tmux.conf:
#   source-file ~/.config/tmux/aether.conf

set -g status-position bottom
set -g status-style "bg={c['mantle']['hex']},fg={c['text']['hex']}"
set -g status-left-length 40
set -g status-right-length 80

set -g status-left "#[fg={c['white']['hex']},bg={c['blue']['hex']},bold] #S #[fg={c['blue']['hex']},bg={c['mantle']['hex']},nobold] "
set -g status-right "#[fg={c['subtext1']['hex']},bg={c['surface0']['hex']}] %Y-%m-%d %H:%M #[fg={c['white']['hex']},bg={c['cyan']['hex']},bold] #H "

setw -g window-status-format "#[fg={c['subtext1']['hex']},bg={c['surface0']['hex']}] #I:#W "
setw -g window-status-current-format "#[fg={c['white']['hex']},bg={c['blue']['hex']},bold] #I:#W "
setw -g window-status-separator " "
setw -g window-status-activity-style "fg={c['yellow']['hex']},bg={c['surface0']['hex']}"

set -g pane-border-style "fg={c['overlay0']['hex']}"
set -g pane-active-border-style "fg={c['blue']['hex']}"

set -g message-style "bg={c['surface2']['hex']},fg={c['textBright']['hex']}"
set -g message-command-style "bg={c['surface2']['hex']},fg={c['cyan']['hex']}"
set -g mode-style "bg={c['blue']['hex']},fg={c['white']['hex']},bold"

set -g display-panes-active-colour "{c['blue']['hex']}"
set -g display-panes-colour "{c['overlay2']['hex']}"
set -g clock-mode-colour "{c['cyan']['hex']}"
"""


def render_nvim_init(pal: dict) -> str:
    c = pal["colors"]
    colors = ansi_list(pal)
    term_lines = "\n".join(
        f'  vim.g.terminal_color_{i} = "{hx}"' for i, hx in enumerate(colors)
    )
    return f"""-- Aether Dark — Neovim colorscheme
local M = {{}}

M.palette = {{
  crust = "{c['crust']['hex']}",
  mantle = "{c['mantle']['hex']}",
  base = "{c['base']['hex']}",
  surface0 = "{c['surface0']['hex']}",
  surface1 = "{c['surface1']['hex']}",
  surface2 = "{c['surface2']['hex']}",
  overlay0 = "{c['overlay0']['hex']}",
  overlay1 = "{c['overlay1']['hex']}",
  overlay2 = "{c['overlay2']['hex']}",
  comment = "{c['comment']['hex']}",
  subtext0 = "{c['subtext0']['hex']}",
  subtext1 = "{c['subtext1']['hex']}",
  subtext2 = "{c['subtext2']['hex']}",
  text = "{c['text']['hex']}",
  text_bright = "{c['textBright']['hex']}",
  white = "{c['white']['hex']}",
  blue = "{c['blue']['hex']}",
  blue_bright = "{c['blueBright']['hex']}",
  blue_dim = "{c['blueDim']['hex']}",
  cyan = "{c['cyan']['hex']}",
  cyan_bright = "{c['cyanBright']['hex']}",
  teal = "{c['teal']['hex']}",
  red = "{c['red']['hex']}",
  yellow = "{c['yellow']['hex']}",
  peach = "{c['peach']['hex']}",
  purple = "{c['purple']['hex']}",
  diff_add = "{c['diffAddBg']['hex']}",
  diff_warn = "{c['diffWarnBg']['hex']}",
  diff_delete = "{c['diffDeleteBg']['hex']}",
}}

function M.setup()
  vim.cmd("hi clear")
  if vim.fn.exists("syntax_on") == 1 then
    vim.cmd("syntax reset")
  end
  vim.o.termguicolors = true
  vim.o.background = "dark"
  vim.g.colors_name = "aether"

  local p = M.palette
  local hl = function(group, opts)
    vim.api.nvim_set_hl(0, group, opts)
  end

  -- Editor UI
  hl("Normal", {{ fg = p.text, bg = p.base }})
  hl("NormalNC", {{ fg = p.text, bg = p.base }})
  hl("NormalFloat", {{ fg = p.text, bg = p.surface0 }})
  hl("FloatBorder", {{ fg = p.overlay1, bg = p.surface0 }})
  hl("FloatTitle", {{ fg = p.cyan, bg = p.surface0, bold = true }})
  hl("Cursor", {{ fg = p.base, bg = p.blue }})
  hl("CursorLine", {{ bg = p.surface1 }})
  hl("CursorColumn", {{ bg = p.surface1 }})
  hl("ColorColumn", {{ bg = p.surface0 }})
  hl("LineNr", {{ fg = p.comment }})
  hl("CursorLineNr", {{ fg = p.blue, bold = true }})
  hl("SignColumn", {{ fg = p.comment, bg = p.base }})
  hl("FoldColumn", {{ fg = p.comment, bg = p.base }})
  hl("Folded", {{ fg = p.subtext1, bg = p.surface0 }})
  hl("VertSplit", {{ fg = p.overlay0 }})
  hl("WinSeparator", {{ fg = p.overlay0 }})
  hl("StatusLine", {{ fg = p.text, bg = p.mantle }})
  hl("StatusLineNC", {{ fg = p.comment, bg = p.mantle }})
  hl("TabLine", {{ fg = p.subtext1, bg = p.surface0 }})
  hl("TabLineFill", {{ bg = p.mantle }})
  hl("TabLineSel", {{ fg = p.white, bg = p.blue, bold = true }})
  hl("Pmenu", {{ fg = p.text, bg = p.surface0 }})
  hl("PmenuSel", {{ fg = p.white, bg = p.blue, bold = true }})
  hl("PmenuSbar", {{ bg = p.surface1 }})
  hl("PmenuThumb", {{ bg = p.overlay1 }})
  hl("Visual", {{ bg = p.diff_add }})
  hl("Search", {{ fg = p.base, bg = p.cyan }})
  hl("IncSearch", {{ fg = p.white, bg = p.blue, bold = true }})
  hl("CurSearch", {{ fg = p.white, bg = p.blue, bold = true }})
  hl("MatchParen", {{ fg = p.cyan_bright, bg = p.overlay1, bold = true }})
  hl("NonText", {{ fg = p.overlay2 }})
  hl("Whitespace", {{ fg = p.overlay1 }})
  hl("SpecialKey", {{ fg = p.overlay2 }})
  hl("Directory", {{ fg = p.blue, bold = true }})
  hl("Title", {{ fg = p.blue, bold = true }})
  hl("ErrorMsg", {{ fg = p.red, bold = true }})
  hl("WarningMsg", {{ fg = p.yellow, bold = true }})
  hl("MoreMsg", {{ fg = p.teal }})
  hl("Question", {{ fg = p.cyan }})

  -- Diff
  hl("DiffAdd", {{ bg = p.diff_add }})
  hl("DiffChange", {{ bg = p.diff_warn }})
  hl("DiffDelete", {{ fg = p.red, bg = p.diff_delete }})
  hl("DiffText", {{ bg = p.overlay1, bold = true }})

  -- Syntax
  hl("Comment", {{ fg = p.comment, italic = true }})
  hl("Constant", {{ fg = p.peach }})
  hl("String", {{ fg = p.teal }})
  hl("Character", {{ fg = p.teal }})
  hl("Number", {{ fg = p.peach }})
  hl("Boolean", {{ fg = p.peach }})
  hl("Float", {{ fg = p.peach }})
  hl("Identifier", {{ fg = p.text }})
  hl("Function", {{ fg = p.blue }})
  hl("Statement", {{ fg = p.purple }})
  hl("Conditional", {{ fg = p.purple }})
  hl("Repeat", {{ fg = p.purple }})
  hl("Label", {{ fg = p.purple }})
  hl("Operator", {{ fg = p.cyan }})
  hl("Keyword", {{ fg = p.purple }})
  hl("Exception", {{ fg = p.purple }})
  hl("PreProc", {{ fg = p.purple }})
  hl("Include", {{ fg = p.purple }})
  hl("Define", {{ fg = p.purple }})
  hl("Type", {{ fg = p.yellow }})
  hl("StorageClass", {{ fg = p.purple }})
  hl("Structure", {{ fg = p.yellow }})
  hl("Typedef", {{ fg = p.yellow }})
  hl("Special", {{ fg = p.cyan_bright }})
  hl("SpecialChar", {{ fg = p.cyan_bright }})
  hl("Tag", {{ fg = p.red }})
  hl("Delimiter", {{ fg = p.subtext1 }})
  hl("SpecialComment", {{ fg = p.subtext0, italic = true }})
  hl("Error", {{ fg = p.white, bg = p.red }})
  hl("Todo", {{ fg = p.base, bg = p.yellow, bold = true }})

  -- Treesitter
  hl("@comment", {{ link = "Comment" }})
  hl("@comment.documentation", {{ fg = p.subtext0, italic = true }})
  hl("@string", {{ link = "String" }})
  hl("@string.escape", {{ fg = p.cyan_bright }})
  hl("@string.regexp", {{ fg = p.cyan_bright }})
  hl("@number", {{ link = "Number" }})
  hl("@boolean", {{ link = "Boolean" }})
  hl("@constant", {{ link = "Constant" }})
  hl("@constant.builtin", {{ fg = p.peach }})
  hl("@keyword", {{ link = "Keyword" }})
  hl("@keyword.operator", {{ fg = p.cyan }})
  hl("@function", {{ link = "Function" }})
  hl("@function.method", {{ fg = p.blue_bright }})
  hl("@function.builtin", {{ fg = p.blue_bright }})
  hl("@type", {{ link = "Type" }})
  hl("@type.builtin", {{ fg = p.yellow }})
  hl("@operator", {{ link = "Operator" }})
  hl("@variable", {{ fg = p.text }})
  hl("@variable.builtin", {{ fg = p.red }})
  hl("@variable.member", {{ fg = p.red }})
  hl("@property", {{ fg = p.red }})
  hl("@tag", {{ fg = p.red }})
  hl("@tag.attribute", {{ fg = p.peach }})
  hl("@punctuation", {{ fg = p.subtext1 }})
  hl("@markup.heading", {{ fg = p.blue, bold = true }})
  hl("@markup.strong", {{ fg = p.peach, bold = true }})
  hl("@markup.italic", {{ fg = p.purple, italic = true }})
  hl("@markup.raw", {{ fg = p.teal }})

  -- Diagnostics & LSP
  hl("DiagnosticError", {{ fg = p.red }})
  hl("DiagnosticWarn", {{ fg = p.yellow }})
  hl("DiagnosticInfo", {{ fg = p.blue }})
  hl("DiagnosticHint", {{ fg = p.cyan }})
  hl("DiagnosticUnderlineError", {{ undercurl = true, sp = p.red }})
  hl("DiagnosticUnderlineWarn", {{ undercurl = true, sp = p.yellow }})
  hl("DiagnosticUnderlineInfo", {{ undercurl = true, sp = p.blue }})
  hl("DiagnosticUnderlineHint", {{ undercurl = true, sp = p.cyan }})
  hl("LspReferenceText", {{ bg = p.surface2 }})
  hl("LspReferenceRead", {{ bg = p.surface2 }})
  hl("LspReferenceWrite", {{ bg = p.overlay0 }})

  -- Plugins (GitSigns, Telescope, Neo-tree, NvimTree, WhichKey, IndentBlankline)
  hl("GitSignsAdd", {{ fg = p.teal }})
  hl("GitSignsChange", {{ fg = p.cyan }})
  hl("GitSignsDelete", {{ fg = p.red }})
  hl("TelescopeBorder", {{ fg = p.overlay1, bg = p.surface0 }})
  hl("TelescopePromptBorder", {{ fg = p.blue, bg = p.surface0 }})
  hl("TelescopeSelection", {{ fg = p.white, bg = p.surface2, bold = true }})
  hl("TelescopeMatching", {{ fg = p.cyan, bold = true }})
  hl("NeoTreeNormal", {{ fg = p.text, bg = p.surface0 }})
  hl("NeoTreeNormalNC", {{ fg = p.text, bg = p.surface0 }})
  hl("NvimTreeNormal", {{ fg = p.text, bg = p.surface0 }})
  hl("WhichKey", {{ fg = p.cyan }})
  hl("WhichKeyGroup", {{ fg = p.blue }})
  hl("WhichKeyDesc", {{ fg = p.text }})
  hl("IblIndent", {{ fg = p.overlay0 }})
  hl("IblScope", {{ fg = p.blue }})

  -- Terminal ANSI colors
{term_lines}
end

return M
"""


def render_lualine(pal: dict) -> str:
    c = pal["colors"]
    return f"""-- Aether Dark — Lualine theme
return {{
  normal = {{
    a = {{ fg = "{c['white']['hex']}", bg = "{c['blue']['hex']}", gui = "bold" }},
    b = {{ fg = "{c['textBright']['hex']}", bg = "{c['surface2']['hex']}" }},
    c = {{ fg = "{c['text']['hex']}", bg = "{c['mantle']['hex']}" }},
  }},
  insert = {{
    a = {{ fg = "{c['base']['hex']}", bg = "{c['teal']['hex']}", gui = "bold" }},
  }},
  visual = {{
    a = {{ fg = "{c['base']['hex']}", bg = "{c['purple']['hex']}", gui = "bold" }},
  }},
  replace = {{
    a = {{ fg = "{c['white']['hex']}", bg = "{c['red']['hex']}", gui = "bold" }},
  }},
  command = {{
    a = {{ fg = "{c['base']['hex']}", bg = "{c['cyan']['hex']}", gui = "bold" }},
  }},
  inactive = {{
    a = {{ fg = "{c['comment']['hex']}", bg = "{c['mantle']['hex']}" }},
    b = {{ fg = "{c['comment']['hex']}", bg = "{c['mantle']['hex']}" }},
    c = {{ fg = "{c['comment']['hex']}", bg = "{c['mantle']['hex']}" }},
  }},
}}
"""


def render_kate_theme(pal: dict) -> str:
    c = pal["colors"]
    syn = pal["semantic"]["syntax"]
    s = lambda k: c[syn[k]]["hex"]
    white = c["white"]["hex"]

    def ts(fg: str, sel: str | None = None, **attrs: bool) -> dict:
        entry: dict = {"text-color": fg, "selected-text-color": sel or white}
        entry.update(attrs)
        return entry

    theme = {
        "metadata": {
            "name": "Aether Dark",
            "revision": 1,
            "copyright": ["SPDX-FileCopyrightText: 2026 lumexren"],
            "license": "SPDX-License-Identifier: MIT",
        },
        "editor-colors": {
            "BackgroundColor": c["base"]["hex"],
            "BracketMatching": c["overlay1"]["hex"],
            "CodeFolding": c["surface2"]["hex"],
            "CurrentLine": c["surface1"]["hex"],
            "CurrentLineNumber": c["blue"]["hex"],
            "IconBorder": c["surface0"]["hex"],
            "IndentationLine": c["overlay0"]["hex"],
            "LineNumbers": c["comment"]["hex"],
            "MarkBookmark": c["blue"]["hex"],
            "MarkBreakpointActive": c["red"]["hex"],
            "MarkBreakpointDisabled": c["comment"]["hex"],
            "MarkBreakpointReached": c["yellow"]["hex"],
            "MarkError": c["red"]["hex"],
            "MarkExecution": c["cyan"]["hex"],
            "MarkWarning": c["yellow"]["hex"],
            "ModifiedLines": c["cyan"]["hex"],
            "ReplaceHighlight": c["diffAddBg"]["hex"],
            "SavedLines": c["teal"]["hex"],
            "SearchHighlight": c["diffWarnBg"]["hex"],
            "Separator": c["overlay0"]["hex"],
            "SpellChecking": c["red"]["hex"],
            "TabMarker": c["overlay2"]["hex"],
            "TemplateBackground": c["surface0"]["hex"],
            "TemplateFocusedPlaceholder": c["blue"]["hex"],
            "TemplatePlaceholder": c["surface2"]["hex"],
            "TemplateReadOnlyPlaceholder": c["surface0"]["hex"],
            "TextSelection": c["diffAddBg"]["hex"],
            "WordWrapMarker": c["overlay0"]["hex"],
        },
        "text-styles": {
            "Normal": ts(s("variable"), bold=False, italic=False, underline=False, **{"strike-through": False}),
            "Keyword": ts(s("keyword")),
            "Function": ts(s("function")),
            "Variable": ts(s("variable")),
            "ControlFlow": ts(s("keyword")),
            "Operator": ts(s("operator")),
            "BuiltIn": ts(s("method")),
            "Extension": ts(s("method")),
            "Preprocessor": ts(s("keyword")),
            "Attribute": ts(s("constant")),
            "Char": ts(s("string")),
            "SpecialChar": ts(s("stringEscape")),
            "String": ts(s("string")),
            "VerbatimString": ts(s("string")),
            "SpecialString": ts(s("stringEscape")),
            "Import": ts(s("keyword")),
            "DataType": ts(s("type")),
            "DecVal": ts(s("number")),
            "BaseN": ts(s("number")),
            "Float": ts(s("number")),
            "Constant": ts(s("constant")),
            "Comment": ts(s("comment"), italic=True),
            "Documentation": ts(s("docComment"), italic=True),
            "Annotation": ts(s("docComment"), italic=True),
            "CommentVar": ts(c["cyan"]["hex"], italic=True),
            "RegionMarker": ts(c["cyan"]["hex"]),
            "Information": ts(c["blue"]["hex"]),
            "Warning": ts(c["yellow"]["hex"]),
            "Alert": ts(c["red"]["hex"], bold=True),
            "Error": ts(c["red"]["hex"], underline=True),
            "Others": ts(s("property")),
        },
    }
    return json.dumps(theme, indent=2) + "\n"


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
    generated = [
        (ROOT / "konsole" / "Aether.colorscheme", render_konsole(pal)),
        (ROOT / "terminals" / "ghostty" / "aether-dark", render_ghostty(pal)),
        (ROOT / "terminals" / "kitty" / "aether-dark.conf", render_kitty(pal)),
        (ROOT / "terminals" / "alacritty" / "aether-dark.toml", render_alacritty(pal)),
        (ROOT / "terminals" / "wezterm" / "aether-dark.toml", render_wezterm(pal)),
        (ROOT / "btop" / "aether.theme", render_btop(pal)),
        (ROOT / "bat" / "themes" / "Aether Dark.tmTheme", render_tmtheme(pal)),
        (ROOT / "cli" / "eza" / "theme.yml", render_eza(pal)),
        (ROOT / "cli" / "lazygit" / "aether-dark.yml", render_lazygit(pal)),
        (ROOT / "cli" / "yazi" / "theme.toml", render_yazi(pal)),
        (ROOT / "cli" / "tmux" / "aether.conf", render_tmux(pal)),
        (ROOT / "neovim" / "lua" / "aether" / "init.lua", render_nvim_init(pal)),
        (ROOT / "neovim" / "lua" / "lualine" / "themes" / "aether.lua", render_lualine(pal)),
        (ROOT / "kate" / "Aether Dark.theme", render_kate_theme(pal)),
    ]
    for path, content in generated:
        sync_or_check_file(path, content, write, errors)

    # 2. TOML validation & palette hex check
    for toml_path in [
        ROOT / "starship" / "starship.toml",
        ROOT / "terminals" / "alacritty" / "aether-dark.toml",
        ROOT / "terminals" / "wezterm" / "aether-dark.toml",
        ROOT / "cli" / "yazi" / "theme.toml",
    ]:
        if toml_path.is_file():
            with toml_path.open("rb") as f:
                tomllib.load(f)
            for hx in set(re.findall(r"#[0-9a-fA-F]{6}", toml_path.read_text(encoding="utf-8"))):
                if hx.lower() not in known_hexes:
                    errors.append(f"{toml_path.relative_to(ROOT)} uses non-palette color {hx}")

    # 3. Fastfetch & Kate JSON validation & hex check
    for json_path in [
        ROOT / "cli" / "fastfetch" / "aether.jsonc",
        ROOT / "kate" / "Aether Dark.theme",
    ]:
        if json_path.is_file():
            with json_path.open("r", encoding="utf-8") as f:
                json.load(f)
            for hx in set(re.findall(r"#[0-9a-fA-F]{6}", json_path.read_text(encoding="utf-8"))):
                if hx.lower() not in known_hexes:
                    errors.append(f"{json_path.relative_to(ROOT)} uses non-palette color {hx}")

    # 4. XML validation
    for xml_path in [
        ROOT / "fontconfig" / "fonts.conf",
        ROOT / "fontconfig" / "local.conf",
        ROOT / "bat" / "themes" / "Aether Dark.tmTheme",
    ]:
        try:
            ET.parse(xml_path)
        except ET.ParseError as exc:
            errors.append(f"Invalid XML in {xml_path.relative_to(ROOT)}: {exc}")

    # 5. Plasma metadata JSON & desktoptheme/colorscheme checks
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

    # 6. Kvantum GeneralColors check
    kv_text = (ROOT / "plasma" / "kvantum" / "Aether" / "Aether.kvconfig").read_text(encoding="utf-8")
    for legacy in ("#edf0f2", "#eefcff", "#556064", "#47535a"):
        if legacy in kv_text.lower():
            errors.append(f"plasma/kvantum/Aether/Aether.kvconfig still contains legacy color {legacy}")

    # 7. GTK tokens check
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

    # 8. Zed & VS Code JSON validation & key palette checks
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

    # 9. VSIX matches source extension
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
