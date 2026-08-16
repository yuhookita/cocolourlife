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
CENTER_SLACK = 1   # px — how far off-centre a raster's margins may be

# The PNGs are delivered at their final, non-supersampled pixel width, so
# anti-aliasing edge pixels are a much larger share of the image than at the
# SVG check's 4x supersample. Measured on a correct build: a pure vector
# (master vs. SVG, no PNG involved) comparison at the same widths as the PNG
# checks reads 0.85% at 1352px and 0.62% at 148px from resampling alone, and
# the actual PNGs read 0.90%/0.15%/1.38% respectively. A genuine defect (a
# 3px crop shift) reads 7.8% at 148px — over 5x this tolerance — so 2% still
# discriminates a real problem from resolution noise.
TOLERANCE_PNG = 0.02

# PNG canvas contracts, from tools/build_logo.py. Not stored constants to
# match against blindly — expected art sizes below are derived from the
# master's own aspect ratio (FULL/MARK), so a wrong crop or a wrong ratio
# in the generator would show up as a mismatch here.
LOGO_PNG_CANVAS_W = 1400
LOGO_PNG_MARGIN = 24     # transparent margin on all four sides
MARK_PNG_CANVAS = 512    # square; mark is centred vertically inside it
ICON_PNG_CANVAS = 180
ICON_PNG_MARGIN = 16     # inset on all four sides, opaque white ground


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


def render_master_at_width(src, clip, width_px):
    """Render a master clip straight to a given pixel width, no supersampling.

    Used for the PNG checks: those assets are delivered at a fixed final
    resolution, so the fair comparison is against the master rendered at
    that same resolution, not at the SVG check's 4x supersample.
    """
    page = fitz.open(str(src))[0]
    rect = fitz.Rect(clip[0], clip[1], clip[0] + clip[2], clip[1] + clip[3])
    factor = width_px / clip[2]
    return to_image(page.get_pixmap(matrix=fitz.Matrix(factor, factor), clip=rect, alpha=False))


def flatten_on_white(rgba_image):
    """Composite an RGBA crop onto white, matching render_master's white backdrop."""
    bg = Image.new("RGB", rgba_image.size, (255, 255, 255))
    bg.paste(rgba_image, (0, 0), rgba_image)
    return bg


def compare(name, official, generated, tolerance=TOLERANCE):
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
    ok = frac <= tolerance
    print(f"{'PASS' if ok else 'FAIL'} {name}: {frac:.4%} of pixels differ strongly "
          f"(tolerance {tolerance:.2%})")
    return ok


def check_transparent_band(name, image, box, label):
    max_alpha = image.split()[-1].crop(box).getextrema()[1]
    ok = max_alpha == 0
    print(f"{'PASS' if ok else 'FAIL'} {name}: {label} band max alpha is {max_alpha} "
          f"(must be 0)")
    return ok


def check_logo_png(src):
    """1400px-wide canvas, artwork on a 24px transparent margin on every side."""
    img = Image.open(ROOT / "assets/logo.png")
    art_w = LOGO_PNG_CANVAS_W - 2 * LOGO_PNG_MARGIN
    expected_h = round(art_w * FULL[3] / FULL[2]) + 2 * LOGO_PNG_MARGIN
    size_ok = (img.width == LOGO_PNG_CANVAS_W
               and abs(img.height - expected_h) <= SIZE_SLACK)
    print(f"{'PASS' if size_ok else 'FAIL'} logo.png: canvas is {img.size} "
          f"(expected {LOGO_PNG_CANVAS_W}x~{expected_h})")

    w, h = img.size
    m = LOGO_PNG_MARGIN
    border_ok = all([
        check_transparent_band("logo.png", img, (0, 0, w, m), "top"),
        check_transparent_band("logo.png", img, (0, h - m, w, h), "bottom"),
        check_transparent_band("logo.png", img, (0, 0, m, h), "left"),
        check_transparent_band("logo.png", img, (w - m, 0, w, h), "right"),
    ])

    generated = flatten_on_white(img.crop((m, m, w - m, h - m)))
    official = render_master_at_width(src, FULL, generated.width)
    artwork_ok = compare("logo.png artwork", official, generated, tolerance=TOLERANCE_PNG)

    return size_ok and border_ok and artwork_ok


def check_logo_mark_png(src):
    """512x512 canvas; the mark spans the full width and is centred vertically."""
    img = Image.open(ROOT / "assets/logo-mark.png")
    size_ok = img.size == (MARK_PNG_CANVAS, MARK_PNG_CANVAS)
    print(f"{'PASS' if size_ok else 'FAIL'} logo-mark.png: canvas is {img.size} "
          f"(expected {MARK_PNG_CANVAS}x{MARK_PNG_CANVAS})")

    bbox = img.split()[-1].getbbox()
    top_margin, bottom_margin = bbox[1], img.height - bbox[3]
    centred_ok = abs(top_margin - bottom_margin) <= CENTER_SLACK
    print(f"{'PASS' if centred_ok else 'FAIL'} logo-mark.png: vertical margins are "
          f"{top_margin}px top / {bottom_margin}px bottom "
          f"(must match within {CENTER_SLACK}px)")

    generated = flatten_on_white(img.crop((0, bbox[1], img.width, bbox[3])))
    official = render_master_at_width(src, MARK, generated.width)
    artwork_ok = compare("logo-mark.png artwork", official, generated, tolerance=TOLERANCE_PNG)

    return size_ok and centred_ok and artwork_ok


def check_apple_touch_icon_png(src):
    """180x180 opaque white canvas; mark inset 16px each side, iOS gets no alpha."""
    img = Image.open(ROOT / "assets/apple-touch-icon.png")
    size_ok = img.size == (ICON_PNG_CANVAS, ICON_PNG_CANVAS)
    print(f"{'PASS' if size_ok else 'FAIL'} apple-touch-icon.png: canvas is {img.size} "
          f"(expected {ICON_PNG_CANVAS}x{ICON_PNG_CANVAS})")

    # iOS composites icons onto black, so this file must carry no transparency.
    opaque_ok = img.mode != "RGBA" or img.split()[-1].getextrema()[0] == 255
    print(f"{'PASS' if opaque_ok else 'FAIL'} apple-touch-icon.png: "
          f"{'has no alpha channel' if img.mode != 'RGBA' else 'alpha is fully opaque'}")

    rgb = img.convert("RGB")
    w, h = rgb.size
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    corner_pixels = [rgb.getpixel(c) for c in corners]
    corners_ok = all(p == (255, 255, 255) for p in corner_pixels)
    print(f"{'PASS' if corners_ok else 'FAIL'} apple-touch-icon.png: corners are "
          f"{corner_pixels} (must all be white)")

    # Deterministic from the build contract (16px inset, master's own aspect
    # ratio) rather than from the generated SVG, so a wrong ratio would show.
    inner_w = ICON_PNG_CANVAS - 2 * ICON_PNG_MARGIN
    inner_h = round(inner_w * MARK[3] / MARK[2])
    y0 = (ICON_PNG_CANVAS - inner_h) // 2
    generated = rgb.crop((ICON_PNG_MARGIN, y0, ICON_PNG_MARGIN + inner_w, y0 + inner_h))
    official = render_master_at_width(src, MARK, inner_w)
    artwork_ok = compare("apple-touch-icon.png artwork", official, generated, tolerance=TOLERANCE_PNG)

    return size_ok and opaque_ok and corners_ok and artwork_ok


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
        check_logo_png(src),
        check_logo_mark_png(src),
        check_apple_touch_icon_png(src),
    ]
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
