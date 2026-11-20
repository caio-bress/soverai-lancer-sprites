#!/usr/bin/env python3
"""
Exports crisp animated GIFs (both individual transparent looping GIFs per
character/direction/animation and isometric-tile showcase GIFs) from the
8-frame Lancer master sprite sheets.
"""

from __future__ import annotations
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parent.parent
SPRITES_DIR = REPO / "sprites"
GIFS_DIR = REPO / "gifs"
BRAIN_DIR = Path(
    "/home/antigravity/.gemini/jetski/brain/v1/default/jetski_remote_agents_3p/ff7f66f4-8693-48db-8219-5ca19e947042"
)

FRAME_W = 192
FRAME_H = 304
COLS = 8

DURATIONS_MS = {
    "idle": 140,  # ~7.1 FPS (smooth 1.1s breathing cycle)
    "walk": 100,  # 10 FPS
    "run": 83,    # 12 FPS
}


def rgba_frames_to_transparent_gif(frames_rgba: list[Image.Image], out_path: Path, duration_ms: int) -> None:
    """Converts a list of RGBA PIL images into a clean, zero-ghosting transparent GIF."""
    # Build a shared 255-color palette from all opaque pixels across the animation
    strip = Image.new("RGBA", (frames_rgba[0].width * len(frames_rgba), frames_rgba[0].height), (0, 0, 0, 0))
    for i, f in enumerate(frames_rgba):
        strip.paste(f, (i * f.width, 0))

    # Quantize RGB of opaque pixels to 255 colors (index 0..254), reserve index 255 for transparency
    rgb_strip = Image.new("RGB", strip.size, (36, 36, 38))
    rgb_strip.paste(strip, (0, 0), strip)
    pal_img = rgb_strip.quantize(colors=255, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE)
    palette = pal_img.getpalette()[: 255 * 3]
    # Pad to 256 colors, index 255 = magenta key (marked transparent)
    while len(palette) < 255 * 3:
        palette.extend([0, 0, 0])
    palette.extend([255, 0, 255])

    pal_ref = Image.new("P", (1, 1))
    pal_ref.putpalette(palette)

    gif_frames: list[Image.Image] = []
    for f in frames_rgba:
        arr = np.array(f)
        alpha_mask = arr[:, :, 3] < 128
        rgb = f.convert("RGB")
        quant = rgb.quantize(palette=pal_ref, dither=Image.Dither.NONE)
        q_arr = np.array(quant, dtype=np.uint8)
        q_arr[alpha_mask] = 255
        p_frame = Image.fromarray(q_arr, mode="P")
        p_frame.putpalette(palette)
        gif_frames.append(p_frame)

    gif_frames[0].save(
        out_path,
        save_all=True,
        append_images=gif_frames[1:],
        loop=0,
        duration=duration_ms,
        transparency=255,
        disposal=2,
        optimize=False,
    )


