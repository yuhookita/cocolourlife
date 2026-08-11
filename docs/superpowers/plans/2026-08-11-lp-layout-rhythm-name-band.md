# LP レイアウト・縦リズム・Our name 濃色帯 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** ワイド画面で横幅を使う2カラムレイアウト、縦余白の圧縮、「Our name」のディープティール濃色帯を実装し、390/768/1440px の3幅で EN・JA 両方の表示を整える。

**Architecture:** 静的サイト（`index.html` / `style.css` / `script.js`）。ビルド工程なし。変更は原則 `style.css` のみで、`index.html` は `#name` の class 属性1箇所だけ差し替える。2カラム化は `.section > .wrap` に限定した CSS Grid で行い、HTML の要素構造には触れない。

**Tech Stack:** 素の HTML / CSS / JS。フレームワーク・ビルドツール・テストランナーなし。ローカル確認は `python3 -m http.server`。

## Global Constraints

- 新しい依存・ビルド工程を追加しない。
- `script.js`（scrollspy・言語切替）は変更しない。
- `index.html` の変更は `#name` の class 属性1箇所のみ。要素の追加・削除・並べ替えをしない。
- 2カラム化のセレクタは `.section > .wrap` に限定する。ヘッダー（`.header-inner`）・フッター・Hero（`.hero-inner`）に Grid を適用しない。
- 2カラムのブレークポイントは `min-width: 900px`。899px 以下は現状どおり1カラム。
- 濃色帯上のテキストは WCAG AA（コントラスト比 4.5:1 以上）を満たすこと。
- `.site-nav` を 767px 以下で非表示にする既存挙動は変更しない。
- 既存の `prefers-reduced-motion` と `@media print` を壊さない。
- テストランナーが存在しないため、各タスクの検証はブラウザ実表示の目視とコントラスト実測で行う。

## File Structure

| ファイル | 責務 | 本計画での変更 |
|---|---|---|
| `style.css` | サイト全体の見た目。単一ファイル構成（既存パターン） | Task 1〜3 で編集 |
| `index.html` | 単一ページのマークアップ | Task 3 で class 属性1箇所のみ |
| `script.js` | scrollspy・言語切替 | 変更なし |
| `<scratchpad>/preview.html` | モバイル幅検証用の iframe ハーネス（リポジトリ外・コミットしない） | Task 0 で作成 |

`style.css` は 449 行の単一ファイルで、セクションごとにコメント区切りされている。この構成を維持し、分割はしない。追加する規則は既存のコメント区切りの該当箇所に置く。

---

## Task 0: 検証環境の準備

**Files:**
- Create: `<scratchpad>/preview.html`（リポジトリ外。`git add` しない）

**Interfaces:**
- Consumes: なし
- Produces: 390px / 768px / 1440px の3幅を同時に表示するプレビューページ。Task 1〜4 の検証で使う。

ブラウザウィンドウのリサイズでは viewport 幅が変わらないことを確認済みのため、固定幅 iframe で実際のメディアクエリを発火させる。

- [ ] **Step 1: ローカルサーバーが動いていることを確認**

```bash
cd /Users/user/Documents/GitHub/cocolourlife
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8765/index.html
```

Expected: `200`。`200` 以外なら `(cd /Users/user/Documents/GitHub/cocolourlife && python3 -m http.server 8765 >/dev/null 2>&1 &)` で起動する。

- [ ] **Step 2: プレビューハーネスを作成**

`<scratchpad>/preview.html` に以下を書く（`<scratchpad>` はセッションのスクラッチパッドディレクトリの絶対パス）:

```html
<!doctype html>
<meta charset="utf-8">
<title>CoColour Life — width preview</title>
<style>
  body { margin: 0; padding: 16px; background: #444; font: 13px system-ui; color: #fff; display: flex; gap: 16px; align-items: flex-start; }
  figure { margin: 0; }
  figcaption { padding: 6px 0; }
  iframe { border: 0; background: #fff; height: 900px; display: block; }
</style>
<figure><figcaption>390px</figcaption><iframe src="http://localhost:8765/index.html" width="390"></iframe></figure>
<figure><figcaption>768px</figcaption><iframe src="http://localhost:8765/index.html" width="768"></iframe></figure>
<figure><figcaption>1440px</figcaption><iframe src="http://localhost:8765/index.html" width="1440"></iframe></figure>
```

