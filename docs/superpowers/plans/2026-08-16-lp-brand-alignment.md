# LP ブランド適用 実装計画

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** CoColour Life のLPを、デザイナー納品の正式ブランド（ロゴ・カラーパレット）に揃える。

**Architecture:** ロゴ資産は公式PDFから機械生成する（手測りのトレースを捨てる）。配色は `style.css` の `:root` トークンを公式10色に置き換え、ティール／テラコッタの独自パレットを廃止する。架空の「弧＋点」グリフはクリムゾンの点とドット構成の図に置換する。LPの構造・文言・情報設計は一切変更しない。

**Tech Stack:** 素のHTML/CSS/JS（ビルドなし）。検証は Python 3.9 + PyMuPDF 1.26.5 + Pillow 11.3。ローカルサーバは `ruby .claude/serve.rb`（:8000）。

**設計書:** `docs/superpowers/specs/2026-08-16-lp-brand-alignment-design.md`

## Global Constraints

- 公式カラー（この値以外を使わない）: Navy `#1B1464` / Crimson `#BB002D` / Dusty Rose `#D8666E` / Peach `#EEA296` / Apricot `#F8BD88` / Butter `#FBD894` / Mint `#8FC9BB` / Sky `#83BED1` / Periwinkle `#92A9D4` / White `#FFFFFF`
- **7つのパステルを `color:` プロパティに使わない。** 白地で WCAG AA を通るのは Navy と Crimson のみ
- 本文色 `--ink: #2a2c33` と `--muted-text: #5f6069` は変更しない
- 書体は変更しない（Source Sans 3 + Noto Sans JP のまま）。ブランドブック指定の Amazon Ember は採用しない
- `index.html` のテキスト内容・セクション順・`data-en` / `data-ja` 属性を変更しない
- `<meta name="robots" content="noindex, nofollow">` と `robots.txt` の `Disallow: /` を維持する
- ロゴ資産のファイル名・パスを変更しない（`assets/logo.svg` `logo-mark.svg` `favicon.svg` `logo.png` `logo-mark.png` `apple-touch-icon.png`）
- push は行わない。Task 5 でユーザーの明示的な承認を得るまで `main` を送信しない
- リポジトリには 2026-08-15 の未コミット変更が既にある。破棄せず、その上に積む

## File Structure

| ファイル | 責務 | 操作 |
|---|---|---|
| `tools/build_logo.py` | 公式PDF → SVG/PNG 6点の生成。資産の出所を実行可能な形で記録する | 新規 |
| `tools/verify_logo.py` | 生成物を正本に重ねてピクセル差分で検査する | 新規 |
| `tools/verify_brand.py` | 配色トークンの健全性・コントラスト・パステル誤用の検査 | 新規 |
| `assets/logo.svg` | 横組みロックアップ（39円＋12グリフ） | 再生成 |
| `assets/logo-mark.svg` | シンボル単体（39円） | 再生成 |
| `assets/favicon.svg` | `logo-mark.svg` と同一図版、`<title>` なし | 再生成 |
| `assets/logo.png` `logo-mark.png` `apple-touch-icon.png` | ラスター版 | 再生成 |
| `style.css` | 配色トークンとグリフ | 変更 |
| `index.html` | ロゴの `width`/`height` 属性、フッターのマーク | 変更 |

`tools/` は新設。ビルドパイプラインではなく、必要なときに手で走らせる再生成・検査スクリプトを置く。

---

### Task 1: ロゴ資産を公式ベクターから再生成する

**Files:**
- Create: `tools/build_logo.py`
- Create: `tools/verify_logo.py`
- Modify: `assets/logo.svg`, `assets/logo-mark.svg`, `assets/favicon.svg`, `assets/logo.png`, `assets/logo-mark.png`, `assets/apple-touch-icon.png`
- Modify: `index.html:38`（ヘッダーロゴの width/height）、`index.html:61`（ヒーローマークの width/height）

**Interfaces:**
- Consumes: なし
- Produces: `assets/logo.svg`（viewBox `0 0 692.1923 207.486`、アスペクト 3.3361）、`assets/logo-mark.svg` と `assets/favicon.svg`（viewBox `0 0 213.4021 207.486`、アスペクト 1.0285）。Task 3 のフッターがこの `logo-mark.svg` を参照する

