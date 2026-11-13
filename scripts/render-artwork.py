#!/usr/bin/env python3
"""Render Aether 4K wallpaper and Plasma Look-and-Feel previews from palette/palette.json."""

from __future__ import annotations

import json
import math
from pathlib import Path

import cairo
import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
PALETTE_PATH = ROOT / "palette" / "palette.json"

WALLPAPER_OUT = ROOT / "plasma" / "wallpaper" / "Aether" / "contents" / "images" / "3840x2160.png"
PREVIEW_FULL_OUT = ROOT / "plasma" / "look-and-feel" / "Aether" / "contents" / "previews" / "fullscreenpreview.jpg"
PREVIEW_THUMB_OUT = ROOT / "plasma" / "look-and-feel" / "Aether" / "contents" / "previews" / "preview.png"
SDDM_PREVIEW_OUT = ROOT / "plasma" / "sddm" / "Aether" / "preview.png"


def load_colors() -> dict[str, str]:
    with PALETTE_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return {k: v["hex"] for k, v in data["colors"].items()}


def hex_rgb(hx: str) -> tuple[float, float, float]:
    h = hx.lstrip("#")
    return tuple(int(h[i : i + 2], 16) / 255.0 for i in (0, 2, 4))


def rounded_rect(ctx: cairo.Context, x: float, y: float, w: float, h: float, r: float) -> None:
    r = min(r, w / 2.0, h / 2.0)
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    ctx.close_path()


def cairo_to_pil(surface: cairo.ImageSurface) -> Image.Image:
    w, h = surface.get_width(), surface.get_height()
    buf = np.frombuffer(surface.get_data(), dtype=np.uint8).reshape((h, w, 4))
    rgba = buf[:, :, [2, 1, 0, 3]].copy()
    return Image.fromarray(rgba, mode="RGBA")


def float_to_uint8_tpdf(arr: np.ndarray) -> Image.Image:
    rng = np.random.default_rng(42)
    u1 = rng.uniform(-0.75, 0.75, size=arr.shape).astype(np.float32)
    u2 = rng.uniform(-0.75, 0.75, size=arr.shape).astype(np.float32)
    dither = (u1 + u2) / 255.0
    out = np.clip(np.round((arr + dither) * 255.0), 0.0, 255.0).astype(np.uint8)
    return Image.fromarray(out, mode="RGB")


def wave1_profile(t: np.ndarray, h: int) -> tuple[np.ndarray, np.ndarray]:
    hill = np.exp(-((t - 0.725) / 0.195) ** 2)
    swell = np.sin(t * 1.65 * math.pi + 0.55)
    y = h * (0.648 - 0.092 * hill + 0.015 * swell)
    dy_dt = h * (
        0.092 * (2.0 * (t - 0.725) / (0.195 ** 2)) * hill
        + 0.015 * (1.65 * math.pi) * np.cos(t * 1.65 * math.pi + 0.55)
    )
    return y, dy_dt


def wave2_profile(t: np.ndarray, h: int) -> tuple[np.ndarray, np.ndarray]:
    swell = np.sin(t * 1.35 * math.pi - 0.15)
    dip = np.exp(-((t - 0.74) / 0.25) ** 2)
    y = h * (0.728 - 0.038 * swell + 0.022 * dip)
    dy_dt = h * (
        -0.038 * (1.35 * math.pi) * np.cos(t * 1.35 * math.pi - 0.15)
        - 0.022 * (2.0 * (t - 0.74) / (0.25 ** 2)) * dip
    )
    return y, dy_dt


