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
