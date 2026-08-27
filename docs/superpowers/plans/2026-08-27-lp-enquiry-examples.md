# LP「いただくご相談の例」追加 実装計画

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Areas of activity の4カテゴリ説明文を読める文に差し替え、その下に「いただくご相談の例」ブロック（小見出し＋3例＋結び）を EN/JA 両言語で追加する。

**Architecture:** 単一ページの静的LP。`index.html` に要素を足し、`style.css` に規則を足すだけで、JS の変更はない。言語切替は `script.js` の既存機構（`[data-en][data-ja]` を `textContent` で置換）にそのまま乗る。検証はこのリポジトリの既存パターン（`tools/verify_brand.py` 型の stdlib 製ガードスクリプト＋非ゼロ終了）に合わせ、`tools/verify_lp_copy.py` を新設する。描画・印刷の確認は Chrome headless を直接叩く。

**Tech Stack:** 素の HTML / CSS / ES5 JavaScript、Python 3（標準ライブラリ＋PyMuPDF）、Chrome headless。ビルド工程・パッケージマネージャ・テストフレームワークは存在しない。Node は入っていない。

## Global Constraints

設計書 `docs/superpowers/specs/2026-08-27-lp-enquiry-examples-design.md` の要求。全タスクに暗黙に適用される。

- EN が DOM の既定テキスト（JS 無効時の表示）。JA は `data-ja` 属性。**既定テキストは `data-en` と完全一致**させる。
- `[data-en][data-ja]` を持つ要素は**子要素を持たないリーフ**であること。`script.js` の `apply()` が `textContent` で丸ごと置換するため、子要素は初回トグルで消える。
- 新規・差し替えの文面に **em dash（`—` U+2014）を使わない**。既存の Our name セクションの正典コピーは対象外で、変更しない。
- 支援例ブロックに **CTA・リンク・料金・実績数値・お客様の声を置かない**（MVV仕様書の「静かな信頼性」）。
- カテゴリ名（`.area-title`）4つは変更しない。
- 新しい寸法トークンを導入しない。行長は既存の `max-width: 66ch`、文字サイズは既存の `var(--t-sm)` を使う。
- 支援例ブロックにカード chrome（`--surface` 背景・`--line` の枠・`border-radius`・`border-top: 3px` のアクセント・円モチーフの透かし）を与えない。
- `noindex` は触らない。`main` への push とデプロイは行わない（Yuho の判断待ち）。
- 作業ブランチは `lp-enquiry-examples`。リポジトリには `tools/build_logo.py` と `tools/verify_logo.py` の未コミット変更が既にある。**これらは本作業と無関係なので、コミットに含めない**（`git add` はファイルを個別指定すること。`git add -A` / `git add .` は禁止）。

---

## File Structure

| ファイル | 役割 | 本計画での扱い |
|---|---|---|
| `index.html` | LP 本体。`#activities` セクションに4カード | 4つの `.area-desc` を差し替え、`ul.areas` の後ろに3要素を追加 |
| `style.css` | 全スタイル。末尾に `@media print` ブロック | `/* areas of activity */` 節の直後に `/* examples of enquiries */` 節を追加。print ブロックに1行追加 |
| `script.js` | 言語トグルとスクロールスパイ | **変更しない**（新要素は既存の属性規約に乗るだけ） |
| `tools/verify_lp_copy.py` | 新設。承認済み文面と i18n 不変条件のガード | Task 1 で作成、Task 2 で拡張 |
| Vault: `20_Projects/Cocolour Life/CoColour Life MVV・ポジショニング 2026-08.md` | MVV 仕様書 | Task 5 で「支援例ブロックはサービスページではない」判断を追記 |

---

### Task 1: 文面ガードを書き、4カテゴリの説明文を差し替える

**Files:**
- Create: `tools/verify_lp_copy.py`
- Modify: `index.html`（`.area-desc` 4箇所、現在は 124, 128, 132, 136 行目付近）

**Interfaces:**
- Consumes: なし（最初のタスク）
- Produces: `tools/verify_lp_copy.py` に以下を定義する。Task 2 がこれを拡張する。
  - `Doc(HTMLParser)` — `parse(path) -> list[dict]` 相当。各 dict は `{"tag": str, "cls": str, "en": str, "ja": str, "text": str, "children": int}`
  - `AREA_DESCS: list[tuple[str, str]]` — (EN, JA) の4組
  - `check_i18n_invariants(nodes) -> list[str]` — 失敗メッセージのリスト
  - `check_area_descs(nodes) -> list[str]`
  - `main() -> int` — 失敗を印字して 1、成功なら 0

- [ ] **Step 1: ガードスクリプトを書く（この時点では失敗する）**

`tools/verify_lp_copy.py` を新規作成する。