- [ ] **Step 3: プレビューを開いて3幅が出ることを確認**

ブラウザで `file://<scratchpad>/preview.html` を開き、スクリーンショットを撮る。

Expected: 3つの iframe が並び、390px の枠ではヘッダーのナビ（About/Our name/…）が非表示、1440px の枠では表示されている。これが確認できればメディアクエリが iframe 内で正しく発火している。

- [ ] **Step 4: コミットしない**

`preview.html` はリポジトリ外なのでコミット対象なし。`git status --short` が空であることを確認する。

---

## Task 1: 2カラムの編集レイアウト

**Files:**
- Modify: `style.css` — `:root` の `--wrap`（36行目付近）、`/* ---------- responsive ---------- */` 区画（376行目付近）

**Interfaces:**
- Consumes: Task 0 のプレビューハーネス
- Produces: `.section > .wrap` の Grid レイアウト。Task 3 の `.section--deep` はこの Grid の上に乗る（濃色帯でも見出しは左レールに入る）。

- [ ] **Step 1: 変更前のスクリーンショットを撮る**

プレビューページを開いて 1440px の枠の About〜Founder あたりを撮影し、比較用に残す。

- [ ] **Step 2: `--wrap` を広げる**

`style.css` の `:root` 内、`/* ---- layout ---- */` の下:

```css
  --wrap: 1080px;
```

（変更前: `--wrap: 820px;`）

- [ ] **Step 3: 2カラムの Grid を追加**

`/* ---------- responsive ---------- */` 区画の `@media (min-width: 620px)` の直後に追加する:

```css
/* wide screens — editorial two-column: section title in a left rail,
   body in the right column. Scoped to .section so the header (flex),
   footer and hero keep their own layout. */
@media (min-width: 900px) {
  .section > .wrap {
    display: grid;
    grid-template-columns: 260px minmax(0, 1fr);
    column-gap: 3rem;
    align-items: start;
  }
  /* span every implicit row so the sticky title has room to travel */
  .section > .wrap > .section-title {
    grid-column: 1;
    grid-row: 1 / span 20;
    align-self: start;
    position: sticky;
    top: 96px;
    margin-bottom: 0;
  }
  .section > .wrap > *:not(.section-title) {
    grid-column: 2;
  }
}
```

`grid-row: 1 / -1` は使わないこと。明示的な行が定義されていないグリッドでは `-1` が1行目に解決され、見出しが1行分しか占めず sticky が機能しない。`column-gap` のみを指定し `row-gap` は指定しないこと（空の暗黙行が高さを持たないようにするため）。

- [ ] **Step 4: 1440px で確認**

プレビューページをリロードして 1440px の枠を撮影する。

Expected:
- About / Our name / Areas of activity / Founder / Contact / Privacy Notice の各見出しが本文の左隣の列に並んでいる
- 本文がセクションをスクロールする間、見出しが画面上部に留まる（sticky）
- 見出し下の色付き罫（`::after`）が見出しの直下に出ている
- ヘッダーのワードマークとナビ、フッターのレイアウトが崩れていない
- Hero のタグラインと右のロゴマークが重なっていない

- [ ] **Step 5: 768px と 390px で1カラムに戻ることを確認**

同じプレビューページの 768px / 390px の枠を撮影する。

Expected: 見出しが本文の真上に積まれ、変更前と同じ縦積みになっている。横スクロールバーが出ていない。

- [ ] **Step 6: コミット**

```bash
cd /Users/user/Documents/GitHub/cocolourlife
git add style.css
git commit -m "Two-column editorial layout on wide screens; widen wrap to 1080px"
```

---

## Task 2: 縦のリズムを詰める

**Files:**
- Modify: `style.css` — `.hero` の `padding-block`（181行目付近）、`.section` の `padding-block`（217行目付近）

**Interfaces:**
- Consumes: Task 1 の Grid レイアウト
- Produces: セクション間余白の最終値。Task 3 の濃色帯もこの余白を使う。

- [ ] **Step 1: `.hero` の上下パディングを縮める**

```css
.hero {
  position: relative;
  overflow: hidden;
  padding-block: clamp(3.5rem, 2.5rem + 4.5vw, 6.5rem);
  border-bottom: 1px solid var(--line);
  background: linear-gradient(180deg, #ffffff 0%, var(--surface) 100%);
}
```

