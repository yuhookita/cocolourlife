#!/usr/bin/env python3
"""Check the generated logo assets against the designer's vector master.

Renders both at the same pixel grid and compares. Run after tools/build_logo.py.
"""
import sys
from pathlib import Path

import fitz
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SRC = Path.home() / "Desktop/CoColour Life logo branding/Logo Sourcefile/Logo Sourcefile.pdf"

# viewBox of each generated asset, in page coordinates of the master
FULL = (153.9040, 396.2570, 692.1923, 207.4860)
MARK = (153.9040, 396.2570, 213.4021, 207.4860)

SCALE = 4          # render at 4x so sub-pixel drift shows up
TOLERANCE = 0.004  # fraction of pixels allowed to differ strongly
SIZE_SLACK = 2     # px — the two renderers round the edge pixel differently


def to_image(pixmap):
    return Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)


def render_master(src, clip):
    page = fitz.open(str(src))[0]
    rect = fitz.Rect(clip[0], clip[1], clip[0] + clip[2], clip[1] + clip[3])
    return to_image(page.get_pixmap(matrix=fitz.Matrix(SCALE, SCALE), clip=rect, alpha=False))


def render_svg(svg_path, width_units):
    page = fitz.open(str(svg_path))[0]
    factor = SCALE * width_units / page.rect.width
    return to_image(page.get_pixmap(matrix=fitz.Matrix(factor, factor), alpha=False))


def compare(name, official, generated):
    if (abs(official.width - generated.width) > SIZE_SLACK
            or abs(official.height - generated.height) > SIZE_SLACK):
        print(f"FAIL {name}: size {generated.size} is not within {SIZE_SLACK}px "
              f"of the master's {official.size}")
        return False
    w = min(official.width, generated.width)
    h = min(official.height, generated.height)
    diff = ImageChops.difference(official.crop((0, 0, w, h)),
                                 generated.crop((0, 0, w, h))).convert("L")
    frac = sum(1 for v in diff.getdata() if v > 80) / (w * h)
    ok = frac <= TOLERANCE
    print(f"{'PASS' if ok else 'FAIL'} {name}: {frac:.4%} of pixels differ strongly "
          f"(tolerance {TOLERANCE:.2%})")
    return ok


def main():
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SRC
    if not src.exists():
        sys.exit(f"master artwork not found: {src}\n"
                 f"pass its path as the first argument")
    results = [
        compare("logo.svg", render_master(src, FULL),
                render_svg(ROOT / "assets/logo.svg", FULL[2])),
        compare("logo-mark.svg", render_master(src, MARK),
                render_svg(ROOT / "assets/logo-mark.svg", MARK[2])),
        compare("favicon.svg", render_master(src, MARK),
                render_svg(ROOT / "assets/favicon.svg", MARK[2])),
    ]
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