```python
#!/usr/bin/env python3
"""Guard the Areas of activity copy and the enquiry-examples block.

Two invariants matter here.

1. script.js swaps languages by writing textContent onto every element that
   carries both data-en and data-ja. Such an element must therefore be a leaf
   and its default text must equal data-en exactly: a child element would be
   silently deleted on the first toggle, and a mismatch would make the page
   change wording the moment a visitor touches the language buttons.
2. The copy approved in docs/superpowers/specs/2026-08-27-lp-enquiry-examples-design.md
   must be present verbatim in both languages, and must stay free of em dashes
   (the deslop rule agreed for the new copy; the Our name canon keeps its own).
"""
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "index.html"

EM_DASH = "—"

# HTML void elements never open a scope, so they must not go on the stack.
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr"}


class Doc(HTMLParser):
    """Collect every element carrying both data-en and data-ja, with its own
    direct text and the number of element children it holds."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []   # [tag, attrs, [text chunks], child count]
        self.nodes = []

    def handle_starttag(self, tag, attrs):
        if self.stack:
            self.stack[-1][3] += 1
        if tag not in VOID:
            self.stack.append([tag, dict(attrs), [], 0])

    def handle_startendtag(self, tag, attrs):
        # <img … /> and friends: counts as a child, opens no scope
        if self.stack:
            self.stack[-1][3] += 1

    def handle_data(self, data):
        if self.stack:
            self.stack[-1][2].append(data)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                node = self.stack[i]
                del self.stack[i:]
                self._close(node)
                return

    def _close(self, node):
        tag, attrs, text, children = node
        if "data-en" in attrs and "data-ja" in attrs:
            self.nodes.append({
                "tag": tag,
                "cls": attrs.get("class", ""),
                "en": attrs["data-en"],
                "ja": attrs["data-ja"],
                "text": "".join(text).strip(),
                "children": children,
            })


def parse(path):
    doc = Doc()
    doc.feed(path.read_text(encoding="utf-8"))
    doc.close()
    return doc.nodes


# ---- approved copy, spec §6.1 ------------------------------------------------

AREA_DESCS = [
    ("Programme and service evaluation, workforce and cost analysis, and "
     "implementation research. The usual output is a report that sets out what "
     "worked, what did not, and what the evidence does not yet cover.",
     "プログラム・サービスの評価、人材と費用の分析、実装研究。成果物は多くの場合、"
     "何が機能し、何が機能しなかったか、そしてエビデンスがまだ及んでいない範囲を"
     "書いた報告書です。"),
    ("Lectures, workshops and teaching materials, in English and Japanese. "
     "Existing material is rebuilt for the setting where it will be used rather "
     "than translated as it stands.",
     "講義・研修・教材の作成。英語と日本語の両方で行います。既存の教材は、そのまま"
     "訳すのではなく、使われる現場に合わせて作り直します。"),
    ("Advisory work with health services, universities and industry: shaping a "
     "project before it starts, or reviewing one already running. We take on a "
     "small number at a time.",
     "医療サービス・大学・企業への助言。企画が始まる前の設計と、進行中の案件の点検が"
     "中心です。同時にお受けする件数は絞っています。"),
    ("Exchange of evidence, models of care and technology in both directions. "
     "Most of the effort goes into working out what has to change before "
     "something that works in one country works under the other's funding and "
     "service arrangements.",
     "エビデンス・ケアモデル・テクノロジーの双方向の交流。労力の大半は、一方の国で"
     "機能しているものが、もう一方の国の制度と資金の仕組みの下でも機能するには何を"
     "変える必要があるかを詰めることに使われます。"),
]


# ---- checks ------------------------------------------------------------------

def check_i18n_invariants(nodes):
    """Every translatable node must be a leaf whose text matches data-en."""
    failures = []
    for n in nodes:
        label = "{}.{}".format(n["tag"], n["cls"] or "(no class)")
        if n["children"]:
            failures.append(
                "{}: has {} child element(s); script.js would delete them on the "
                "first language toggle".format(label, n["children"]))
        if n["text"] != n["en"].strip():
            failures.append(
                "{}: default text does not match data-en\n    text: {!r}\n"
                "    data-en: {!r}".format(label, n["text"], n["en"].strip()))
    return failures


def _by_class(nodes, cls):
    return [n for n in nodes if cls in n["cls"].split()]


def check_area_descs(nodes):
    descs = _by_class(nodes, "area-desc")
    failures = []
    if len(descs) != 4:
        failures.append(
            "expected 4 .area-desc nodes, found {}".format(len(descs)))
        return failures
    for i, (en, ja) in enumerate(AREA_DESCS):
        if descs[i]["en"] != en:
            failures.append(
                "area-desc {}: data-en is not the approved copy\n    found: {!r}"
                .format(i + 1, descs[i]["en"]))
        if descs[i]["ja"] != ja:
            failures.append(
                "area-desc {}: data-ja is not the approved copy\n    found: {!r}"
                .format(i + 1, descs[i]["ja"]))
    return failures


def check_no_em_dash(nodes, classes):
    """The new copy must not carry em dashes. Scoped to the classes this spec
    introduces, so the Our name canon keeps its own."""
    failures = []
    for cls in classes:
        for n in _by_class(nodes, cls):
            for key in ("en", "ja"):
                if EM_DASH in n[key]:
                    failures.append(
                        "{}: data-{} contains an em dash".format(cls, key))
    return failures


def main():
    nodes = parse(HTML)
    failures = []
    failures += check_i18n_invariants(nodes)
    failures += check_area_descs(nodes)
    failures += check_no_em_dash(nodes, ["area-desc"])

    if failures:
        print("index.html copy guard: {} failure(s)\n".format(len(failures)))
        for f in failures:
            print("  - {}".format(f))
        return 1
    print("index.html copy guard: OK ({} translatable nodes)".format(len(nodes)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: 実行して失敗を確認する**

Run: `python3 tools/verify_lp_copy.py`

Expected: 終了コード 1。`area-desc 1: data-en is not the approved copy` を含む8件の失敗（4カテゴリ × EN/JA）。`check_i18n_invariants` の失敗は **0件**であること（既存サイトが既にこの不変条件を満たしているため）。もし i18n 側で失敗が出たら、それはパーサのバグなので先にそちらを直す。

- [ ] **Step 3: index.html の4つの説明文を差し替える**

`#activities` の `ul.areas` 内、4つの `<span class="area-desc">` を差し替える。`data-en` / `data-ja` / 既定テキストの3箇所すべてを同時に更新する（既定テキストは `data-en` と一字一句同じ）。`.area-title` の4行は触らない。