**背景（実装者向け）**

`Logo Sourcefile.pdf` の1ページ目がカラー横組みの正本。ページは1000×1000pt で、ロゴはその中央付近にある。

- マークは **41個の塗り円**。うち2個は後から描かれる大きい円に完全に隠れるので、**可視は39個**
- ワードマークは **12個の独立したグリフ輪郭**、全て `#1B1464`。円に `#1B1464` は1つも無いので、fill の値だけでマークとワードマークを分離できる
- 座標は PyMuPDF の `get_drawings()` が左上原点で返すので、SVG の座標系とそのまま一致する

**ベジェを自前で組み直してはいけない。** `page.get_drawings()` の items から SVG path を再構成すると、"e" のカウンター（穴）の始点が直前の終点と一致してしまい、サブパスの切れ目を検出できずに字が塗り潰れる。MuPDF 自身の SVG 書き出し `page.get_svg_image(text_as_path=True)` を使い、`viewBox` を差し替えて切り出す。これは検証済み。

- [ ] **Step 1: 検証スクリプトを書く（先に失敗させる）**

`tools/verify_logo.py`:

```python
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
```

閾値の根拠（実測済み）: 現行の手測りトレースは **0.87%**、公式から生成したものは **0.22%**（残りはアンチエイリアスの縁）。0.4% はこの2つをはっきり分ける。マーク単体は 0.04%。

- [ ] **Step 2: 走らせて失敗を確認する**

```bash
cd ~/Documents/GitHub/cocolourlife && python3 tools/verify_logo.py
```

期待: `FAIL logo.svg: 0.8667% of pixels differ strongly (tolerance 0.40%)` — 現行の `assets/logo.svg` は手測りのトレースで、円の半径が平均+2.5%大きく、赤が `#BC002D`、青系4色が1色に潰れているため差分が許容量を超える。終了コード1。

- [ ] **Step 3: 生成スクリプトを書く**

`tools/build_logo.py`:

