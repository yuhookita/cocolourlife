---
name: refero-style
description: 実在サイトのデザインシステムを DESIGN.md 化した公開ライブラリ styles.refero.design（Refero Styles）から参照スタイルを探し、DESIGN.md を取り出し、いま作っている画面に適用する。トリガー例:「参考になるデザインを探して」「◯◯みたいなトーンで作って」「配色とタイポのトークンを決めて」「DESIGN.md がほしい」「refero を使って」。UI・LP・スライド等のビジュアル実装に着手する前の下ごしらえに使う。既存ブランドがある案件では色とロゴは既存を優先し、構造だけを借りる。
---

# Refero Styles を設計の下敷きにする

styles.refero.design は、実在サイトの見た目を「色・タイポ・余白・コンポーネント」に
分解して DESIGN.md 形式で置いてあるライブラリ。ゼロから配色を考える代わりに、
**成立している体系を1つ選んで下敷きにする**ために使う。

同梱の `scripts/refero.py` が公開 JSON API を叩く（依存なし・Python3 標準ライブラリのみ）。

## 手順

1. **探す** — 気分・用途・色・フォントで絞る。日本語の語もある程度は英語に展開される。

   ```bash
   python3 .claude/skills/refero-style/scripts/refero.py search "落ち着いた 医療 #1B1464 serif" --top 5
   ```

   ユーザーが既に候補ページの URL（`https://styles.refero.design/style/<UUID>`）を
   持っているなら、探す手順は飛ばす。

2. **取り出す** — 1件を DESIGN.md にする。作業用に保存してから読む。

   ```bash
   python3 .claude/skills/refero-style/scripts/refero.py get <UUID|URL> -o /tmp/DESIGN.md
   ```

   生 JSON が要るときは `--json`。応答は24時間キャッシュされる（`--no-cache` で無効化）。

3. **選んで適用する** — DESIGN.md を丸ごと貼らない。下の原則で取捨してから CSS に落とす。

4. **検証する** — 適用後に必ず実物を確認する（下記「検証」）。

## 何を借り、何を借りないか

| 借りてよい | 借りない |
|---|---|
| 型スケール・行間・字送りの比率 | ブランドカラーそのもの（既存ブランドがある場合） |
| 余白・角丸・最大幅のリズム | ロゴ、マーク、固有のイラスト表現 |
| 面（surface）と影の段階の作り方 | 参照元のコピー・文言・レイアウトの丸写し |
| do/don't に書かれた設計判断 | 参照元のブランド名を想起させる要素一式 |

参照元は実在企業のサイト。**体系の作り方を学ぶ対象であって、複製する対象ではない。**
「◯◯社そっくりにして」という依頼が来たら、そのまま作らずに、
どの性質（静けさ・密度・コントラスト）が欲しいのかに翻訳してから適用する。

## この repo（CoColour Life）で使うときの制約

- 配色は **ブランドブック p.9 の10色で確定済み**。`style.css` の `:root` が正のソース。
  Refero から色を持ち込まない。借りるのは型スケール・余白・面の設計だけ。
- パステル7色は本文色に使えない（白地で最大2.37:1）。ネイビーとクリムゾンのみ AA を通る。
- 変更したら必ず走らせる:

  ```bash
  python3 tools/verify_brand.py && python3 tools/verify_lp_copy.py
  ```

- 見た目は目で確認する: `ruby .claude/serve.rb` → http://localhost:8000

## 検証

- スクリプト自体の整形処理: `python3 .claude/skills/refero-style/scripts/refero.py selftest`（ネット不要）
- 適用後: コントラスト比の再計算（`tools/verify_brand.py` が担当）＋ ブラウザで実表示を確認。
  「DESIGN.md に書いてあったから」は根拠にならない。数値は自分で確かめる。

## うまくいかないとき

- **接続できない**（`Tunnel connection failed` 等）: ネットワーク制限のある環境では
  styles.refero.design に到達できない。ローカルの Claude Code から実行する。
- **HTTP 404 / 応答の形が違う**: API は非公式。`references/api.md` に観測した仕様がある。
  そこを直してからスクリプトを直す。最後の手段として style ページを WebFetch する。
- **API を使わず MCP で済ませたい**: 公式ではないが `faridjafarlee/refero-styles-mcp-server`
  という MCP サーバーがある。常用するならそちらを入れてもよい（このスキルと役割は重なる）。