```html
<li>
  <span class="area-title" data-en="Research and evaluation" data-ja="研究・評価">Research and evaluation</span>
  <span class="area-desc" data-en="Programme and service evaluation, workforce and cost analysis, and implementation research. The usual output is a report that sets out what worked, what did not, and what the evidence does not yet cover." data-ja="プログラム・サービスの評価、人材と費用の分析、実装研究。成果物は多くの場合、何が機能し、何が機能しなかったか、そしてエビデンスがまだ及んでいない範囲を書いた報告書です。">Programme and service evaluation, workforce and cost analysis, and implementation research. The usual output is a report that sets out what worked, what did not, and what the evidence does not yet cover.</span>
</li>
<li>
  <span class="area-title" data-en="Education and knowledge translation" data-ja="教育・知識の実装と普及">Education and knowledge translation</span>
  <span class="area-desc" data-en="Lectures, workshops and teaching materials, in English and Japanese. Existing material is rebuilt for the setting where it will be used rather than translated as it stands." data-ja="講義・研修・教材の作成。英語と日本語の両方で行います。既存の教材は、そのまま訳すのではなく、使われる現場に合わせて作り直します。">Lectures, workshops and teaching materials, in English and Japanese. Existing material is rebuilt for the setting where it will be used rather than translated as it stands.</span>
</li>
<li>
  <span class="area-title" data-en="Advisory and collaborative projects" data-ja="アドバイザリー・協働プロジェクト">Advisory and collaborative projects</span>
  <span class="area-desc" data-en="Advisory work with health services, universities and industry: shaping a project before it starts, or reviewing one already running. We take on a small number at a time." data-ja="医療サービス・大学・企業への助言。企画が始まる前の設計と、進行中の案件の点検が中心です。同時にお受けする件数は絞っています。">Advisory work with health services, universities and industry: shaping a project before it starts, or reviewing one already running. We take on a small number at a time.</span>
</li>
<li>
  <span class="area-title" data-en="Australia–Japan collaboration in health and rehabilitation" data-ja="保健医療・リハビリテーション領域における日豪連携">Australia–Japan collaboration in health and rehabilitation</span>
  <span class="area-desc" data-en="Exchange of evidence, models of care and technology in both directions. Most of the effort goes into working out what has to change before something that works in one country works under the other's funding and service arrangements." data-ja="エビデンス・ケアモデル・テクノロジーの双方向の交流。労力の大半は、一方の国で機能しているものが、もう一方の国の制度と資金の仕組みの下でも機能するには何を変える必要があるかを詰めることに使われます。">Exchange of evidence, models of care and technology in both directions. Most of the effort goes into working out what has to change before something that works in one country works under the other's funding and service arrangements.</span>
</li>
```

注意: カテゴリ④の `data-en` と本文にはアポストロフィ `'`（`the other's`）が入る。属性は `"` で囲まれているのでエスケープ不要。カテゴリ④のタイトルにある `–` は **en dash** であり、禁止した em dash とは別の文字。変更しないこと。

- [ ] **Step 4: 実行して通ることを確認する**

Run: `python3 tools/verify_lp_copy.py`

Expected: 終了コード 0。`index.html copy guard: OK (N translatable nodes)`。