（変更前: `padding-block: clamp(4.5rem, 3rem + 9vw, 9rem);`）

計算結果: 1440px で 104px（変更前 144px）、390px で 57.5px（変更前 72px）。

- [ ] **Step 2: `.section` の上下パディングを縮める**

```css
.section { padding-block: clamp(2.75rem, 5vw, 5rem); }
```

（変更前: `.section { padding-block: clamp(3.5rem, 8vw, 7.5rem); }`）

計算結果: 1440px で 72px（変更前 115px）、1512px で 75.6px（変更前 120px）、390px で 44px（変更前 56px）。隣接セクション間は 1440px で 144px（変更前 230px）。

- [ ] **Step 3: 3幅で確認**

プレビューページをリロードして3幅すべてを撮影する。

Expected:
- 1440px で「Our name」の直後と「Areas of activity」の直前の空白が、変更前より明らかに詰まっている
- セクションの境界（tint 帯の切り替わり）がまだ判別できる — 詰めすぎてセクションが繋がって見えていない
- 390px で本文が窮屈になっていない

- [ ] **Step 4: 詰まりすぎ・緩すぎを微調整**

Step 3 の目視で違和感があれば `clamp()` の第3引数のみを 0.5rem 刻みで調整する。第1引数（モバイル最小値 2.75rem）は変えないこと。

- [ ] **Step 5: コミット**

```bash
cd /Users/user/Documents/GitHub/cocolourlife
git add style.css
git commit -m "Tighten vertical rhythm: section 120px->80px, hero 144px->104px"
```

---

## Task 3: Our name — ディープティールの濃色帯

**Files:**
- Modify: `index.html:137` — `#name` の class
- Modify: `style.css` — `:root`（8行目付近）に色トークン追加、`.section--tint` の隣（218行目付近）に `.section--deep` 追加、`/* ---------- Our name ---------- */` 区画（402行目付近）、`@media print`（441行目付近）

**Interfaces:**
- Consumes: Task 1 の Grid（見出しは左レールに入る）、Task 2 の余白
- Produces: 新しい CSS カスタムプロパティ `--deep`（`#1a5f56`）と `--deep-muted`（`#cfe3df`）、および再利用可能な `.section--deep` クラス

- [ ] **Step 1: 色トークンを追加**

`style.css` の `:root` 内、`/* ---- brand: 4 core colours ... ---- */` ブロックの末尾（`--amber` の次の行）に追加:

```css
  /* ---- deep band (the "Our name" section) ---- */
  --deep:       #1a5f56;   /* deep teal ground — white on this = 7.6:1 (AAA) */
  --deep-muted: #cfe3df;   /* secondary text on --deep = 5.7:1 (AA) */
```

- [ ] **Step 2: `.section--deep` を追加**

`.section--tint { background: var(--surface); }` の直後に追加:

```css
/* deep band — reserved for the section that carries the brand story */
.section--deep {
  background: var(--deep);
  color: #ffffff;
}
.section--deep .section-title { color: #ffffff; --marker: #ffffff; }
.section--deep .lead { color: #ffffff; }
.section--deep ::selection { background: rgba(255, 255, 255, 0.24); }
.section--deep a:focus-visible,
.section--deep button:focus-visible { outline-color: #ffffff; }
```

`--marker: #ffffff` は必須。`#name` は既存のセクション色サイクル（`#about` / `#activities` / `#founder` / `#contact` / `#privacy`）に含まれていないため、指定しないと `.section-title` の初期値 `--marker: var(--teal)` が効き、見出し前の Co マークがディープティール地に沈んで見えなくなる。

- [ ] **Step 3: `index.html` の class を差し替え**

`index.html:137`:

```html
    <section class="section section--deep" id="name">
```

（変更前: `<section class="section section--tint" id="name">`）

- [ ] **Step 4: Our name 区画の配色と文字サイズを更新**

`/* ---------- Our name — the heart of the site ---------- */` 区画を以下に置き換える:

