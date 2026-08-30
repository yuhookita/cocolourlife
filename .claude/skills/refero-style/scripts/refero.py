#!/usr/bin/env python3
"""styles.refero.design の公開 JSON API を叩く小道具。

  refero.py list   [--pages 3]
  refero.py search "calm clinical, navy, serif" [--pages 3] [--top 5]
  refero.py get    <id|https://styles.refero.design/style/UUID> [--json] [-o DESIGN.md]
  refero.py selftest          # ネットワーク不要。整形処理だけを検証する

API は公開されているが非公式（refero-styles-mcp-server が使っているエンドポイントと
同じもの）。応答の形が変わったら references/api.md を直してからここを直す。
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

API = os.environ.get("REFERO_API", "https://styles.refero.design/api")
SITE = "https://styles.refero.design"
UA = "refero-style-skill/1.0"
TIMEOUT = 30
CACHE_TTL = 24 * 3600
CACHE = Path(os.environ.get("XDG_CACHE_HOME", str(Path.home() / ".cache"))) / "refero-styles"

# 日本語の指示語 → API 側の英語表現。search のヒット率のためだけの薄い辞書。
MOOD_JA = {
    "落ち着": "calm quiet restrained",
    "静か": "quiet minimal",
    "余白": "minimal spacious",
    "ミニマル": "minimal",
    "医療": "health clinical care",
    "臨床": "clinical",
    "学術": "academic editorial research",
    "研究": "research academic",
    "信頼": "trust professional",
    "誠実": "honest professional",
    "温か": "warm friendly",
    "やさし": "soft friendly warm",
    "親しみ": "friendly approachable",
    "高級": "premium luxury refined",
    "上品": "refined elegant",
    "遊び": "playful bold",
    "力強": "bold strong",
    "ダーク": "dark",
    "暗": "dark",
    "明る": "light bright",
    "白基調": "light white",
    "企業": "corporate saas",
    "SaaS": "saas product",
    "ランディング": "landing marketing",
    "教育": "education learning",
    "セリフ": "serif",
    "明朝": "serif",
    "ゴシック": "sans",
    "サンセリフ": "sans",
}


# ---------------------------------------------------------------- HTTP + cache
def _cache_path(key: str) -> Path:
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", key)
    return CACHE / f"{safe}.json"


def fetch(path: str, use_cache: bool = True) -> dict:
    """GET {API}{path} を JSON で返す。24時間キャッシュ。"""
    cp = _cache_path(path)
    if use_cache and cp.exists() and time.time() - cp.stat().st_mtime < CACHE_TTL:
        return json.loads(cp.read_text(encoding="utf-8"))
    req = urllib.request.Request(
        API + path, headers={"Accept": "application/json", "User-Agent": UA}
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            data = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        sys.exit(f"[refero] HTTP {e.code} {API}{path} — API仕様が変わった可能性。references/api.md を確認。")
    except urllib.error.URLError as e:
        sys.exit(f"[refero] 接続失敗 {API}{path}: {e.reason}\n"
                 f"        （ネットワーク制限下では styles.refero.design に到達できないことがある）")
    if use_cache:
        CACHE.mkdir(parents=True, exist_ok=True)
        cp.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return data


def fetch_summaries(pages: int, use_cache: bool = True) -> list[dict]:
    out, page = [], 1
    while page <= pages:
        data = fetch(f"/styles?page={page}", use_cache)
        chunk = data.get("styles") or []
        if not chunk:
            break
        out.extend(chunk)
        nxt = data.get("nextPage")
        if not nxt:
            break
        page = nxt
    return out


# ------------------------------------------------------------------- matching
def _expand(query: str) -> str:
    q = query
    for ja, en in MOOD_JA.items():
        if ja in query:
            q += " " + en
    return q.lower()


def _tokens(text: str) -> set[str]:
    return {t for t in re.split(r"[^a-z0-9#]+", text.lower()) if len(t) > 2}


def _hexes(text: str) -> list[str]:
    return [h.lower() for h in re.findall(r"#[0-9a-fA-F]{6}", text)]


def _rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _dist(a: str, b: str) -> float:
    try:
        ra, ga, ba = _rgb(a)
        rb, gb, bb = _rgb(b)
    except ValueError:
        return 999.0
    return ((ra - rb) ** 2 + (ga - gb) ** 2 + (ba - bb) ** 2) ** 0.5


def score(style: dict, query: str) -> tuple[float, list[str]]:
    q = _expand(query)
    qt = _tokens(q)
    reasons: list[str] = []
    total = 0.0

    hay = " ".join([
        style.get("siteName", ""), style.get("northStar", ""),
        " ".join(style.get("fonts") or []),
        " ".join(c.get("name", "") for c in (style.get("colors") or [])),
    ])
    hit = qt & _tokens(hay)
    if hit:
        total += 2.0 * len(hit)
        reasons.append("語: " + ", ".join(sorted(hit)))

    scheme = (style.get("colorScheme") or "").lower()
    if scheme and scheme in qt:
        total += 2.0
        reasons.append(f"配色モード: {scheme}")

    for want in _hexes(query):
        near = min(
            ((_dist(want, c.get("hex", "")), c) for c in (style.get("colors") or [])),
            default=None, key=lambda p: p[0],
        )
        if near and near[0] < 90:
            total += 4.0 - near[0] / 30.0
            reasons.append(f"{want} ≈ {near[1].get('hex')} ({near[1].get('name','')})")

    for f in style.get("fonts") or []:
        if f.lower() in q:
            total += 2.0
            reasons.append(f"フォント: {f}")

    return total, reasons


# -------------------------------------------------------------- DESIGN.md 整形
def _bullets(items, fmt) -> list[str]:
    return [f"- {fmt(i)}" for i in items]


def render_design_md(style: dict) -> str:
    ds = ((style.get("fullResult") or {}).get("designSystem")) or {}
    name = style.get("siteName") or "(unnamed)"
    L: list[str] = [f"# {name} — design system", ""]

    meta = []
    if style.get("url"):
        meta.append(f"source: {style['url']}")
    if style.get("id"):
        meta.append(f"refero: {SITE}/style/{style['id']}")
    if style.get("colorScheme"):
        meta.append(f"scheme: {style['colorScheme']}")
    if meta:
        L += ["> " + " · ".join(meta), ""]

    north = ds.get("northStar") or style.get("northStar")
    if north:
        L += [f"**North star** — {north}", ""]
    if ds.get("description"):
        L += [ds["description"], ""]

    colors = ds.get("colors") or style.get("colors") or []
    if colors:
        L += ["## Colors", ""]
        for c in colors:
            bits = [f"`{c.get('hex','')}`", c.get("name", "")]
            if c.get("role"):
                bits.append(f"— {c['role']}")
            if c.get("group"):
                bits.append(f"({c['group']})")
            L.append("- " + " ".join(b for b in bits if b))
        L.append("")

    typo = ds.get("typography") or []
    if typo or style.get("fonts"):
        L += ["## Typography", ""]
        if typo:
            for t in typo:
                bits = [f"**{t.get('family','')}**"]
                if t.get("weights"):
                    bits.append("weights " + ", ".join(str(w) for w in t["weights"]))
                if t.get("fallback"):
                    bits.append(f"fallback: {t['fallback']}")
                L.append("- " + " — ".join(bits))
        else:
            L += _bullets(style.get("fonts") or [], lambda f: f)
        L.append("")

    scale = ds.get("typeScale") or []
    if scale:
        L += ["### Type scale", "",
              "| role | size | weight | line-height | letter-spacing |",
              "| --- | --- | --- | --- | --- |"]
        for s in scale:
            L.append("| {} | {} | {} | {} | {} |".format(
                s.get("role", ""), s.get("size", ""), s.get("weight", ""),
                s.get("lineHeight", ""), s.get("letterSpacing", "")))
        L.append("")

    sp = ds.get("spacing") or {}
    if sp:
        L += ["## Spacing & radius", ""]
        for k, v in sp.items():
            L.append(f"- {k}: {v}")
        L.append("")

    if ds.get("layout"):
        L += ["## Layout", "", ds["layout"], ""]

    surfaces = ds.get("surfaces") or []
    if surfaces:
        L += ["## Surfaces", ""]
        L += _bullets(surfaces, lambda s: " — ".join(
            x for x in [s.get("name", ""), s.get("color", ""), s.get("description", "")] if x))
        L.append("")

    elev = ds.get("elevation") or []
    if elev:
        L += ["## Elevation", ""]
        L += _bullets(elev, lambda e: " — ".join(
            x for x in [e.get("name", ""), e.get("shadow", "")] if x))
        L.append("")

    if ds.get("imagery"):
        L += ["## Imagery", "", ds["imagery"], ""]

    if ds.get("dos") or ds.get("donts"):
        L += ["## Principles", ""]
        L += _bullets(ds.get("dos") or [], lambda d: f"Do: {d}")
        L += _bullets(ds.get("donts") or [], lambda d: f"Don't: {d}")
        L.append("")

    comps = ds.get("components") or []
    if comps:
        L += ["## Components", ""]
        for c in comps:
            L.append(f"### {c.get('name','component')}")
            if c.get("description"):
                L += ["", c["description"]]
            if c.get("html"):
                L += ["", "```html", c["html"].strip(), "```"]
            if c.get("css"):
                L += ["", "```css", c["css"].strip(), "```"]
            L.append("")

    for sec in ds.get("customSections") or []:
        L += [f"## {sec.get('title','')}", "", sec.get("content", ""), ""]

    if not ds:
        L += ["_この style には fullResult.designSystem がなかった。"
              "上の色とフォントだけが確かな情報。_", ""]

    return "\n".join(L).rstrip() + "\n"


# ---------------------------------------------------------------- subcommands
def style_id(arg: str) -> str:
    m = re.search(r"[0-9a-fA-F-]{36}", arg)
    return m.group(0) if m else arg


def cmd_list(a) -> None:
    for s in fetch_summaries(a.pages, not a.no_cache):
        print(f"{s.get('id','')}  {s.get('siteName','')}  [{s.get('colorScheme','')}]  "
              f"{', '.join((s.get('fonts') or [])[:2])}")
        if s.get("northStar"):
            print(f"    {s['northStar']}")


def cmd_search(a) -> None:
    ranked = []
    for s in fetch_summaries(a.pages, not a.no_cache):
        sc, why = score(s, a.query)
        if sc > 0:
            ranked.append((sc, why, s))
    ranked.sort(key=lambda r: -r[0])
    if not ranked:
        print("該当なし。語を減らすか、--pages を増やす。")
        return
    for sc, why, s in ranked[: a.top]:
        print(f"{sc:5.1f}  {s.get('siteName','')}  [{s.get('colorScheme','')}]")
        print(f"       {SITE}/style/{s.get('id','')}")
        if s.get("northStar"):
            print(f"       {s['northStar']}")
        if why:
            print(f"       理由: {' / '.join(why)}")
        print()


def cmd_get(a) -> None:
    data = fetch(f"/styles/{style_id(a.id)}", not a.no_cache)
    detail = data.get("style") or data
    out = json.dumps(data, ensure_ascii=False, indent=2) if a.json else render_design_md(detail)
    if a.out:
        Path(a.out).write_text(out, encoding="utf-8")
        print(f"書き出した: {a.out} ({len(out)} bytes)")
    else:
        print(out)


FIXTURE = {
    "id": "00000000-0000-0000-0000-000000000000",
    "siteName": "Fixture Co", "url": "https://example.com",
    "colorScheme": "light", "northStar": "quiet clinical calm",
    "colors": [{"name": "Navy", "hex": "#1b1464"}],
    "fonts": ["Source Serif 4"],
    "fullResult": {"designSystem": {
        "description": "Test system.",
        "colors": [{"name": "Navy", "hex": "#1b1464", "role": "primary"}],
        "typography": [{"family": "Source Serif 4", "weights": [400, 600]}],
        "typeScale": [{"role": "h1", "size": "2.5rem", "lineHeight": "1.1"}],
        "spacing": {"radius": "8px", "pageMaxWidth": "820px"},
        "surfaces": [{"name": "card", "color": "#f6f6fa"}],
        "elevation": [{"name": "raised", "shadow": "0 1px 2px rgba(0,0,0,.06)"}],
        "dos": ["keep it quiet"], "donts": ["no gradients"],
        "components": [{"name": "Button", "css": ".btn{border-radius:8px}"}],
        "customSections": [{"title": "Motion", "content": "150ms ease-out."}],
    }},
}


def cmd_selftest(_a) -> None:
    md = render_design_md(FIXTURE)
    need = ["# Fixture Co", "## Colors", "`#1b1464`", "## Typography",
            "### Type scale", "| h1 | 2.5rem |", "## Spacing & radius", "radius: 8px",
            "## Surfaces", "## Elevation", "## Principles", "Do: keep it quiet",
            "Don't: no gradients", "### Button", "```css", "## Motion",
            f"{SITE}/style/00000000-0000-0000-0000-000000000000"]
    missing = [n for n in need if n not in md]
    sc, why = score(FIXTURE, "落ち着いた clinical #1B1464 Source Serif 4")
    if sc <= 0 or not why:
        missing.append("score() が日本語＋hex＋フォントの問い合わせに反応しない")
    if style_id(f"{SITE}/style/00000000-0000-0000-0000-000000000000") != FIXTURE["id"]:
        missing.append("style_id() が URL から UUID を取り出せない")
    if missing:
        print("FAIL:")
        for m in missing:
            print("  -", m)
        sys.exit(1)
    print(f"OK — 整形{len(md)}文字 / スコア{sc:.1f} ({'; '.join(why)})")
    print("（ネットワーク経路は selftest では検証していない）")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--no-cache", action="store_true", help="24時間キャッシュを使わない")
    sub = p.add_subparsers(dest="cmd", required=True)

    pl = sub.add_parser("list", help="スタイル一覧")
    pl.add_argument("--pages", type=int, default=3)
    pl.set_defaults(func=cmd_list)

    ps = sub.add_parser("search", help="語・気分・色・フォントで絞る")
    ps.add_argument("query")
    ps.add_argument("--pages", type=int, default=3)
    ps.add_argument("--top", type=int, default=5)
    ps.set_defaults(func=cmd_search)

    pg = sub.add_parser("get", help="1件を DESIGN.md にする")
    pg.add_argument("id", help="UUID か styles.refero.design/style/... のURL")
    pg.add_argument("--json", action="store_true", help="生JSONを出す")
    pg.add_argument("-o", "--out")
    pg.set_defaults(func=cmd_get)

    pt = sub.add_parser("selftest", help="ネット不要の整形テスト")
    pt.set_defaults(func=cmd_selftest)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
