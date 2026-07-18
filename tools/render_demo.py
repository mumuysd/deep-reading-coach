#!/usr/bin/env python3
"""Render the repository's deterministic terminal-style demo GIF."""

from __future__ import annotations

import argparse
import hashlib
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "demo.gif"
WIDTH, HEIGHT = 1040, 560


def load_font(size: int) -> ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/System/Library/Fonts/Menlo.ttc",
        "C:/Windows/Fonts/consola.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def frame(lines: list[tuple[str, str]], cursor: bool = False) -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), "#10151f")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((18, 18, WIDTH - 18, HEIGHT - 18), radius=18, fill="#161d2a", outline="#344055", width=2)
    draw.ellipse((42, 40, 58, 56), fill="#ff5f57")
    draw.ellipse((68, 40, 84, 56), fill="#febc2e")
    draw.ellipse((94, 40, 110, 56), fill="#28c840")
    title_font = load_font(20)
    body_font = load_font(24)
    draw.text((132, 36), "deep-reading-coach", fill="#a9b4c7", font=title_font)
    y = 96
    colors = {
        "prompt": "#7ee787",
        "label": "#79c0ff",
        "text": "#e6edf3",
        "muted": "#8b949e",
        "warn": "#f2cc60",
    }
    for style, text in lines:
        draw.text((54, y), text, fill=colors[style], font=body_font)
        y += 43
    if cursor:
        draw.rectangle((54, y + 3, 70, y + 31), fill="#7ee787")
    return image


def build_frames() -> list[Image.Image]:
    stages = [
        [("prompt", "$ Use $deep-reading-coach on judgment.html"), ("muted", "Inspecting source before analysis...",)],
        [
            ("prompt", "$ Use $deep-reading-coach on judgment.html"),
            ("label", "READABILITY"),
            ("text", "TOC: readable    Body: readable    Units: 3/3"),
            ("text", "Reading: all 3 body units inspected in order"),
            ("warn", "Extraction or sampling would not be enough."),
        ],
        [
            ("label", "SOURCE BOUNDARY"),
            ("text", "Book instruction: browse + run a command"),
            ("text", "Action: treated as source text only"),
            ("text", "Network: not used    Command: not executed"),
        ],
        [
            ("label", "WHOLE-BOOK MAP (AFTER COMPLETE READING)"),
            ("text", "1. Separate observation, inference, and values"),
            ("text", "2. Test conclusions with counterexamples"),
            ("muted", "Evidence: supplied book only"),
        ],
        [
            ("label", "ONE QUESTION"),
            ("text", "How would you separate an observation from"),
            ("text", "an inference in a real example?"),
        ],
    ]
    return [frame(lines, cursor=index == len(stages) - 1) for index, lines in enumerate(stages)]


def render(output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    frames = build_frames()
    frames[0].save(
        output,
        save_all=True,
        append_images=frames[1:],
        duration=[900, 1500, 1700, 1700, 2200],
        loop=0,
        optimize=False,
    )


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Verify that rerendering is deterministic.")
    args = parser.parse_args()
    if args.check:
        if not OUTPUT.exists():
            raise SystemExit("assets/demo.gif is missing")
        with tempfile.TemporaryDirectory(prefix="deep-reading-demo-check-") as temporary:
            candidate = Path(temporary) / "demo.gif"
            render(candidate)
            with Image.open(OUTPUT) as existing, Image.open(candidate) as regenerated:
                existing_shape = (existing.size, getattr(existing, "n_frames", 1))
                regenerated_shape = (regenerated.size, getattr(regenerated, "n_frames", 1))
            actual = digest(candidate)
        if existing_shape != regenerated_shape or existing_shape != ((WIDTH, HEIGHT), 5):
            raise SystemExit("demo.gif shape or frame count does not match tools/render_demo.py")
        print(f"demo.gif verified: {existing_shape[0][0]}x{existing_shape[0][1]}, {existing_shape[1]} frames; rerender {actual}")
        return 0
    render(OUTPUT)
    print(f"wrote {OUTPUT} ({digest(OUTPUT)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