- [ ] **Step 5: コミット**

```bash
git add tools/verify_lp_copy.py index.html
git commit -m "Rewrite the area descriptions as sentences, and guard the copy

Two of the four read as bare noun lists, which only a peer researcher can
picture. Say what actually comes out of the work, including what it does
not cover. The guard also pins the invariant script.js depends on: every
translatable node is a leaf whose default text equals data-en."
```

---

### Task 2: 支援例ブロックを追加する

**Files:**
- Modify: `tools/verify_lp_copy.py`（定数と関数を追加、`main()` を拡張）
- Modify: `index.html`（`ul.areas` の閉じタグ直後に3要素を追加）
- Modify: `style.css`（`/* areas of activity */` 節の直後に新節、`@media print` に1行）

**Interfaces:**
- Consumes: Task 1 の `Doc`, `parse`, `_by_class`, `check_i18n_invariants`, `check_no_em_dash`, `main`
- Produces: `tools/verify_lp_copy.py` に `ENQUIRIES_TITLE: tuple[str, str]`、`ENQUIRIES: list[tuple[str, str]]`、`ENQUIRIES_NOTE: tuple[str, str]`、`check_enquiries(nodes) -> list[str]`、`check_css() -> list[str]` を追加

- [ ] **Step 1: ガードを拡張する（この時点では失敗する）**

`tools/verify_lp_copy.py` の `AREA_DESCS` 定義の直後に、承認済み文面（spec §6.2）を足す。

```python
# ---- approved copy, spec §6.2 ------------------------------------------------

ENQUIRIES_TITLE = ("Examples of enquiries we receive", "いただくご相談の例")

ENQUIRIES = [
    ("A company or research group whose healthcare product or service already "
     "works in one country and who want to introduce it in another. What they "
     "usually need first is a clear account of the evidence they will be asked "
     "for, and of the conditions in the setting where it would be used.",
     "ある国ですでに成果を上げている医療・ヘルスケアの製品やサービスを、別の国で"
     "展開したい企業・研究グループから。最初に必要になるのはたいてい、導入先で"
     "求められるエビデンスと、実際に使われる現場の条件を把握することです。"),
    ("A practitioner or organisation who has seen a way of working succeed in "
     "Australia, or in Japan, and wants to bring it to the other country with "
     "colleagues there rather than on their own. In practice this often means "
     "joint presentations, co-authored writing, and rebuilding existing "
     "material together.",
     "オーストラリア（あるいは日本）の現場で評価されている取り組みを、もう一方の国に"
     "紹介したい実践者・団体から。ひとりで進めるのではなく、現地の人たちと一緒に"
     "進めたいというご相談です。実際の作業は、共同での発表や執筆、既存の教材を"
     "一緒に作り直すことが多くなります。"),
    ("Researchers or clinicians with an international project or study in mind, "
     "who know the question they want to ask but not how a collaboration across "
     "two systems is set up, funded and kept going. Some of this we can answer "
     "from experience. Some of it we work out together.",
     "海外との共同プロジェクトや研究を考えている研究者・臨床家から。問いは決まって"
     "いるが、二つの制度をまたぐ協働をどう立ち上げ、どう資金を得て、どう続けるかが"
     "分からない、というご相談です。経験から答えられる部分もあれば、一緒に考えながら"
     "進める部分もあります。"),
]

ENQUIRIES_NOTE = (
    "Not every enquiry is a fit. Where it is not, we say so, and where we can "
    "we point to someone better placed.",
    "すべてのご相談をお受けできるわけではありません。適さない場合はその旨をお伝えし、"
    "可能であればより適した方をご紹介します。",
)
```

`check_area_descs` の直後に検査関数を足す。

```python
def check_enquiries(nodes):
    failures = []

    titles = _by_class(nodes, "enquiries-title")
    if len(titles) != 1:
        failures.append(
            "expected 1 .enquiries-title, found {}".format(len(titles)))
    else:
        if titles[0]["tag"] != "h3":
            failures.append(
                ".enquiries-title must be an <h3> (it sits under the section's "
                "<h2>), found <{}>".format(titles[0]["tag"]))
        en, ja = ENQUIRIES_TITLE
        if titles[0]["en"] != en or titles[0]["ja"] != ja:
            failures.append(".enquiries-title is not the approved copy")

    items = _by_class(nodes, "enquiry")
    if len(items) != 3:
        failures.append("expected 3 .enquiry items, found {}".format(len(items)))
    else:
        for i, (en, ja) in enumerate(ENQUIRIES):
            if items[i]["en"] != en:
                failures.append(
                    "enquiry {}: data-en is not the approved copy\n    found: "
                    "{!r}".format(i + 1, items[i]["en"]))
            if items[i]["ja"] != ja:
                failures.append(
                    "enquiry {}: data-ja is not the approved copy\n    found: "
                    "{!r}".format(i + 1, items[i]["ja"]))

    notes = _by_class(nodes, "enquiries-note")
    if len(notes) != 1:
        failures.append(
            "expected 1 .enquiries-note, found {}".format(len(notes)))
    else:
        en, ja = ENQUIRIES_NOTE
        if notes[0]["en"] != en or notes[0]["ja"] != ja:
            failures.append(".enquiries-note is not the approved copy")

    # the block must carry no call to action of any kind
    for n in items + notes:
        if n["children"]:
            failures.append(
                "the enquiries block must hold no links or other markup")
    return failures
```

