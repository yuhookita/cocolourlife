#!/usr/bin/env python3
"""Guard the brand palette rules in style.css.

The pastels are ground-and-decoration colours: on white they do not even reach
the 3:1 large-text threshold, so using one as a text colour is the single most
likely way to regress accessibility here.
"""
import re
import sys
from pathlib import Path

CSS = Path(__file__).resolve().parent.parent / "style.css"

OFFICIAL = {
    "navy": "#1B1464", "crimson": "#BB002D", "rose": "#D8666E",
    "peach": "#EEA296", "apricot": "#F8BD88", "butter": "#FBD894",
    "mint": "#8FC9BB", "sky": "#83BED1", "peri": "#92A9D4",
}
PASTELS = {"rose", "peach", "apricot", "butter", "mint", "sky", "peri"}
# Task 3 extends this with the glyph tokens once their replacements exist.
RETIRED = ["--teal", "--teal-dk", "--teal-lt", "--blue", "--terracotta", "--amber",
           "--co-glyph", "--motif-co", "--motif-nested", "--motif-link", "--motif-union"]

# (foreground, background, label, minimum ratio)
PAIRS = [
    ("#2a2c33", "#ffffff", "body text on page ground", 4.5),
    ("#2a2c33", "#f6f6fa", "body text on tinted sections", 4.5),
    ("#5f6069", "#ffffff", "secondary text on page ground", 4.5),
    ("#5f6069", "#f6f6fa", "secondary text on tinted sections", 4.5),
    ("#1B1464", "#ffffff", "links and headings", 4.5),
    ("#BB002D", "#ffffff", "link hover", 4.5),
    ("#ffffff", "#1B1464", "reversed text on the deep band", 4.5),
    ("#cbd3ec", "#1B1464", "secondary text on the deep band", 4.5),
]


def luminance(hex_colour):
    r, g, b = (int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5))
    def lin(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def contrast(fg, bg):
    a, b = sorted((luminance(fg), luminance(bg)), reverse=True)
    return (a + 0.05) / (b + 0.05)


def main():
    css = CSS.read_text()
    failures = []

    for name, value in OFFICIAL.items():
        if not re.search(rf"--{name}:\s*{value};", css, re.IGNORECASE):
            failures.append(f"token --{name}: {value} is not defined in :root")

    for token in RETIRED:
        if re.search(rf"{re.escape(token)}\b", css):
            failures.append(f"retired token {token} still present")

    for pastel in PASTELS:
        for match in re.finditer(r"(?<!-)\bcolor:\s*([^;]+);", css):
            value = match.group(1)
            if f"var(--{pastel})" in value or OFFICIAL[pastel].lower() in value.lower():
                line = css[:match.start()].count("\n") + 1
                failures.append(f"line {line}: pastel --{pastel} used as a text colour")

    for fg, bg, label, minimum in PAIRS:
        ratio = contrast(fg, bg)
        status = "PASS" if ratio >= minimum else "FAIL"
        print(f"{status} {ratio:6.2f}:1  {label}  ({fg} on {bg}, needs {minimum})")
        if ratio < minimum:
            failures.append(f"{label}: {ratio:.2f}:1 is below {minimum}:1")

    if failures:
        print()
        for f in failures:
            print(f"FAIL {f}")
        sys.exit(1)
    print("\nall brand checks passed")


if __name__ == "__main__":
    main()