```css
/* ---------- Our name — the heart of the site ---------- */
/* multicolour rule under the title — the logo's pastel dots, which read
   on the deep ground (the original teal→terracotta gradient sinks into it) */
#name .section-title::after {
  width: 116px;
  background: linear-gradient(90deg, #9ec9b7, #88b4d4, #fbd88f, #eda394);
}
#name .lead + .lead { margin-top: 1.1em; }

/* dot divider — the hero ring's palette, restated in miniature.
   Final red dot = the ring's #BC002D accent (the Japan sun); on the deep
   ground it needs a hairline ring to separate from the background. */
.dot-divider {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-top: 2.3rem;
}
.dot-divider span { width: 9px; height: 9px; border-radius: 50%; }
.dot-divider span:nth-child(1) { background: #88b4d4; }
.dot-divider span:nth-child(2) { background: #9ec9b7; }
.dot-divider span:nth-child(3) { background: #fbd88f; }
.dot-divider span:nth-child(4) { background: #ab9fda; }
.dot-divider span:nth-child(5) {
  background: #bc002d;
  width: 11px;
  height: 11px;
  box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.9);
}

/* closing line (kokkara) — the largest type on the page */
.name-coda-intro {
  margin-top: 1.15rem;
  color: var(--deep-muted);
  max-width: 66ch;
}
.name-coda {
  margin-top: 0.5rem;
  font-weight: 600;
  font-size: clamp(2.2rem, 1.8rem + 1.6vw, 3rem);
  line-height: 1.2;
  letter-spacing: -0.015em;
  color: #ffffff;
}
```

- [ ] **Step 5: 印刷スタイルで濃色帯を無効化**

`@media print` ブロック内、`.hero { padding-block: 1.5rem; background: none; }` の次の行に追加:

```css
  .section--deep { background: none !important; color: #000 !important; }
  .section--deep .section-title,
  .section--deep .lead,
  .name-coda,
  .name-coda-intro { color: #000 !important; }
```

これを入れないと、印刷時に濃いティールのベタ面が1ページ分刷られる。

- [ ] **Step 6: コントラストを実測**

ブラウザのコンソールで、実際にレンダリングされた色から比を計算する:

```js
const lum = c => { const [r,g,b] = c.match(/\d+/g).map(n => { const s = n/255; return s <= 0.03928 ? s/12.92 : Math.pow((s+0.055)/1.055, 2.4); }); return 0.2126*r + 0.7152*g + 0.0722*b; };
const ratio = (a,b) => { const [x,y] = [lum(a), lum(b)].sort((p,q) => q-p); return ((x+0.05)/(y+0.05)).toFixed(2); };
const bg = getComputedStyle(document.querySelector('#name')).backgroundColor;
JSON.stringify({
  coda:  ratio(getComputedStyle(document.querySelector('.name-coda')).color, bg),
  lead:  ratio(getComputedStyle(document.querySelector('#name .lead')).color, bg),
  intro: ratio(getComputedStyle(document.querySelector('.name-coda-intro')).color, bg),
  title: ratio(getComputedStyle(document.querySelector('#name .section-title')).color, bg),
})
```

Expected: 4つとも `4.5` 以上。下回った値があれば、その要素の色を明るくしてから再測定する（`--deep-muted` を上げるか、`--deep` を暗くする）。

- [ ] **Step 7: 3幅・EN/JA で確認**

プレビューページをリロードし、3幅それぞれで Our name セクションを撮影する。続いて各 iframe 内の「日本語」ボタンを押して JA でも撮影する。

Expected:
- 濃いティールの帯が画面の左右いっぱいに出ている（`.wrap` の外まで届いている）
- 見出し「Our name / 名前に込めた想い」と前の Co マークが白で読める
- 見出し下のパステルのグラデ罫が見える
- ドットディバイダーの5つ目（赤）が白い輪郭で背景から分離している
- coda「Life starts from here. / こっからライフ — 人生は、ここから。」がページで最大の文字になっている
- 390px で coda が2〜3行に収まり、はみ出していない
- 前後のセクション（About / Areas of activity）との境界がはっきりしている

- [ ] **Step 8: コミット**

```bash
cd /Users/user/Documents/GitHub/cocolourlife
git add index.html style.css
git commit -m "Our name: deep teal band, pastel rule, largest-type coda"
```

---

## Task 4: 全幅・両言語の最終確認

**Files:**
- Modify: `style.css`（Step 3 で不具合が見つかった場合のみ）

**Interfaces:**
- Consumes: Task 1〜3 のすべての変更
- Produces: なし（検証タスク）

- [ ] **Step 1: EN で全セクションを通しで確認**