続けて CSS ガードを足す。ファイル冒頭の `HTML = ROOT / "index.html"` の下に `CSS = ROOT / "style.css"` を追加したうえで、次を定義する。

```python
def check_css():
    css = CSS.read_text(encoding="utf-8")
    failures = []

    required = [
        (".enquiries-title", "border-top: 1px solid var(--line)"),
        (".enquiries li", "border-left: 2px solid var(--card-accent)"),
        (".enquiries li:nth-child(1)", "--card-accent: var(--mint)"),
        (".enquiries li:nth-child(2)", "--card-accent: var(--peri)"),
        (".enquiries li:nth-child(3)", "--card-accent: var(--peach)"),
    ]
    for selector, declaration in required:
        if selector not in css:
            failures.append("style.css: missing selector {}".format(selector))
        elif declaration not in css:
            failures.append(
                "style.css: {} must declare {}".format(selector, declaration))

    # the separator and the rules have to survive the print stylesheet, which is
    # why they are borders and not the dot divider (spec §7.1)
    print_block = css.split("@media print")[-1]
    if "border-left-color: #000" not in print_block:
        failures.append(
            "style.css: @media print must force .enquiries li border-left-color "
            "to #000")

    # no card chrome: that is what tells a reader these are not a fifth area
    block = css.split("examples of enquiries")[-1].split("/* ----------")[0]
    for banned in ("background:", "border-radius:", "var(--surface)"):
        if banned in block:
            failures.append(
                "style.css: the enquiries block must carry no card chrome, "
                "found {}".format(banned))
    return failures
```

最後に `main()` を差し替える。

```python
def main():
    nodes = parse(HTML)
    failures = []
    failures += check_i18n_invariants(nodes)
    failures += check_area_descs(nodes)
    failures += check_enquiries(nodes)
    failures += check_no_em_dash(
        nodes, ["area-desc", "enquiries-title", "enquiry", "enquiries-note"])
    failures += check_css()

    if failures:
        print("index.html copy guard: {} failure(s)\n".format(len(failures)))
        for f in failures:
            print("  - {}".format(f))
        return 1
    print("index.html copy guard: OK ({} translatable nodes)".format(len(nodes)))
    return 0
```

- [ ] **Step 2: 実行して失敗を確認する**

Run: `python3 tools/verify_lp_copy.py`

Expected: 終了コード 1。`expected 1 .enquiries-title, found 0` / `expected 3 .enquiry items, found 0` / `expected 1 .enquiries-note, found 0` と、`style.css: missing selector` 系5件、print ブロック1件。

- [ ] **Step 3: index.html に支援例ブロックを追加する**

`#activities` の `</ul>`（`ul.areas` の閉じ）の直後、`</div>`（`.wrap` の閉じ）の前に挿入する。

```html
        <!-- The three enquiries cut across the four areas above rather than
             sitting under one of them, so they are deliberately not cards:
             equal weight would read as a fifth area. -->
        <h3 class="enquiries-title" data-en="Examples of enquiries we receive" data-ja="いただくご相談の例">Examples of enquiries we receive</h3>
        <ul class="enquiries">
          <li class="enquiry" data-en="A company or research group whose healthcare product or service already works in one country and who want to introduce it in another. What they usually need first is a clear account of the evidence they will be asked for, and of the conditions in the setting where it would be used." data-ja="ある国ですでに成果を上げている医療・ヘルスケアの製品やサービスを、別の国で展開したい企業・研究グループから。最初に必要になるのはたいてい、導入先で求められるエビデンスと、実際に使われる現場の条件を把握することです。">A company or research group whose healthcare product or service already works in one country and who want to introduce it in another. What they usually need first is a clear account of the evidence they will be asked for, and of the conditions in the setting where it would be used.</li>
          <li class="enquiry" data-en="A practitioner or organisation who has seen a way of working succeed in Australia, or in Japan, and wants to bring it to the other country with colleagues there rather than on their own. In practice this often means joint presentations, co-authored writing, and rebuilding existing material together." data-ja="オーストラリア（あるいは日本）の現場で評価されている取り組みを、もう一方の国に紹介したい実践者・団体から。ひとりで進めるのではなく、現地の人たちと一緒に進めたいというご相談です。実際の作業は、共同での発表や執筆、既存の教材を一緒に作り直すことが多くなります。">A practitioner or organisation who has seen a way of working succeed in Australia, or in Japan, and wants to bring it to the other country with colleagues there rather than on their own. In practice this often means joint presentations, co-authored writing, and rebuilding existing material together.</li>
          <li class="enquiry" data-en="Researchers or clinicians with an international project or study in mind, who know the question they want to ask but not how a collaboration across two systems is set up, funded and kept going. Some of this we can answer from experience. Some of it we work out together." data-ja="海外との共同プロジェクトや研究を考えている研究者・臨床家から。問いは決まっているが、二つの制度をまたぐ協働をどう立ち上げ、どう資金を得て、どう続けるかが分からない、というご相談です。経験から答えられる部分もあれば、一緒に考えながら進める部分もあります。">Researchers or clinicians with an international project or study in mind, who know the question they want to ask but not how a collaboration across two systems is set up, funded and kept going. Some of this we can answer from experience. Some of it we work out together.</li>
        </ul>
        <p class="enquiries-note" data-en="Not every enquiry is a fit. Where it is not, we say so, and where we can we point to someone better placed." data-ja="すべてのご相談をお受けできるわけではありません。適さない場合はその旨をお伝えし、可能であればより適した方をご紹介します。">Not every enquiry is a fit. Where it is not, we say so, and where we can we point to someone better placed.</p>
```

