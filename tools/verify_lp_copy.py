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
CSS = ROOT / "style.css"

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
    ("Programme and service evaluation, health workforce and cost analysis, and "
     "implementation research. Evaluation work is delivered as a report setting "
     "out what worked, what did not, and what the evidence does not yet cover.",
     "プログラム・サービスの評価、保健医療人材と費用の分析、実装研究。評価の成果物は、"
     "何が機能し、何が機能しなかったか、そしてエビデンスがまだ及んでいない範囲を"
     "書いた報告書です。"),
    ("Lectures, workshops and teaching materials, in English and Japanese. "
     "Existing material is rebuilt for the setting where it will be used rather "
     "than translated as it stands.",
     "講義・研修・教材の作成。英語と日本語の両方で行います。既存の教材は、そのまま"
     "訳すのではなく、使われる現場に合わせて作り直します。"),
    ("Advisory work with health services, universities and industry: shaping a "
     "project before it starts, or reviewing one already running. The "
     "number we take on at a time is limited.",
     "医療サービス・大学・企業への助言。企画が始まる前の設計や、進行中の案件の点検を"
     "行います。同時にお受けする件数は限られます。"),
    ("Exchange of evidence, models of care and technology in both directions. "
     "Most of the effort goes into working out what has to change for something "
     "that works in one country to work under the funding and service "
     "arrangements of the other.",
     "エビデンス・ケアモデル・テクノロジーの双方向の交流。労力の大半は、一方の国で"
     "機能しているものが、もう一方の国の制度と資金の仕組みの下でも機能するには何を"
     "変える必要があるかを詰めることに使われます。"),
]


# ---- approved copy, spec §6.2 ------------------------------------------------

ENQUIRIES_TITLE = ("Examples of past enquiries", "これまでのご相談の例")

# each item is (lead EN, lead JA, detail EN, detail JA). The lead is a short
# scan line so a reader can find the case that matches theirs without reading
# all three in full; the detail is the copy approved on 2026-08-27, uncut.
ENQUIRIES = [
    ("Taking a product or service into another country.",
     "製品やサービスの、別の国への展開",
     "A company or research group with a healthcare product or service already "
     "in use in one country, looking to introduce it in another. What "
     "they usually need first is a clear account of the evidence they will be "
     "asked for, and of the conditions in the setting where it would be used.",
     "ある国ですでに使われている医療・ヘルスケアの製品やサービスを、別の国で"
     "展開したい企業・研究グループから。最初に必要になるのはたいてい、導入先で"
     "求められるエビデンスと、実際に使われる現場の条件を把握することです。"),
    ("Introducing a way of working to the other country.",
     "取り組みの、もう一方の国への紹介",
     "A practitioner or organisation who has seen a way of working take hold in "
     "Australia, or in Japan, and wants to bring it to the other country with "
     "colleagues there rather than on their own. In practice this often means "
     "joint presentations, co-authored writing, and rebuilding existing "
     "material together.",
     "オーストラリア（あるいは日本）の現場で定着している取り組みを、もう一方の国に"
     "紹介したい実践者・団体から。ひとりで進めるのではなく、現地の人たちと一緒に"
     "進めたいというご相談です。実際の作業は、共同での発表や執筆、既存の教材を"
     "一緒に作り直すことが多くなります。"),
    ("Setting up an international project or study.",
     "国際的なプロジェクト・研究の立ち上げ",
     "Researchers or clinicians with an international project or study in mind, "
     "who know the question they want to ask but not how a collaboration across "
     "two systems is set up and kept going. We can answer some of this from "
     "experience. Some of it we work out together.",
     "海外との共同プロジェクトや研究を考えている研究者・臨床家から。問いは決まって"
     "いるが、二つの制度をまたぐ協働をどう立ち上げ、どう続けるかが分からない、という"
     "ご相談です。経験から答えられる部分もあれば、一緒に考えながら進める部分も"
     "あります。"),
]

ENQUIRIES_NOTE = (
    "Not every enquiry is a fit. Where it is not, we say so, and, where we can, "
    "we point to someone better placed.",
    "すべてのご相談をお受けできるわけではありません。適さない場合はその旨をお伝えし、"
    "可能であればより適した先をお示しします。",
)


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

    leads = _by_class(nodes, "enquiry-lead")
    details = _by_class(nodes, "enquiry-detail")
    if len(leads) != 3 or len(details) != 3:
        failures.append(
            "expected 3 .enquiry-lead and 3 .enquiry-detail, found {} and {}"
            .format(len(leads), len(details)))
    else:
        for i, (lead_en, lead_ja, det_en, det_ja) in enumerate(ENQUIRIES):
            for got, want, what in ((leads[i], (lead_en, lead_ja), "lead"),
                                    (details[i], (det_en, det_ja), "detail")):
                if got["en"] != want[0] or got["ja"] != want[1]:
                    failures.append(
                        "enquiry {} {}: not the approved copy\n    found EN: {!r}"
                        .format(i + 1, what, got["en"]))

    notes = _by_class(nodes, "enquiries-note")
    if len(notes) != 1:
        failures.append(
            "expected 1 .enquiries-note, found {}".format(len(notes)))
    else:
        en, ja = ENQUIRIES_NOTE
        if notes[0]["en"] != en or notes[0]["ja"] != ja:
            failures.append(".enquiries-note is not the approved copy")

    # the block must carry no call to action of any kind (spec §2)
    html = HTML.read_text(encoding="utf-8")
    start = html.find('<div class="enquiries-block">')
    end = html.find("</div>", start)
    if start == -1 or "<a " in html[start:end]:
        failures.append(
            "the enquiries block must hold no links: it is an annotation, not "
            "a call to action")
    return failures


def check_css():
    css = CSS.read_text(encoding="utf-8")
    failures = []

    required = [
        (".enquiries-title", "border-top: 1px solid var(--line)"),
        (".enquiries li", "border-left: 2px solid var(--card-accent)"),
        # 66ch resolves against the element's own font-size, so the list
        # and the note must declare the same one or their measures drift
        (".enquiries {", "font-size: var(--t-sm)"),
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
    # the closing line qualifies the three examples, so a printed page must
    # never carry them without it
    if "break-inside: avoid" not in print_block:
        failures.append(
            "style.css: @media print must keep .enquiries-block together with "
            "break-inside: avoid")
    if '<div class="enquiries-block">' not in HTML.read_text(encoding="utf-8"):
        failures.append(
            "index.html: the enquiries block must stay wrapped in "
            ".enquiries-block, which is what the print rule holds together")

    # the soft ground circle every other body section carries
    if "#activities::before" not in css:
        failures.append(
            "style.css: #activities must carry the same soft ground circle as "
            "the hero, founder and contact sections")
    elif "#activities::before" not in print_block:
        failures.append(
            "style.css: @media print must hide #activities::before, as it does "
            "the other ground circles")

    # no card chrome: that is what tells a reader these are not a fifth area
    block = css.split("examples of enquiries")[-1].split("/* ----------")[0]
    for banned in ("background:", "border-radius:", "var(--surface)"):
        if banned in block:
            failures.append(
                "style.css: the enquiries block must carry no card chrome, "
                "found {}".format(banned))
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
    failures += check_enquiries(nodes)
    failures += check_no_em_dash(
        nodes, ["area-desc", "enquiries-title", "enquiry-lead", "enquiry-detail",
                "enquiries-note"])
    failures += check_css()

    if failures:
        print("index.html copy guard: {} failure(s)\n".format(len(failures)))
        for f in failures:
            print("  - {}".format(f))
        return 1
    print("index.html copy guard: OK ({} translatable nodes)".format(len(nodes)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