プレビューページで3幅すべてを上から下までスクロールして撮影する。

チェック項目:
- 390px: ヘッダーのワードマークと言語トグルが1行に収まっている（折り返していない）
- 390px: Hero のロゴマーク（右下・86px）がタグラインと重なっていない
- 390px: `.areas` のカードが1列で、内側余白が窮屈でない
- 768px: `.areas` が2列（`min-width: 620px`）で、カードの文字が詰まっていない
- 全幅: 横スクロールバーが出ていない
- 1440px: sticky の見出しが次のセクションに侵入していない

- [ ] **Step 2: JA で全セクションを通しで確認**

各 iframe 内で「日本語」を押し、同じ範囲を撮影する。

チェック項目:
- 見出しが左レール（260px）に収まっている。「名前に込めた想い」「保健医療・リハビリテーション領域における日豪連携」など長い日本語が破綻していない
- 本文の行長と改行位置が不自然でない
- タイトルタグと meta description が JA に切り替わっている（`script.js` の既存挙動）

- [ ] **Step 3: 見つかった不具合を修正**

Step 1〜2 で問題があれば `style.css` を修正し、該当幅で再確認する。修正がなければこの Step はスキップして Step 4 へ。

- [ ] **Step 4: キーボード操作を確認**

1440px の iframe をクリックしてフォーカスを移し、`Tab` を繰り返し押す。

Expected: skip link → ワードマーク → ナビ5項目 → 言語トグル2つ → 本文中のリンク（LinkedIn、メール、フッター）の順にフォーカスが移り、各要素でフォーカスリング（2px のアウトライン）が見える。濃色帯を通過する際もリングが見える。

- [ ] **Step 5: 印刷プレビューを確認**

1440px の iframe を右クリックして印刷、または `window.print()` は使わずに、ブラウザの印刷プレビューで確認する（ダイアログでの操作は不要、表示の確認のみ）。

Expected: 濃色帯が白地・黒文字になっている。ヘッダー・Hero マーク・ドットディバイダー・フッターマークが非表示。

- [ ] **Step 6: 最終コミット**

Step 3 で修正した場合のみ:

```bash
cd /Users/user/Documents/GitHub/cocolourlife
git add style.css
git commit -m "Fix responsive issues found in cross-width verification"
```

修正がなければ `git status --short` が空であることを確認して終了する。

---

## Self-Review

**Spec coverage:**

| 仕様書の項目 | 対応タスク |
|---|---|
| ① `--wrap` 1080px、`.section > .wrap` の Grid 化、sticky 見出し、900px ブレークポイント | Task 1 |
| ② `.section` 120→80px、`.hero` 144→104px、モバイル 56→44px | Task 2 |
| ③ `#name` の class 差し替え、`.section--deep`、グラデ罫の色替え、ドットディバイダー調整、coda 拡大、`--marker` | Task 3 |
| ③ コントラスト要件（AA 4.5:1） | Task 3 Step 6 |
| モバイル（Hero マーク重なり、ヘッダー収まり、濃色帯全幅、カード余白、日本語行長） | Task 4 Step 1〜3 |
| 検証（390/768/1440、EN/JA、フォーカス、reduced-motion、印刷） | Task 4 |
| `script.js` 変更なし | Global Constraints |
| スコープ外（noindex、ABN、apple-touch-icon、Founder 写真、Contact 強化） | どのタスクにも含めない |

`prefers-reduced-motion` は Task 1〜3 のいずれもアニメーション・トランジションを追加しないため、既存ブロックが影響を受けない。Task 4 で明示的な確認手順を置いていないが、変更を加えないものを確認する手順は不要と判断した。

**Placeholder scan:** 「適切に」「必要に応じて」等の曖昧な指示なし。全 CSS 規則を実値で記載済み。Task 2 Step 4 と Task 4 Step 3 は条件付き修正だが、判断基準（目視での違和感、Step 1〜2 のチェック項目）と調整範囲（`clamp()` の第3引数のみ、0.5rem 刻み）を明示している。

**Type consistency:** `--deep` / `--deep-muted` は Task 3 Step 1 で定義し、Step 2・Step 4 で使用。`.section--deep` は Task 3 Step 2 で定義し、Step 3（HTML）・Step 5（print）で使用。`.section > .wrap` のセレクタは Task 1 Step 3 でのみ定義。名前の揺れなし。