```python
#!/usr/bin/env python3
"""Regenerate the web logo assets from the designer's vector master.

MuPDF's own SVG writer is used rather than re-assembling the bezier items by
hand: the "e" counter starts exactly where the previous subpath ends, so a
hand-rolled reconstruction cannot tell the subpaths apart and fills the glyph
in solid. Cropping is done purely by swapping the viewBox.
"""
import re
import sys
from pathlib import Path

import fitz
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
DEFAULT_SRC = Path.home() / "Desktop/CoColour Life logo branding/Logo Sourcefile/Logo Sourcefile.pdf"

# Measured from the master: the two hidden circles are excluded from the bbox.
FULL = (153.9040, 396.2570, 692.1923, 207.4860)   # mark + wordmark
MARK = (153.9040, 396.2570, 213.4021, 207.4860)   # mark only

NAVY = "#1b1464"   # the wordmark's ink; no circle uses it, so it isolates glyphs

BANNER = ("<!-- Generated by tools/build_logo.py from the designer's vector master\n"
          "     (Logo Sourcefile.pdf, {what}). Do not hand-edit, recolour, redraw\n"
          "     or re-space this file — regenerate it instead.\n"
          "     Ink #1B1464, accent #BB002D. -->\n")


def page_svg(src):
    return fitz.open(str(src))[0].get_svg_image(text_as_path=True)


def crop(svg, box, drop_wordmark=False, title=None, what=""):
    x, y, w, h = box
    out = svg.replace('width="1000" height="1000" viewBox="0 0 1000 1000"',
                      f'viewBox="{x} {y} {w} {h}"', 1)
    if drop_wordmark:
        out = re.sub(r'<path[^>]*fill="' + NAVY + r'"[^>]*/>\s*', "", out)
    if title:
        out = out.replace("<defs>", f"<title>{title}</title>\n<defs>", 1)
        out = out.replace("<svg ", '<svg role="img" aria-label="CoColour Life" ', 1)
    else:
        out = out.replace("<svg ", '<svg role="presentation" ', 1)
    # normalise MuPDF's lowercase hex so the files read like the brand book
    out = re.sub(r'fill="#([0-9a-f]{6})"', lambda m: 'fill="#%s"' % m.group(1).upper(), out)
    return BANNER.format(what=what) + out


def rasterise(svg_path, width_px):
    page = fitz.open(str(svg_path))[0]
    factor = width_px / page.rect.width
    pix = page.get_pixmap(matrix=fitz.Matrix(factor, factor), alpha=True)
    return Image.frombytes("RGBA", (pix.width, pix.height), pix.samples)


def main():
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SRC
    if not src.exists():
        sys.exit(f"master artwork not found: {src}\npass its path as the first argument")

    svg = page_svg(src)
    (ASSETS / "logo.svg").write_text(
        crop(svg, FULL, title="CoColour Life", what="page 1, colour horizontal lockup"))
    (ASSETS / "logo-mark.svg").write_text(
        crop(svg, MARK, drop_wordmark=True, title="CoColour Life", what="page 1, symbol only"))
    (ASSETS / "favicon.svg").write_text(
        crop(svg, MARK, drop_wordmark=True, what="page 1, symbol only"))

    # logo.png — 1400px wide artwork on a 24px transparent margin
    art = rasterise(ASSETS / "logo.svg", 1400 - 48)
    canvas = Image.new("RGBA", (1400, art.height + 48), (0, 0, 0, 0))
    canvas.paste(art, (24, 24), art)
    canvas.save(ASSETS / "logo.png")

    # logo-mark.png — 512 square, mark centred (it is 1.0285:1, not square)
    mark = rasterise(ASSETS / "logo-mark.svg", 512)
    square = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    square.paste(mark, (0, (512 - mark.height) // 2), mark)
    square.save(ASSETS / "logo-mark.png")

    # apple-touch-icon — 180 square, white ground, 16px inset (iOS does not
    # composite transparency, it puts the icon on black)
    inner = rasterise(ASSETS / "logo-mark.svg", 180 - 32)
    icon = Image.new("RGBA", (180, 180), (255, 255, 255, 255))
    icon.paste(inner, (16, (180 - inner.height) // 2), inner)
    icon.convert("RGB").save(ASSETS / "apple-touch-icon.png")

    for name in ("logo.svg", "logo-mark.svg", "favicon.svg",
                 "logo.png", "logo-mark.png", "apple-touch-icon.png"):
        print(f"wrote assets/{name} ({(ASSETS / name).stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: 生成して検証が通ることを確認する**

```bash
cd ~/Documents/GitHub/cocolourlife && python3 tools/build_logo.py && python3 tools/verify_logo.py
```

期待: 6ファイルの書き出しログのあと `PASS logo.svg`（0.22%前後）/ `PASS logo-mark.svg`（0.04%前後）/ `PASS favicon.svg`、終了コード0。

- [ ] **Step 5: 赤が正しいことを確認する**

```bash
cd ~/Documents/GitHub/cocolourlife && grep -o '#BC002D' assets/*.svg | wc -l && grep -o '#BB002D' assets/logo.svg | wc -l
```

期待: 1行目が `0`（誤った赤が消えている）、2行目が `1`（正しい赤が1箇所）。

- [ ] **Step 6: `index.html` の寸法属性を新しいアスペクト比に合わせる**

`index.html:38` — ヘッダーのロゴ。`width="649" height="195"` は旧 viewBox（3.3306）の値。

```html
        <img class="wordmark-logo" src="assets/logo.svg" alt="" width="692" height="207" />
```

`index.html:61` — ヒーローのマーク。`width="200" height="195"` は旧 viewBox（1.0267）の値。

```html
        <img src="assets/logo-mark.svg" alt="" width="213" height="207" />
```

`width`/`height` は CSS で上書きされるが、読み込み中のレイアウトシフトを防ぐアスペクト比の宣言として効くので、実体と合わせる必要がある。

- [ ] **Step 7: ブラウザで表示崩れがないことを確認する**

サーバを起動（すでに :8000 で動いていれば不要）:

```bash
cd ~/Documents/GitHub/cocolourlife && ruby .claude/serve.rb
```

`http://localhost:8000/` を開き、ヘッダーのロゴとヒーローのマークが歪まず表示され、DevTools のコンソールに404・警告が出ないことを確認する。

- [ ] **Step 8: コミット**

```bash
cd ~/Documents/GitHub/cocolourlife
git add tools/build_logo.py tools/verify_logo.py assets/ index.html
git commit -m "Regenerate logo assets from the vector master

The hand-measured trace had the accent at #BC002D instead of #BB002D,
collapsed four blues and two salmons into one colour each, and inflated
every radius by 2.5%. Generating from the PDF removes all three."
```

---

### Task 2: 配色トークンを公式パレットに置き換える

**Files:**
- Create: `tools/verify_brand.py`
- Modify: `style.css:8-50`（`:root`）、`style.css:53`（`::selection`）、`style.css:152-156`, `178`（ナビ）、`style.css:271-275`（マーカー）、`style.css:308`（カードのホバー）、`style.css:328-331`（カード罫）、`style.css:396-398`（背景ブロブ）、`style.css:463-485`（Our name の罫とドット）

**Interfaces:**
- Consumes: なし
- Produces: `--navy` `--crimson` `--rose` `--peach` `--apricot` `--butter` `--mint` `--sky` `--peri` `--dot`。Task 3 が `--dot` と `--navy` を使う

**背景（実装者向け）**

現行の `--teal` / `--blue` / `--terracotta` / `--amber` はブランド確定前に作られた独自色で、公式パレットに対応色が無い（CIELAB ΔE で最近傍から17〜45離れている）。名前を残したまま値だけ差し替えると `--teal` がネイビーを指すことになるので、名前ごと変える。

`--teal-dk` と `--teal-lt` は**どこからも参照されていない死んだトークン**なので、リネームせず削除する（`grep -c "var(--teal-dk)" style.css` が `0` であることを確認済み）。

- [ ] **Step 1: 検証スクリプトを書く（先に失敗させる）**

`tools/verify_brand.py`:

```python
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
RETIRED = ["--teal", "--teal-dk", "--teal-lt", "--blue", "--terracotta", "--amber"]

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
```

`(?<!-)\bcolor:` は `background-color:` `border-bottom-color:` `--card-accent:` などにマッチさせないための境界。

- [ ] **Step 2: 走らせて失敗を確認する**

```bash
cd ~/Documents/GitHub/cocolourlife && python3 tools/verify_brand.py
```

期待: `--navy` 以下9トークンが未定義、`--teal` 他が残存、という FAIL が並び、終了コード1。

- [ ] **Step 3: `:root` を置き換える**

`style.css:9-30` の neutrals とブランド色のブロックを、以下に差し替える。

```css
  /* ---- neutrals (cooled slightly so they sit under brand navy) ---- */
  --bg:         #ffffff;
  --surface:    #f6f6fa;   /* cool off-white */
  --ink:        #2a2c33;   /* body text — long-form legibility beats brand purity */
  --muted-text: #5f6069;   /* AA on white = 6.24:1 */
  --line:       #e6e5ee;   /* cool hairline */

  /* ---- official palette (BRAND BOOK p.9) ------------------------------
     Navy and Crimson are the only two that clear WCAG AA on white
     (15.78:1 and 6.66:1). The seven pastels top out at 2.37:1, so they are
     ground and decoration only — never a text colour. On navy they all pass.
     tools/verify_brand.py enforces this. */
  --navy:    #1B1464;
  --crimson: #BB002D;
  --rose:    #D8666E;
  --peach:   #EEA296;
  --apricot: #F8BD88;
  --butter:  #FBD894;
  --mint:    #8FC9BB;
  --sky:     #83BED1;
  --peri:    #92A9D4;

  /* ---- deep band (the "Our name" section) ---- */
  --deep:       #1B1464;   /* white on this = 15.78:1 (AAA) */
  --deep-muted: #cbd3ec;   /* secondary text on --deep = 10.84:1 */

  /* functional colour (links, focus) */
  --colour-primary:    #1B1464;   /* 15.78:1 on white */
  --colour-primary-dk: #BB002D;   /* hover — 6.66:1 on white */