- [ ] **Step 4: style.css に規則を追加する**

`.areas li:nth-child(4) { … }` の行の直後、`/* ---------- founder ---------- */` の前に挿入する。

```css
/* ---------- examples of enquiries ---------- */
/* deliberately not cards: the four areas above are the taxonomy; these three
   cut across it. Equal visual weight would read as a fifth area. The rules are
   borders, not the dot divider, because the divider is hidden in print and the
   separation has to survive the reference copy. */
.enquiries-title {
  margin-top: 2.6rem;
  padding-top: 2.6rem;
  border-top: 1px solid var(--line);
  font-size: var(--t-sm);
  font-weight: 600;
  color: var(--ink);
}
.enquiries {
  margin-top: 1.2rem;
  max-width: 66ch;
}
.enquiries li {
  border-left: 2px solid var(--card-accent);
  padding-left: 1.15rem;
  font-size: var(--t-sm);
  color: var(--muted-text);
}
.enquiries li + li { margin-top: 1.15rem; }
.enquiries li:nth-child(1) { --card-accent: var(--mint); }
.enquiries li:nth-child(2) { --card-accent: var(--peri); }
.enquiries li:nth-child(3) { --card-accent: var(--peach); }
.enquiries-note {
  margin-top: 1.6rem;
  max-width: 66ch;
  font-size: var(--t-sm);
  color: var(--muted-text);
}
```

`@media print { … }` ブロック内、`.section { padding-block: 1.2rem; }` の行の直後に1行足す。

```css
  /* the pastel rules go grey on a mono printer; force ink so the three
     enquiries stay visibly separate on paper */
  .enquiries li { border-left-color: #000; }
```

- [ ] **Step 5: 実行して通ることを確認する**

Run: `python3 tools/verify_lp_copy.py`

Expected: 終了コード 0。`index.html copy guard: OK (N translatable nodes)`。N は Task 1 の値より 5 大きい。

- [ ] **Step 6: コミット**

```bash
git add tools/verify_lp_copy.py index.html style.css
git commit -m "Add the enquiry examples under Areas of activity

The four areas name what we do; they do not let a reader tell whether
their own situation belongs there. Three enquiries we actually receive
sit below them, as an annotation rather than a fifth area, and the block
closes by saying we do not take everything."
```

---

### Task 3: 描画と印刷を実機で確認する

**Files:**
- Create: `/private/tmp/claude-501/-Users-user/1d48a8a7-af7c-44e9-884b-4b60bf7dfe0d/scratchpad/probe.html`（一時ファイル。リポジトリには入れない）
- Modify: 不具合が出た場合のみ `style.css`

**Interfaces:**
- Consumes: Task 2 で完成した `index.html` と `style.css`
- Produces: なし（確認のみ）

- [ ] **Step 1: 横スクロール検出用のプローブを作る**

`index.html` のコピーに計測スクリプトを足したものを scratchpad に置く。相対パス（`style.css` / `script.js` / `assets/`）を解決させるため、コピーはリポジトリ直下に置き、確認後に削除する。

```bash
cd /Users/user/Documents/GitHub/cocolourlife
python3 - <<'PY'
from pathlib import Path
src = Path("index.html").read_text(encoding="utf-8")
probe = """<script>
(function () {
  var d = document.documentElement;
  function over() { return d.scrollWidth - d.clientWidth; }
  var out = 'en:' + over();
  var ja = document.querySelector('.lang-btn[data-lang="ja"]');
  if (ja) { ja.click(); out += ' ja:' + over(); }
  document.body.setAttribute('data-probe', out);
})();
</script>
</body>"""
Path("_probe.html").write_text(src.replace("</body>", probe), encoding="utf-8")
print("wrote _probe.html")
PY
```