def render_wallpaper(c: dict[str, str], w: int = 3840, h: int = 2160) -> Image.Image:
    xs = (np.arange(w, dtype=np.float32) + 0.5) / float(w)
    ys = (np.arange(h, dtype=np.float32) + 0.5) / float(h)
    xg = xs[None, :]
    yg = ys[:, None]

    def rgb(hx: str) -> np.ndarray:
        return np.array(hex_rgb(hx), dtype=np.float32).reshape(1, 1, 3)

    diag = np.clip(0.55 * xg + 0.45 * yg, 0.0, 1.0)[..., None]
    canvas = (1.0 - diag) * rgb(c["base"]) + diag * rgb(c["crust"])

    def add_radial_glow(cx: float, cy: float, rx: float, ry: float, color_hex: str, strength: float) -> None:
        nonlocal canvas
        dist2 = ((xg - cx) / rx) ** 2 + ((yg - cy) / ry) ** 2
        glow = np.exp(-1.65 * dist2) * np.clip(1.0 - 0.22 * dist2, 0.0, 1.0)
        canvas = canvas + (glow[..., None] * strength) * (rgb(color_hex) - canvas)

    add_radial_glow(0.16, 0.14, 0.58, 0.62, c["blue"], 0.40)
    add_radial_glow(0.32, 0.30, 0.42, 0.45, c["blueDim"], 0.18)
    add_radial_glow(0.64, 0.54, 0.38, 0.34, c["cyan"], 0.14)
    add_radial_glow(0.93, 0.09, 0.38, 0.42, c["red"], 0.22)

    py = (np.arange(h, dtype=np.float32) + 0.5)[:, None]
    scale = float(w) / 3840.0

    def composite_wave(
        profile_fn,
        fill_top_hex: str,
        fill_bot_hex: str,
        glow_hex: str,
        core_hex: str,
        crest_accent_hex: str,
        crest_center: float,
        fill_alpha_top: float,
        ribbon_sigma: float,
        ribbon_alpha: float,
        glow_sigma: float,
        glow_alpha: float,
    ) -> None:
        nonlocal canvas
        wy, dy_dt = profile_fn(xs, h)
        dy_dx = dy_dt / float(w)
        inv_norm = 1.0 / np.sqrt(1.0 + dy_dx * dy_dx)

        signed_d = (py - wy[None, :]) * inv_norm[None, :]
        abs_d = np.abs(signed_d)

        aa_width = 1.6 * scale
        fill_mask = np.clip(0.5 + signed_d / (2.0 * aa_width), 0.0, 1.0)
        depth = np.clip(signed_d / (0.34 * h), 0.0, 1.0)
        fill_col = (1.0 - depth[..., None]) * rgb(fill_top_hex) + depth[..., None] * rgb(fill_bot_hex)
        subsurface_rim = np.exp(-np.maximum(signed_d, 0.0) / (36.0 * scale)) * (signed_d >= -aa_width)
        fill_col = fill_col + (0.14 * subsurface_rim[..., None]) * (rgb(glow_hex) - fill_col)

        eff_fill_alpha = fill_mask * (fill_alpha_top + (1.0 - fill_alpha_top) * np.sqrt(depth))
        canvas = canvas * (1.0 - eff_fill_alpha[..., None]) + fill_col * eff_fill_alpha[..., None]

        crest_focus = np.exp(-((xg - crest_center) / 0.34) ** 2)
        edge_fade = np.clip(np.sin(math.pi * (0.08 + 0.84 * xg)), 0.0, 1.0) ** 0.35
        luma_x = (0.58 + 0.42 * crest_focus) * edge_fade

        wide_halo = np.exp(-0.5 * (abs_d / (glow_sigma * 2.4 * scale)) ** 2) * (glow_alpha * 0.45)
        tight_halo = np.exp(-0.5 * (abs_d / (glow_sigma * 0.65 * scale)) ** 2) * glow_alpha
        halo_intensity = np.clip((wide_halo + tight_halo) * luma_x, 0.0, 1.0)[..., None]
        halo_color = (1.0 - crest_focus[..., None]) * rgb(glow_hex) + crest_focus[..., None] * rgb(crest_accent_hex)
        canvas = canvas + halo_intensity * (halo_color - canvas * 0.55)

        ribbon = np.exp(-0.5 * (abs_d / (ribbon_sigma * scale)) ** 2)
        core = np.exp(-0.5 * (abs_d / (ribbon_sigma * 0.48 * scale)) ** 2) * 0.55
        stroke_intensity = np.clip((ribbon + core) * 0.72 * ribbon_alpha * luma_x, 0.0, 1.0)[..., None]
        stroke_color = (1.0 - crest_focus[..., None]) * rgb(core_hex) + crest_focus[..., None] * rgb(crest_accent_hex)
        canvas = canvas * (1.0 - stroke_intensity) + stroke_color * stroke_intensity

    composite_wave(
        profile_fn=wave1_profile,
        fill_top_hex=c["surface0"],
        fill_bot_hex=c["crust"],
        glow_hex=c["blueDim"],
        core_hex=c["blue"],
        crest_accent_hex=c["blueBright"],
        crest_center=0.725,
        fill_alpha_top=0.92,
        ribbon_sigma=2.2,
        ribbon_alpha=0.88,
        glow_sigma=18.0,
        glow_alpha=0.26,
    )

    composite_wave(
        profile_fn=wave2_profile,
        fill_top_hex=c["mantle"],
        fill_bot_hex=c["crust"],
        glow_hex=c["cyan"],
        core_hex=c["cyan"],
        crest_accent_hex=c["cyanBright"],
        crest_center=0.34,
        fill_alpha_top=0.80,
        ribbon_sigma=2.0,
        ribbon_alpha=0.80,
        glow_sigma=16.0,
        glow_alpha=0.22,
    )

    return float_to_uint8_tpdf(canvas)