```

`--teal` `--teal-dk` `--teal-lt` `--blue` `--terracotta` `--amber` の6行は削除する（`--teal-dk` と `--teal-lt` は元から未使用）。

- [ ] **Step 4: 参照側を新しいトークン名に直す**

`style.css:53`:

```css
::selection { background: rgba(27, 20, 100, 0.14); }
```

`style.css:152-156` — ナビの現在位置。Butter は白地 1.37:1 で見えないので、5本ともネイビーに揃える。

```css
.site-nav a[href="#about"].is-current      { border-bottom-color: var(--navy); }
.site-nav a[href="#name"].is-current       { border-bottom-color: var(--navy); }
.site-nav a[href="#activities"].is-current { border-bottom-color: var(--navy); }
.site-nav a[href="#founder"].is-current    { border-bottom-color: var(--navy); }
.site-nav a[href="#contact"].is-current    { border-bottom-color: var(--navy); }
```

`style.css:178`:

```css
.lang-btn.is-active { color: var(--ink); border-bottom-color: var(--navy); }
```

`style.css:248`（`.section-title` の既定値）:

```css
  --marker: var(--navy);
```

`style.css:271-275` — セクションごとに4色を巡回させるのをやめ、ネイビーに統一する。

```css
#about      .section-title { --marker: var(--navy); }
#activities .section-title { --marker: var(--navy); }
#founder    .section-title { --marker: var(--navy); }
#contact    .section-title { --marker: var(--navy); }
#privacy    .section-title { --marker: var(--navy); }
```

`style.css:308` — カードのホバー地色もクール寄りに。

```css
.areas li:hover { border-color: #d9d8e6; background: #fbfbfd; }
```

`style.css:328-331` — カード上端の罫を公式パステル4色に。`--motif` の側は Task 3 で図ごと差し替えるので、ここでは触らない。

```css
.areas li:nth-child(1) { --card-accent: var(--mint);   --motif: var(--motif-co); }
.areas li:nth-child(2) { --card-accent: var(--peri);   --motif: var(--motif-nested); }
.areas li:nth-child(3) { --card-accent: var(--butter); --motif: var(--motif-link); }
.areas li:nth-child(4) { --card-accent: var(--peach);  --motif: var(--motif-union); }
```

`style.css:396-398` — 背景ブロブ。パステルは彩度が低いので、同じ存在感を出すのに opacity を上げる必要がある。

```css
.hero::after     { width: 340px; height: 340px; left: -150px; bottom: -160px; background: var(--peach);  opacity: 0.16; }
#founder::before { width: 430px; height: 430px; right: -190px; top: -130px;   background: var(--peri);   opacity: 0.16; }
#contact::before { width: 380px; height: 380px; left: -165px;  bottom: -165px; background: var(--butter); opacity: 0.22; }
```

`style.css:466` — Our name の見出し罫のグラデーション。公式値ちょうどに。

```css
  background: linear-gradient(90deg, #8FC9BB, #92A9D4, #FBD894, #EEA296);
```

`style.css:471` のコメント中の `#BC002D` を `#BB002D` に直す。

`style.css:480-485` — dot-divider。現行4色は公式値から最大 ΔE 14 ずれており、4色目 `#aa9fd9` に至っては公式パレットに存在しない紫。

```css
.dot-divider span:nth-child(1) { background: #8FC9BB; }
.dot-divider span:nth-child(2) { background: #92A9D4; }
.dot-divider span:nth-child(3) { background: #FBD894; }
.dot-divider span:nth-child(4) { background: #83BED1; }
.dot-divider span:nth-child(5) {
  background: #BB002D;
```

- [ ] **Step 5: 検証が通ることを確認する**

```bash
cd ~/Documents/GitHub/cocolourlife && python3 tools/verify_brand.py
```

期待: 8行すべて `PASS`、最後に `all brand checks passed`、終了コード0。

架空グリフ（`--co-glyph` と `--motif-*`）はこの時点ではまだ残っている。色の話とは別なので Task 3 で扱う。

- [ ] **Step 6: コミット**

```bash
cd ~/Documents/GitHub/cocolourlife
git add tools/verify_brand.py style.css
git commit -m "Replace the pre-brand palette with the official one

The teal/terracotta/amber set predates the brand and has no counterpart in
the official ten colours. Navy and crimson carry every text and functional
role; the pastels are held to ground and decoration, which verify_brand.py
now enforces."
```

---

### Task 3: 架空グリフを廃し、ドットの語彙に置き換える

**Files:**
- Modify: `style.css:33-37`（グリフのトークン定義）、`style.css:237-268`（`.section-title`）、`style.css:232`（deep band）、`style.css:309-320`（カードの透かし）、`style.css:365`（フッターのマーク）、`style.css:516`（印刷）
- Modify: `index.html:174-179`（フッターのインラインSVG）

**Interfaces:**
- Consumes: Task 1 の `assets/logo-mark.svg`、Task 2 の `--navy` `--crimson`
- Produces: なし（最終タスク）

**背景（実装者向け）**

現行の `--co-glyph`（弧＋点）は、ブランド確定前に作られた**ロゴもどき**。本物のマークは39ドットのリングで、造形言語がまったく違う。フッターにも同じ架空マークがインラインSVGで直書きされており、ヘッダーの本物ロゴと並んで矛盾している。

見出しの前を本物のリングの簡略版にする案も検討したが、20pxではどの簡略版でもドットが潰れて「読み込み中のスピナー」に見える。加えて、見出しごとに小さなロゴを反復するのは、納品物レポート D-5 で「ロゴ改変禁止と自己矛盾」と指摘したブランドパターンと同じことをやってしまう。**クリムゾンの点だけ**にする。ロゴの署名要素の引用であり、マークの模倣ではない。

カードの透かしも同じ理屈で、円だけで構成した図に差し替える。ドットはブランドの造形言語そのものなので、ロゴを模倣せずにブランドの語彙で話せる。

- [ ] **Step 1: 検査に架空グリフの禁止を足す（先に失敗させる）**

`tools/verify_brand.py` の `RETIRED` を拡張する。

```python
RETIRED = ["--teal", "--teal-dk", "--teal-lt", "--blue", "--terracotta", "--amber",
           "--co-glyph", "--motif-co", "--motif-nested", "--motif-link", "--motif-union"]
```

走らせる:

```bash
cd ~/Documents/GitHub/cocolourlife && python3 tools/verify_brand.py
```

期待: `FAIL retired token --co-glyph still present` など5件、終了コード1。

- [ ] **Step 2: グリフのトークンを差し替える**

`style.css:33-37` の5行（`--co-glyph` と `--motif-*` 4本）を、以下の4行に置き換える。`--co-glyph` は行き先が無いので削除。

```css
  /* card watermarks — built from circles only, because dots are the brand's
     drawing language. None of these is the logo mark: repeating the mark as
     decoration is the thing the brand book forbids. */
  --motif-series: url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2040%2040'%3E%3Cg%20fill='black'%3E%3Ccircle%20cx='7'%20cy='30'%20r='3.5'/%3E%3Ccircle%20cx='16'%20cy='26'%20r='4.5'/%3E%3Ccircle%20cx='26'%20cy='21'%20r='5.5'/%3E%3Ccircle%20cx='34'%20cy='15'%20r='6'/%3E%3C/g%3E%3C/svg%3E");
  --motif-spread: url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2040%2040'%3E%3Cg%20fill='black'%3E%3Ccircle%20cx='12'%20cy='20'%20r='7'/%3E%3Ccircle%20cx='25'%20cy='13'%20r='3'/%3E%3Ccircle%20cx='29.5'%20cy='20'%20r='3.5'/%3E%3Ccircle%20cx='25'%20cy='27'%20r='3'/%3E%3C/g%3E%3C/svg%3E");
  --motif-pair:   url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2040%2040'%3E%3Cg%20fill='black'%3E%3Ccircle%20cx='13'%20cy='24'%20r='6.5'/%3E%3Ccircle%20cx='27'%20cy='24'%20r='6.5'/%3E%3Ccircle%20cx='20'%20cy='11'%20r='3.2'/%3E%3C/g%3E%3C/svg%3E");
  --motif-bridge: url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2040%2040'%3E%3Cg%20fill='black'%3E%3Ccircle%20cx='7.5'%20cy='20'%20r='5.5'/%3E%3Ccircle%20cx='32.5'%20cy='20'%20r='5.5'/%3E%3Ccircle%20cx='15'%20cy='20'%20r='2.4'/%3E%3Ccircle%20cx='20'%20cy='20'%20r='2.4'/%3E%3Ccircle%20cx='25'%20cy='20'%20r='2.4'/%3E%3C/g%3E%3C/svg%3E");
```

`style.css:328-331` の `--motif` 側も新しい名前に合わせる（`--card-accent` は Task 2 で設定済み）:

```css
.areas li:nth-child(1) { --card-accent: var(--mint);   --motif: var(--motif-series); }
.areas li:nth-child(2) { --card-accent: var(--peri);   --motif: var(--motif-spread); }
.areas li:nth-child(3) { --card-accent: var(--butter); --motif: var(--motif-pair); }
.areas li:nth-child(4) { --card-accent: var(--peach);  --motif: var(--motif-bridge); }
```

図の意味は順に、研究・評価＝右上がりに大きくなる点の系列、教育と普及＝大きい点から広がる点、アドバイザリー・協働＝対等な点2つと上の小さな点、日豪連携＝両端の点を小さな点が橋渡し。

- [ ] **Step 3: 見出しのマークを点にする**

`style.css:248`（`.section-title` のブロック末尾）に `--dot` を足す:

```css
  --marker: var(--navy);
  --dot: var(--crimson);
}
```

`style.css:250-259` の `.section-title::before` を差し替える:

```css
/* the logo's accent dot, quoted — not the mark redrawn. At this size the
   39-dot ring would only ever read as a smudge. */
.section-title::before {
  content: "";
  flex: none;
  width: 11px;
  height: 11px;
  border-radius: 50%;
  background: var(--dot);
}
```

`style.css:232`（deep band）で反転色にする:

```css
.section--deep .section-title { color: #ffffff; --marker: #ffffff !important; --dot: #ffffff; }
```

- [ ] **Step 4: カードの透かしをネイビーにする**

`style.css:316-317`（`.areas li::before` の塗り）:

```css
  background: var(--navy);
  opacity: 0.30;
```

以前は `var(--card-accent)` だったが、パステルはクールな地色の上で沈んで見えない。

- [ ] **Step 5: フッターのマークを本物に差し替える**

`index.html:174-179` を置き換える:

```html
      <div class="footer-mark" aria-hidden="true">
        <img src="assets/logo-mark.svg" alt="" width="213" height="207" />
      </div>
```

`style.css:365`:

```css
.footer-mark img { display: block; width: 42px; height: auto; }
```

マークは正方形ではなく 1.0285:1 なので、`height` を追従させないと縦に潰れる。

- [ ] **Step 6: 印刷時に点が消えないようにする**

`style.css:516`:

```css
  /* the deep band loses its ground in print, so the white rule and white dot
     it carries would vanish — force both back to ink */
  .section--deep .section-title { color: #000 !important; --marker: #000 !important; --dot: #000 !important; }
```

- [ ] **Step 7: 架空グリフが残っていないことを確認する**

```bash
cd ~/Documents/GitHub/cocolourlife
grep -c 'co-glyph\|motif-co\|motif-nested\|motif-link\|motif-union' style.css
grep -c '1d6e63\|bd5d43\|dda94e\|5b7fb0\|1a5f56\|14675d' style.css index.html
python3 tools/verify_brand.py
```

期待: 1行目 `0`、2行目 `0`、3つ目は全 PASS で終了コード0。

- [ ] **Step 8: ブラウザで確認する**

`http://localhost:8000/` を開き、以下を目視する。

- 各セクション見出しの前がクリムゾンの点1つ（弧＋点のグリフが残っていない）
- 「Our name」の帯の中では点と罫が白
- カード4枚の透かしが4種とも円だけの図で、1枚だけ様式が違うということがない
- フッターのマークが本物のドットリングで、縦に潰れていない
- コンソールに404・警告がない

- [ ] **Step 9: コミット**

```bash
cd ~/Documents/GitHub/cocolourlife
git add style.css index.html
git commit -m "Retire the improvised arc-and-dot glyph

It was a stand-in logo drawn before the real one existed, and the footer
still carried it in green and terracotta next to the genuine mark in the
header. Headings now take the logo's accent dot, the cards take figures
built from circles, and the footer takes the mark itself."
```

---

### Task 4: 全幅・両言語・印刷で検証する

**Files:**
- 変更なし（検証のみ。不具合が出た場合のみ `style.css` を修正）

**Interfaces:**
- Consumes: Task 1〜3 の成果すべて
- Produces: なし

- [ ] **Step 1: 自動検査をまとめて走らせる**

```bash
cd ~/Documents/GitHub/cocolourlife && python3 tools/verify_logo.py && python3 tools/verify_brand.py && echo "ALL CHECKS PASSED"
```

期待: 最後に `ALL CHECKS PASSED`。

- [ ] **Step 2: 幅を変えて崩れを見る**

`http://localhost:8000/` を、320 / 768 / 1024 / 1440 px の各幅で表示する。ブラウザ操作ツールがあれば `resize_window` を使う。

各幅で確認すること:

- 横スクロールバーが出ない
- ヘッダーのロゴが切れない・潰れない
- カードのグリッドが破綻しない（320pxでは1列、1440pxでは2列）
- 「Our name」のネイビーの帯が画面幅いっぱいに伸びている
- ヒーローのマークが本文に重ならない

- [ ] **Step 3: 日本語表示で同じ項目を見る**

ヘッダーの「日本語」ボタンを押し、Step 2 の5項目を 320 / 768 / 1440 px で繰り返す。和文は行長と改行位置が英文と違うため、英文で問題が出なくても和文で溢れることがある。

- [ ] **Step 4: 印刷プレビューを見る**

ブラウザの印刷プレビュー（`Cmd+P`）を開く。

- 「Our name」の帯が地色を失っても、見出しの点と罫が黒で見えている
- ヘッダー・ヒーローのマーク・dot-divider・フッターのマークが非表示になっている（元からの `@media print` の挙動）
- 本文が黒、リンクに下線が付いている

- [ ] **Step 5: コンソールとネットワークを確認する**

DevTools で以下を確認する。

- Console にエラー・警告が無い
- Network に 404 が無い（特に `assets/logo.svg` `logo-mark.svg` `favicon.svg` `apple-touch-icon.png`）
- Carlito が読み込まれていない（旧ロゴのワードマーク用に読んでいたもので、8/15の変更で削除済み）

- [ ] **Step 6: 不具合があれば直してコミット、無ければ次へ**

修正した場合:

```bash
cd ~/Documents/GitHub/cocolourlife
git add -A
git commit -m "Fix <具体的な事象> found at <幅/言語/印刷>"
```

---

### Task 5: ローカル確認を経て公開する

**Files:**
- 変更なし

**Interfaces:**
- Consumes: Task 4 の検証結果
- Produces: なし

**この Task はユーザーの承認なしに完了できない。** `main` は Vercel に自動デプロイされるため、push はそのまま公開になる。

- [ ] **Step 1: コミット履歴と差分の総量を確認する**

```bash
cd ~/Documents/GitHub/cocolourlife
git log --oneline origin/main..HEAD
git diff --stat origin/main..HEAD
git status --short
```

`git status --short` が空であること（作業中の変更が残っていない）を確認する。

- [ ] **Step 2: `noindex` が維持されていることを確認する**

```bash
cd ~/Documents/GitHub/cocolourlife
grep -c 'noindex, nofollow' index.html && grep -c 'Disallow: /' robots.txt
```

期待: どちらも `1`。ABN発行前なので検索エンジンには出さない。

- [ ] **Step 3: ユーザーに確認を取る**

`http://localhost:8000/` のスクリーンショット（ヒーロー / Our name / 活動領域 / フッター、英日それぞれ）を撮り、以下を添えて提示する。

- `origin/main..HEAD` のコミット一覧
- Task 4 の検証結果
- 「push すると https://www.cocolourlife.com に即座に反映されます。進めてよいですか？」

**ユーザーが明示的に承認するまで Step 4 に進まない。**

- [ ] **Step 4: 承認を得てから push する**

```bash
cd ~/Documents/GitHub/cocolourlife && git push origin main
```

- [ ] **Step 5: 本番を確認する**

Vercel のデプロイ完了後（1〜2分）、`https://www.cocolourlife.com` を開き、ヘッダーのロゴ・ネイビーの帯・フッターのマークがローカルと一致することを確認する。キャッシュが残る場合はスーパーリロードする。

---

## スコープ外（この計画で扱わない）

- `noindex` の解除、`sitemap.xml` の再生成、フッターへの ABN 追記 — ABN発行後に別途
- OGP画像の追加
- ファビコンの16px対策 — 39ドットは小サイズで潰れる。デザイナーに簡略版シンボルを要求すべき事項
- デザイナーへの差し戻し一式 — `~/Desktop/CoColour Life logo branding/修正指示書_20260816.md` を参照
- LPの構造・文言・情報設計