- [ ] **Step 2: 4つの幅で横スクロールが出ないことを確認する**

```bash
cd /Users/user/Documents/GitHub/cocolourlife
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
for W in 360 600 900 1400; do
  printf "%s: " "$W"
  "$CHROME" --headless --disable-gpu --no-sandbox \
    --window-size=$W,2400 --virtual-time-budget=3000 --dump-dom \
    "file://$PWD/_probe.html" 2>/dev/null \
    | grep -o 'data-probe="[^"]*"' | head -1
done
```

Expected: 4行すべてが `data-probe="en:0 ja:0"`。0 以外なら、その幅で横スクロールが発生している。

注: headless はネットワークなしで動くため Google Fonts は読まれず、フォールバック書体で計測される。日本語のフォールバックは指定書体より字幅が広いことが多いので、この計測は**厳しめに出る**。0 なら実機でも安全と読んでよい。

- [ ] **Step 3: 4つの幅のスクリーンショットを撮って目で確認する**

```bash
cd /Users/user/Documents/GitHub/cocolourlife
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT=/private/tmp/claude-501/-Users-user/1d48a8a7-af7c-44e9-884b-4b60bf7dfe0d/scratchpad
for W in 360 600 900 1400; do
  "$CHROME" --headless --disable-gpu --no-sandbox \
    --window-size=$W,2400 --virtual-time-budget=3000 \
    --screenshot="$OUT/lp-$W.png" "file://$PWD/index.html" 2>/dev/null
done
ls -la "$OUT"/lp-*.png
```

4枚を Read ツールで開き、次を確認する。

1. 支援例の3項目がカードに見えないこと（背景の面がなく、左に細い縦罫だけ）
2. 4カードと支援例の間にヘアラインが1本入っていること
3. 900px と 1400px で、左レールの "Areas of activity" が sticky のまま支援例の高さぶん追随すること
4. 360px で縦罫と本文が詰まりすぎていないこと

- [ ] **Step 4: 印刷版に支援例が残ることを確認する**

```bash
cd /Users/user/Documents/GitHub/cocolourlife
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT=/private/tmp/claude-501/-Users-user/1d48a8a7-af7c-44e9-884b-4b60bf7dfe0d/scratchpad
"$CHROME" --headless --disable-gpu --no-sandbox --virtual-time-budget=3000 \
  --print-to-pdf="$OUT/lp.pdf" --no-pdf-header-footer \
  "file://$PWD/index.html" 2>/dev/null
python3 - <<PY
import fitz
doc = fitz.open("$OUT/lp.pdf")
text = "".join(p.get_text() for p in doc)
drawings = sum(len(p.get_drawings()) for p in doc)
need = ["Examples of enquiries we receive",
        "Not every enquiry is a fit",
        "A company or research group whose healthcare product"]
missing = [n for n in need if n not in text]
print("pages", doc.page_count, "| drawings", drawings, "| missing", missing)
raise SystemExit(0 if not missing and drawings >= 4 else 1)
PY
```

Expected: 終了コード 0。`missing []` で `drawings` が 4 以上（ヘアライン1本＋縦罫3本が最低ライン。カードの枠も数に入るので実際はもっと多い）。

- [ ] **Step 5: 一時ファイルを消す**

```bash
cd /Users/user/Documents/GitHub/cocolourlife && rm -f _probe.html && git status --short
```

Expected: `_probe.html` が出てこないこと。`tools/build_logo.py` と `tools/verify_logo.py` の既存の未コミット変更だけが残る。

- [ ] **Step 6: 不具合を直した場合のみコミット**

Step 2 から 4 で修正が必要になった場合のみ。

```bash
git add style.css
git commit -m "Fix <what broke> found in cross-width verification"
```

修正が不要だった場合はコミットしない。

---

### Task 4: MVV仕様書に判断を追記する

**Files:**
- Modify: `/Users/user/Desktop/Yuho Vault/20_Projects/Cocolour Life/CoColour Life MVV・ポジショニング 2026-08.md`

**Interfaces:**
- Consumes: 設計書 §3 の判断
- Produces: なし

MVV仕様書 §4 は「サービスページ追加なし／CTA追加なし」を定め、スコープ外に「顧客獲得型LPへの改修（2027年の再評価まで凍結）」を置いている。本作業はそこに触れるので、なぜ内側に収まると判断したのかを仕様書側に残す。残さないと、次に §4 を読んだ人が矛盾と受け取る。

- [ ] **Step 1: §4 の表に行を足す**

`| 5 | ロゴ段落追加（2026-08-17） | …` の行の直後に足す。