def draw_shadow_layer(w: int, h: int, rx: float, ry: float, rw: float, rh: float, radius: float, blur: float, opacity: float) -> Image.Image:
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    ctx = cairo.Context(surf)
    rounded_rect(ctx, rx, ry, rw, rh, radius)
    ctx.set_source_rgba(0.0, 0.0, 0.0, opacity)
    ctx.fill()
    return cairo_to_pil(surf).filter(ImageFilter.GaussianBlur(radius=blur))


def render_preview(c: dict[str, str], wallpaper_4k: Image.Image) -> Image.Image:
    w, h = 3840, 2160
    s = 2.0

    base = wallpaper_4k.convert("RGBA")
    base = Image.alpha_composite(base, draw_shadow_layer(w, h, 218 * s, 148 * s, 968 * s, 650 * s, 14 * s, blur=26 * s, opacity=0.55))
    base = Image.alpha_composite(base, draw_shadow_layer(w, h, 1040 * s, 298 * s, 660 * s, 570 * s, 14 * s, blur=28 * s, opacity=0.62))
    base = Image.alpha_composite(base, draw_shadow_layer(w, h, 700 * s, 996 * s, 520 * s, 68 * s, 18 * s, blur=16 * s, opacity=0.45))

    bgra = np.asarray(base, dtype=np.uint8)[:, :, [2, 1, 0, 3]].copy()
    surf = cairo.ImageSurface.create_for_data(bgra, cairo.FORMAT_ARGB32, w, h)
    ctx = cairo.Context(surf)
    ctx.set_antialias(cairo.ANTIALIAS_BEST)

    ctx.rectangle(0, 0, w, 40 * s)
    ctx.set_source_rgba(*hex_rgb(c["base"]), 0.72)
    ctx.fill()
    ctx.move_to(0, 40 * s)
    ctx.line_to(w, 40 * s)
    ctx.set_source_rgba(*hex_rgb(c["white"]), 0.06)
    ctx.set_line_width(1.0 * s)
    ctx.stroke()

    rounded_rect(ctx, 14 * s, 10 * s, 20 * s, 20 * s, 5 * s)
    ctx.set_source_rgb(*hex_rgb(c["blue"]))
    ctx.fill()

    rounded_rect(ctx, 886 * s, 14 * s, 148 * s, 12 * s, 6 * s)
    ctx.set_source_rgba(*hex_rgb(c["subtext0"]), 0.45)
    ctx.fill()

    for idx in range(3):
        ctx.arc((1848 + idx * 24) * s, 20 * s, 4.5 * s, 0, 2 * math.pi)
        ctx.set_source_rgba(*hex_rgb(c["subtext2"]), 0.85)
        ctx.fill()

    lx, ly, lw, lh = 218 * s, 140 * s, 968 * s, 650 * s
    rounded_rect(ctx, lx, ly, lw, lh, 14 * s)
    ctx.set_source_rgb(*hex_rgb(c["base"]))
    ctx.fill_preserve()
    ctx.set_source_rgba(*hex_rgb(c["overlay1"]), 0.9)
    ctx.set_line_width(1.5 * s)
    ctx.stroke()

    ctx.save()
    rounded_rect(ctx, lx, ly, lw, lh, 14 * s)
    ctx.clip()
    ctx.rectangle(lx, ly, 224 * s, lh)
    ctx.set_source_rgb(*hex_rgb(c["surface0"]))
    ctx.fill()
    ctx.move_to(lx + 224 * s, ly)
    ctx.line_to(lx + 224 * s, ly + lh)
    ctx.set_source_rgb(*hex_rgb(c["overlay0"]))
    ctx.set_line_width(1.2 * s)
    ctx.stroke()
    ctx.restore()

    for idx, key in enumerate(["red", "cyan", "blue"]):
        ctx.arc((246 + idx * 22) * s, 162 * s, 6.2 * s, 0, 2 * math.pi)
        ctx.set_source_rgb(*hex_rgb(c[key]))
        ctx.fill()

    rounded_rect(ctx, 236 * s, 204 * s, 188 * s, 30 * s, 6 * s)
    ctx.set_source_rgba(*hex_rgb(c["blue"]), 0.30)
    ctx.fill()
    for idx, width_bar in enumerate([146, 114, 134, 152, 108, 128]):
        rounded_rect(ctx, 242 * s, (256 + idx * 28) * s, width_bar * s, 11 * s, 5.5 * s)
        ctx.set_source_rgba(*hex_rgb(c["subtext0"]), 0.55)
        ctx.fill()

    code_lines = [
        (0, 140, "blue"),
        (1, 242, "cyan"),
        (2, 336, "subtext2"),
        (3, 434, "teal"),
        (4.3, 150, "red"),
        (5.3, 248, "blue"),
        (6.3, 344, "cyan"),
        (7.3, 444, "subtext2"),
        (8.6, 156, "teal"),
        (9.6, 254, "red"),
        (10.6, 352, "blue"),
        (11.6, 450, "cyan"),
        (12.9, 164, "subtext0"),
        (13.9, 260, "teal"),
    ]
    for row_idx, bar_w, color_key in code_lines:
        indent = int((row_idx % 4.3) * 28)
        cx = (480 + indent) * s
        cy = (214 + row_idx * 36) * s
        rounded_rect(ctx, cx, cy, bar_w * s, 14 * s, 7 * s)
        ctx.set_source_rgb(*hex_rgb(c[color_key]))
        ctx.fill()

    rx, ry, rw, rh = 1040 * s, 290 * s, 660 * s, 570 * s
    rounded_rect(ctx, rx, ry, rw, rh, 14 * s)
    ctx.set_source_rgb(*hex_rgb(c["surface0"]))
    ctx.fill_preserve()
    ctx.set_source_rgba(*hex_rgb(c["blue"]), 0.85)
    ctx.set_line_width(1.6 * s)
    ctx.stroke()

    for idx, key in enumerate(["red", "cyan", "blue"]):
        ctx.arc((1068 + idx * 22) * s, 312 * s, 6.2 * s, 0, 2 * math.pi)
        ctx.set_source_rgb(*hex_rgb(c[key]))
        ctx.fill()

    rounded_rect(ctx, 1076 * s, 360 * s, 588 * s, 118 * s, 10 * s)
    ctx.set_source_rgb(*hex_rgb(c["base"]))
    ctx.fill_preserve()
    ctx.set_source_rgb(*hex_rgb(c["overlay0"]))
    ctx.set_line_width(1.2 * s)
    ctx.stroke()

    rounded_rect(ctx, 1100 * s, 392 * s, 224 * s, 18 * s, 9 * s)
    ctx.set_source_rgb(*hex_rgb(c["textBright"]))
    ctx.fill()
    rounded_rect(ctx, 1100 * s, 428 * s, 360 * s, 13 * s, 6.5 * s)
    ctx.set_source_rgb(*hex_rgb(c["comment"]))
    ctx.fill()

    rounded_rect(ctx, 1076 * s, 518 * s, 166 * s, 44 * s, 8 * s)
    ctx.set_source_rgb(*hex_rgb(c["blue"]))
    ctx.fill()

    rounded_rect(ctx, 1262 * s, 518 * s, 166 * s, 44 * s, 8 * s)
    ctx.set_source_rgb(*hex_rgb(c["surface2"]))
    ctx.fill_preserve()
    ctx.set_source_rgb(*hex_rgb(c["overlay1"]))
    ctx.set_line_width(1.2 * s)
    ctx.stroke()

    dx, dy, dw, dh = 700 * s, 994 * s, 520 * s, 68 * s
    rounded_rect(ctx, dx, dy, dw, dh, 18 * s)
    ctx.set_source_rgba(*hex_rgb(c["base"]), 0.86)
    ctx.fill_preserve()
    ctx.set_source_rgba(*hex_rgb(c["overlay1"]), 0.9)
    ctx.set_line_width(1.4 * s)
    ctx.stroke()

    dock_keys = ["blue", "cyan", "teal", "red", "subtext0", "blue", "cyan"]
    start_x = 736
    for idx, key in enumerate(dock_keys):
        rounded_rect(ctx, (start_x + idx * 66) * s, 1010 * s, 38 * s, 38 * s, 9 * s)
        ctx.set_source_rgb(*hex_rgb(c[key]))
        ctx.fill()

    return Image.fromarray(bgra[:, :, [2, 1, 0, 3]], mode="RGBA").convert("RGB")