def draw_iso_stage(w: int, h: int, centers: list[tuple[int, int]], labels: list[str]) -> Image.Image:
    """Draws a clean dark tactical-RPG isometric tile stage for showcase GIFs."""
    bg = Image.new("RGBA", (w, h), (22, 25, 34, 255))
    draw = ImageDraw.Draw(bg)

    # Subtle isometric floor tiles under each character anchor
    tw, th = 148, 74
    for (cx, cy), label in zip(centers, labels):
        # 3D isometric tile diamond + side lips
        top = (cx, cy - th // 2)
        right = (cx + tw // 2, cy)
        bottom = (cx, cy + th // 2)
        left = (cx - tw // 2, cy)
        depth = 12
        draw.polygon([left, bottom, (bottom[0], bottom[1] + depth), (left[0], left[1] + depth)], fill=(30, 34, 46, 255), outline=(58, 66, 86, 255))
        draw.polygon([right, bottom, (bottom[0], bottom[1] + depth), (right[0], right[1] + depth)], fill=(24, 28, 38, 255), outline=(58, 66, 86, 255))
        draw.polygon([top, right, bottom, left], fill=(44, 49, 64, 255), outline=(88, 102, 130, 255))
        # Inner bevel line
        itw, ith = tw - 24, th - 12
        draw.polygon(
            [(cx, cy - ith // 2), (cx + itw // 2, cy), (cx, cy + ith // 2), (cx - itw // 2, cy)],
            outline=(66, 76, 98, 255),
        )
        # Label below tile
        bbox = draw.textbbox((0, 0), label)
        lw = bbox[2] - bbox[0]
        draw.text((cx - lw // 2, cy + th // 2 + 18), label, fill=(176, 190, 212, 255))

    return bg


def build_showcase_row_gif(
    char_name: str,
    title: str,
    direction: str,
    out_path: Path,
) -> None:
    """Side-by-side 3-tile showcase GIF showing Idle, Walk, and Run simultaneously."""
    sheet = Image.open(SPRITES_DIR / f"{char_name}_isometric_{direction}_full_sheet.png")
    w, h = 660, 355
    centers = [(118, 278), (330, 278), (542, 278)]
    labels = [f"IDLE ({direction.upper()})", f"WALK ({direction.upper()})", f"RUN ({direction.upper()})"]
    stage = draw_iso_stage(w, h, centers, labels)

    # Header bar
    hdraw = ImageDraw.Draw(stage)
    hdraw.text((22, 16), f"{title} - 8-Frame Isometric Cycles ({direction.upper()})", fill=(226, 232, 240, 255))

    frames: list[Image.Image] = []
    # 8-frame synchronized showcase loop
    for step in range(8):
        frame = stage.copy()
        fdraw = ImageDraw.Draw(frame)
        for r, (cx, cy) in enumerate(centers):
            cell = sheet.crop((step * FRAME_W, r * FRAME_H, (step + 1) * FRAME_W, (r + 1) * FRAME_H))
            # Ground shadow ellipse (shrinks on airborne run frames 3 & 7)
            is_air = (r == 2 and step in (3, 7))
            rx, ry = (28, 13) if is_air else (38, 18)
            fdraw.ellipse((cx - rx, cy - ry + 2, cx + rx, cy + ry + 2), fill=(10, 12, 18, 120 if is_air else 165))
            frame.alpha_composite(cell, dest=(cx - FRAME_W // 2, cy - FRAME_H + 22))
        frames.append(frame.convert("RGB").quantize(colors=192, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE))

    frames[0].save(
        out_path,
        save_all=True,
        append_images=frames[1:],
        loop=0,
        duration=100,
        optimize=True,
    )


def build_duo_all_showcase_gif(out_path: Path) -> None:
    """Creates a compact 2-character isometric showcase cycling Idle -> Walk -> Run in SE & NW."""
    sheets = {
        ("male", "se"): Image.open(SPRITES_DIR / "male_lancer_isometric_se_full_sheet.png"),
        ("male", "nw"): Image.open(SPRITES_DIR / "male_lancer_isometric_nw_full_sheet.png"),
        ("female", "se"): Image.open(SPRITES_DIR / "female_lancer_isometric_se_full_sheet.png"),
        ("female", "nw"): Image.open(SPRITES_DIR / "female_lancer_isometric_nw_full_sheet.png"),
    }

    w, h = 500, 355
    centers = [(145, 276), (355, 276)]
    base_stage = draw_iso_stage(w, h, centers, ["MALE LANCER", "FEMALE LANCER"])

    sequence = [
        ("se", 0, "IDLE (BREATHING) | SE", 2, 130),
        ("se", 1, "WALK CYCLE (8F)  | SE", 2, 95),
        ("se", 2, "RUN CYCLE (8F)   | SE", 2, 82),
        ("nw", 0, "IDLE (BREATHING) | NW", 2, 130),
        ("nw", 1, "WALK CYCLE (8F)  | NW", 2, 95),
        ("nw", 2, "RUN CYCLE (8F)   | NW", 2, 82),
    ]

    frames: list[Image.Image] = []
    durations: list[int] = []

    for direction, row, badge, loops, dur in sequence:
        for _ in range(loops):
            for c in range(COLS):
                frame = base_stage.copy()
                fdraw = ImageDraw.Draw(frame)
                fdraw.rounded_rectangle((18, 14, 245, 38), radius=6, fill=(32, 38, 52, 255), outline=(56, 189, 248, 255))
                fdraw.text((28, 21), f"{badge}  [{c+1}/8]", fill=(226, 232, 240, 255))

                for char_key, (cx, cy) in zip(["male", "female"], centers):
                    cell = sheets[(char_key, direction)].crop((c * FRAME_W, row * FRAME_H, (c + 1) * FRAME_W, (row + 1) * FRAME_H))
                    is_air = (row == 2 and c in (3, 7))
                    rx, ry = (28, 13) if is_air else (38, 18)
                    fdraw.ellipse((cx - rx, cy - ry + 2, cx + rx, cy + ry + 2), fill=(10, 12, 18, 120 if is_air else 165))
                    frame.alpha_composite(cell, dest=(cx - FRAME_W // 2, cy - FRAME_H + 22))

                frames.append(frame.convert("RGB").quantize(colors=192, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE))
                durations.append(dur)

    frames[0].save(
        out_path,
        save_all=True,
        append_images=frames[1:],
        loop=0,
        duration=durations,
        optimize=True,
    )


def main() -> None:
    GIFS_DIR.mkdir(parents=True, exist_ok=True)
    row_names = ["idle", "walk", "run"]

    # 1. Individual transparent looping GIFs (12 files: male/female x se/nw x idle/walk/run)
    for char_name in ["male_lancer", "female_lancer"]:
        for direction in ["se", "nw"]:
            sheet = Image.open(SPRITES_DIR / f"{char_name}_isometric_{direction}_full_sheet.png")
            for r, rname in enumerate(row_names):
                frames = [
                    sheet.crop((c * FRAME_W, r * FRAME_H, (c + 1) * FRAME_W, (r + 1) * FRAME_H))
                    for c in range(COLS)
                ]
                out_p = GIFS_DIR / f"{char_name}_{direction}_{rname}.gif"
                rgba_frames_to_transparent_gif(frames, out_p, DURATIONS_MS[rname])
                print(f"Exported transparent GIF: {out_p.name} ({out_p.stat().st_size // 1024} KB)")

    # 2. Side-by-side Idle/Walk/Run showcase GIFs per character & direction
    for char_name, title in [("male_lancer", "Male Lancer"), ("female_lancer", "Female Lancer")]:
        for direction in ["se", "nw"]:
            out_p = GIFS_DIR / f"{char_name}_{direction}_showcase.gif"
            build_showcase_row_gif(char_name, title, direction, out_p)
            # Also copy SE/NW showcase GIFs to artifact dir for direct preview
            out_brain = BRAIN_DIR / out_p.name
            out_brain.write_bytes(out_p.read_bytes())
            print(f"Exported showcase GIF: {out_p.name} ({out_p.stat().st_size // 1024} KB)")

    # 3. Master Duo Showcase GIF (Both Lancers cycling Idle -> Walk -> Run in SE & NW)
    duo_p = GIFS_DIR / "lancers_isometric_duo_showcase.gif"
    build_duo_all_showcase_gif(duo_p)
    (BRAIN_DIR / duo_p.name).write_bytes(duo_p.read_bytes())
    print(f"Exported duo showcase GIF: {duo_p.name} ({duo_p.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