```markdown
| 6 | 支援例ブロック追加（2026-08-27） | `#activities` の4カードの下に「いただくご相談の例」（小見出し＋3例＋結び）を追加し、①③のカテゴリ説明文を書き直し。**サービスページではなく既存カテゴリの注釈**として扱う。第三者記述の事実のみ／CTAなし／料金・実績数値・お客様の声なし の3条件で §4-4「変更しないこと」の内側に収まると判断（2026-08-27 Yuho承認）。設計書: `cocolourlife/docs/superpowers/specs/2026-08-27-lp-enquiry-examples-design.md` |
```

- [ ] **Step 2: §5 の決定ログに行を足す**

`| 進め方 | 案2（LP＋vaultノート＋計画書改訂メモの整合化） | 公式文書間の矛盾を残さない |` の直後に足す。

```markdown
| 支援例の追加（2026-08-27） | 4カテゴリの下に独立ブロックで3例を追加（カードにしない） | 4カテゴリは供給側の言葉で、読み手が自分の案件の該当を判断できない。3例は4カテゴリを横断するのでカード内に埋めると割り当てに無理が出る。信用確認が主目的なので、供給側の分類を先に置き具体を後に足す順が素直 |
| 支援例の文体（2026-08-27） | 一人称の悩み調を使わず第三者記述。ブロック末に「すべては受けられない」を置く | 信用確認の場で集客LPの語り口を混ぜると、記述全体の信頼性が割り引かれる。観察ノート §5「豪州を売り込まない」に沿う |
```

- [ ] **Step 3: 更新日を直す**

frontmatter の `updated: 2026-08-17` を `updated: 2026-08-27` にする。

- [ ] **Step 4: vault 側をコミットする**

vault は git リポジトリで、obsidian-git が同期している。編集を確定させる。

```bash
cd "/Users/user/Desktop/Yuho Vault"
git add "20_Projects/Cocolour Life/CoColour Life MVV・ポジショニング 2026-08.md"
git commit -m "MVV: 支援例ブロックの追加判断を記録（2026-08-27）"
```

- [ ] **Step 5: 実装ブランチの状態を報告する**

```bash
cd /Users/user/Documents/GitHub/cocolourlife
python3 tools/verify_lp_copy.py && python3 tools/verify_brand.py && git log --oneline main..HEAD
```

Expected: 両ガードが 0 で終了し、`lp-enquiry-examples` に3〜4コミット。**push はしない。** Yuho に差分とスクリーンショットを見せ、デプロイの判断を仰ぐ。

---

## Self-Review

**1. Spec coverage**

| 設計書 | 対応タスク |
|---|---|
| §6.1 4カテゴリの説明文 | Task 1 |
| §6.2 支援例ブロック | Task 2 |
| §6.3 "regulatory" を書かない | Task 1・2 の文面定数に反映済み（承認文面をそのまま定数化） |
| §7.1 ドットディバイダを使わない | Task 2 Step 4（border による区切り）、`check_css` の print ブロック検査 |
| §7.2 DOM 構造 | Task 2 Step 3 |
| §7.3 既存レイアウトとの適合（変更不要） | Task 3 Step 3 の目視項目3 |
| §7.4 i18n の制約 | Task 1 の `check_i18n_invariants` |
| §7.5 見た目 | Task 2 Step 4、`check_css` の card chrome 検査 |
| §7.6 印刷 | Task 2 Step 4、Task 3 Step 4 |
| §8 完了条件 1〜6 | 1・2 → Task 1/2 のガード、3 → Task 3 Step 2、4 → Task 3 Step 4、5 → Task 3 Step 2（ja の計測）と Step 3、6 → Task 1/2 の `check_no_em_dash` |
| §3 MVV仕様書への追記 | Task 4 |

未対応なし。

**2. Placeholder scan**

`TBD` / `TODO` / 「適切に」「必要に応じて」の類はなし。全ステップにコマンドまたはコードの実体がある。Task 3 Step 6 の「不具合を直した場合のみ」は条件分岐であってプレースホルダではなく、条件と対象ファイルを明示している。

**3. Type consistency**

- `Doc` / `parse` / `_by_class` / `check_i18n_invariants` / `check_no_em_dash` / `main` は Task 1 で定義し、Task 2 が同じ名前で参照している。
- `check_css` は `CSS` を使う。Task 2 Step 1 で `CSS = ROOT / "style.css"` の追加を明示した。
- クラス名は `enquiries-title` / `enquiry` / `enquiries-note` / `enquiries` で、ガード・HTML・CSS の3箇所すべてで一致。`li` には `enquiry`（単数）、`ul` には `enquiries`（複数）を付ける点が紛れやすいので、Task 2 Step 3 の HTML で両方を明示した。
- `check_no_em_dash(nodes, classes)` の第2引数は Task 1 で `["area-desc"]`、Task 2 で4クラスに拡張。シグネチャは不変。