def render_sddm_preview(c: dict[str, str], wallpaper_4k: Image.Image) -> Image.Image:
    w, h = 1920, 1080
    base = wallpaper_4k.resize((w, h), Image.Resampling.LANCZOS).convert("RGBA")
    base = Image.alpha_composite(base, draw_shadow_layer(w, h, 765, 390, 390, 300, 14, blur=24, opacity=0.6))

    bgra = np.asarray(base, dtype=np.uint8)[:, :, [2, 1, 0, 3]].copy()
    surf = cairo.ImageSurface.create_for_data(bgra, cairo.FORMAT_ARGB32, w, h)
    ctx = cairo.Context(surf)
    ctx.set_antialias(cairo.ANTIALIAS_BEST)

    rounded_rect(ctx, 888, 250, 144, 42, 8)
    ctx.set_source_rgba(*hex_rgb(c["textBright"]), 0.9)
    ctx.fill()
    rounded_rect(ctx, 850, 306, 220, 14, 7)
    ctx.set_source_rgba(*hex_rgb(c["subtext2"]), 0.7)
    ctx.fill()

    rounded_rect(ctx, 765, 390, 390, 300, 14)
    ctx.set_source_rgba(*hex_rgb(c["surface0"]), 0.92)
    ctx.fill_preserve()
    ctx.set_source_rgb(*hex_rgb(c["overlay1"]))
    ctx.set_line_width(1.4)
    ctx.stroke()

    rounded_rect(ctx, 795, 426, 330, 42, 8)
    ctx.set_source_rgb(*hex_rgb(c["base"]))
    ctx.fill_preserve()
    ctx.set_source_rgb(*hex_rgb(c["overlay0"]))
    ctx.stroke()

    rounded_rect(ctx, 795, 484, 330, 42, 8)
    ctx.set_source_rgb(*hex_rgb(c["base"]))
    ctx.fill_preserve()
    ctx.set_source_rgb(*hex_rgb(c["blue"]))
    ctx.set_line_width(1.6)
    ctx.stroke()

    rounded_rect(ctx, 795, 550, 206, 40, 8)
    ctx.set_source_rgb(*hex_rgb(c["surface2"]))
    ctx.fill_preserve()
    ctx.set_source_rgb(*hex_rgb(c["overlay1"]))
    ctx.set_line_width(1.2)
    ctx.stroke()

    rounded_rect(ctx, 1013, 550, 112, 40, 8)
    ctx.set_source_rgb(*hex_rgb(c["blue"]))
    ctx.fill()

    return Image.fromarray(bgra[:, :, [2, 1, 0, 3]], mode="RGBA").convert("RGB").resize((960, 540), Image.Resampling.LANCZOS)


def main() -> int:
    c = load_colors()
    wp_4k = render_wallpaper(c, 3840, 2160)
    WALLPAPER_OUT.parent.mkdir(parents=True, exist_ok=True)
    wp_4k.save(WALLPAPER_OUT, format="PNG", optimize=True)

    master_preview = render_preview(c, wp_4k)
    PREVIEW_FULL_OUT.parent.mkdir(parents=True, exist_ok=True)
    master_preview.resize((1920, 1080), Image.Resampling.LANCZOS).save(
        PREVIEW_FULL_OUT, format="JPEG", quality=98, subsampling=0, optimize=True
    )
    master_preview.resize((512, 288), Image.Resampling.LANCZOS).save(
        PREVIEW_THUMB_OUT, format="PNG", optimize=True
    )

    SDDM_PREVIEW_OUT.parent.mkdir(parents=True, exist_ok=True)
    render_sddm_preview(c, wp_4k).save(SDDM_PREVIEW_OUT, format="PNG", optimize=True)

    print(f"Rendered: {WALLPAPER_OUT}, {PREVIEW_FULL_OUT}, {PREVIEW_THUMB_OUT}, {SDDM_PREVIEW_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
