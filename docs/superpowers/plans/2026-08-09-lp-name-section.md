# CoColour Life LP改訂（名前セクション・略歴・プレースホルダ解消）Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 承認済み仕様書（vault: `20_Projects/Cocolour Life/CoColour Life MVV・ポジショニング 2026-08.md`）に基づき、redesignブランチのLPに「名前に込めた想い」セクションを追加し、Founder略歴に臨床一文を加え、ABN/LinkedInプレースホルダを解消し、事業計画書の改訂メモを作成する。

**Architecture:** 静的サイト（index.html + style.css + script.js）。バイリンガルは `data-en`/`data-ja` 属性方式で、`script.js` が `[data-en][data-ja]` を自動検出するため、**新規要素は属性を付けるだけで言語切替に対応する**（JS変更不要）。デフォルトのテキストノードは英語（JS無効時のフォールバック）。

**Tech Stack:** HTML/CSS（フレームワークなし）、git（redesignブランチ）、python-docx（改訂メモ生成）

## Global Constraints

- 作業ブランチ: `redesign`（`~/Documents/GitHub/cocolourlife`）。mainには触れない
- トーン: 現サイトの抑制的な品位を維持。太字・絵文字・マーケティング文言を追加しない
- `<meta name="robots" content="noindex, nofollow" />`（L8）は**削除しない**（公開判断まで維持）
- コピーは仕様書§2の正典コピーを一字一句使用（勝手に「改善」しない）
- 臨床への言及はFounder略歴の事実記述一文のみ。サービス・料金・効果の記載は追加しない（AHPRA広告非該当を維持）
- 解析・トラッキングを追加しない
- 各タスク完了ごとにコミット。pushはYuhoの確認後のみ（pushするとVercelプレビューが更新される）

---

### Task 1: ABN・ACNの確認（実装の前提情報収集）

**Files:**
- Read: `/Users/user/Desktop/Cocolour Life/company_registration.pdf`
- Read: `/Users/user/Desktop/Cocolour Life/202606 Engagement letter (COCOLOUR LIFE).pdf`（前者に無い場合）

**Interfaces:**
- Produces: 実ABN（`NN NNN NNN NNN` 形式・11桁）→ Task 4が使用

- [ ] **Step 1: 登記書類からACN/ABNを抽出**

ReadツールでPDFを読み、ACN（9桁）とABN（11桁）を探す。

- [ ] **Step 2: ABR公式でABNをクロス検証**

WebFetchまたはWebSearchで `abr.business.gov.au` の「CoColour Life Pty Ltd」検索結果と照合。**書類とABRが一致した場合のみ確定**。ABNが書類に無くABR検索でも特定できない場合は、Yuhoに直接確認する（推測で埋めない）。

Expected: `ABN = NN NNN NNN NNN`（確定値）をタスクの結果として記録

---

### Task 2: 「Our name / 名前に込めた想い」セクション追加

**Files:**
- Modify: `index.html:125-127`（Aboutセクション閉じタグ直後、AREAS OF ACTIVITYコメントの前に挿入）
- Modify: `style.css`（末尾に `.name-coda` ルールを追加）

**Interfaces:**
- Consumes: 仕様書§2の正典コピー（下記に転記済み）
- Produces: `<section id="name">` — 後続タスクからの依存なし

- [ ] **Step 1: index.htmlにセクションを挿入**

`index.html` の L125（`</section>` = Aboutの閉じ）と L127（`<!-- ===== AREAS OF ACTIVITY ===== -->`）の間に、以下をそのまま挿入する:

```html
    <!-- ===== OUR NAME ===== -->
    <section class="section" id="name">
      <div class="wrap">
        <h2 class="section-title" data-en="Our name" data-ja="名前に込めた想い">Our name</h2>
        <p class="lead"
           data-en="“Co” is how we work: collaboration, co-design and growing together. Nothing meaningful is created alone."
           data-ja="「Co」は、私たちの働き方です。コラボレーション、共同デザイン、そして共に成長すること。意味のあるものは、ひとりでは創れません。">“Co” is how we work: collaboration, co-design and growing together. Nothing meaningful is created alone.</p>
        <p class="lead"
           data-en="“Colour” is what we work for: everyday lives rich in the occupations that make each person who they are; services and collaboration that reach people of diverse cultures and backgrounds; and the conviction that we do not add colour to people’s lives — we create colour together."
           data-ja="「Colour」は、私たちが目指すものです。一人ひとりが、その人らしい日常の彩りに参加できること。多様な文化や背景を持つ人々に、サービスと協働が届くこと。そして——私たちは人の人生に色を添えるのではなく、共に色を創ります。">“Colour” is what we work for: everyday lives rich in the occupations that make each person who they are; services and collaboration that reach people of diverse cultures and backgrounds; and the conviction that we do not add colour to people’s lives — we create colour together.</p>
        <p class="name-coda"
           data-en="In Japanese, CoColour sounds like kokkara — “from here.” Life starts from here."
           data-ja="そして日本語では、CoColourは「こっから」と聞こえます。こっからライフ — 人生は、ここから。">In Japanese, CoColour sounds like kokkara — “from here.” Life starts from here.</p>
      </div>
    </section>
```

設計判断メモ: クラスは既存の `section`（無着色）を使う。About（無着色）と連続するが、AboutとOur nameは一続きの物語として読まれるため許容（交互着色の全面組み替えはYAGNI）。

- [ ] **Step 2: style.css末尾にコーダ用ルールを追加**

`style.css` の末尾に追加:

```css
/* Our name — closing line (kokkara) */
.name-coda {
  margin-top: 1.4em;
  font-weight: 600;
}
```

- [ ] **Step 3: 構文・言語パリティ検証**

Run:
```bash
cd ~/Documents/GitHub/cocolourlife && python3 - <<'EOF'
import re
src = open('index.html').read()
en = len(re.findall(r'data-en="', src)); ja = len(re.findall(r'data-ja="', src))
assert en == ja, f"EN/JA attribute mismatch: {en} vs {ja}"
assert 'id="name"' in src and 'kokkara' in src and 'こっから' in src
print(f"OK: data-en={en}, data-ja={ja}, name section present")
EOF
```
Expected: `OK: data-en=..., data-ja=...`（en=jaで一致）

- [ ] **Step 4: ブラウザ目視確認**

Run: `open ~/Documents/GitHub/cocolourlife/index.html`
Expected: About直後に「Our name」。EN/日本語トグルで両言語表示、コーダ行がやや強調される

- [ ] **Step 5: Commit**

```bash
cd ~/Documents/GitHub/cocolourlife && git add index.html style.css && git commit -m "Add 'Our name' section: Co / three colours / kokkara coda (EN+JA)"
```

---

### Task 3: Founder略歴に臨床一文を追加

**Files:**
- Modify: `index.html:147-149`（`.founder-bio` の data-en / data-ja / デフォルトテキストの3箇所）

**Interfaces:**
- Consumes: 仕様書§4-2の確定文言（下記）

- [ ] **Step 1: 3箇所に文を追加**

`data-en` 属性値の末尾 `...reach everyday health and rehabilitation practice.` の直後に追加:
`He continues to maintain a small clinical practice.`

`data-ja` 属性値の末尾 `...CoColour Lifeを設立。` の直後に追加:
`現在も、小規模な臨床実践を続けている。`

要素のデフォルトテキスト（タグ内側）にも同じ英文を追加（JS無効時のフォールバック一致のため）。

- [ ] **Step 2: 検証**

Run:
```bash
cd ~/Documents/GitHub/cocolourlife && grep -c "small clinical practice" index.html && grep -c "小規模な臨床実践" index.html
```
Expected: `2`（data-en+デフォルトテキスト）と `1`（data-ja）

- [ ] **Step 3: Commit**

```bash
cd ~/Documents/GitHub/cocolourlife && git add index.html && git commit -m "Founder bio: add factual sentence on ongoing small clinical practice (EN+JA)"
```

---

### Task 4: プレースホルダ解消（ABN・LinkedIn URL）

**Files:**
- Modify: `index.html:189`（footer ABN）
- Modify: `index.html:151` および `index.html:194`（`[LinkedIn URL]` ×2）

**Interfaces:**
- Consumes: Task 1の確定ABN。LinkedIn URLは**Yuhoに確認**（vault/CVに記録なし。確認できるまでこのステップは保留可）

- [ ] **Step 1: ABN差し替え**

L189の `ABN XX XXX XXX XXX` を Task 1 の確定値に置換。

- [ ] **Step 2: LinkedIn URL差し替え（YuhoからURL取得後）**

L151・L194の `[LinkedIn URL]` を実URLに置換。未取得の場合はこのステップをスキップし、未解消として報告する（noindexが維持されているため公開事故はない）。

- [ ] **Step 3: 検証**

Run:
```bash
cd ~/Documents/GitHub/cocolourlife && ! grep -n "XX XXX XXX XXX" index.html && grep -c "linkedin.com" index.html || echo "REMAINING PLACEHOLDERS — report to Yuho"
```
Expected: ABNプレースホルダ0件。LinkedInは2件（または保留の報告）

- [ ] **Step 4: Commit**

```bash
cd ~/Documents/GitHub/cocolourlife && git add index.html && git commit -m "Replace ABN (and LinkedIn) placeholders with verified values"
```

---

### Task 5: 事業計画書の改訂メモ（アドレンダム）作成

**Files:**
- Create: `/Users/user/Desktop/Cocolour life Claude AI/Co-Colour Life 2026事業計画書_改訂メモ_2026-08.docx`
- Modify: vault `20_Projects/Cocolour Life/Cocolour Life Dashboard.md`（タスクのチェック）

設計判断メモ: 元のdocx（26ページ・整形済み）を直接編集すると書式破損リスクがあるため、**別ファイルのアドレンダム**とする（仕様書§3の意図=「矛盾を公式文書に残さない」はアドレンダム+Dashboard参照で満たす）。

- [ ] **Step 1: python-docxでアドレンダム生成**

内容（1ページ、体裁は `~/.claude/skills/md-to-word/scripts/convert.py` のスタイルを流用してもよい）:

```text
Co-Colour Life 2026事業計画書 — 改訂メモ（2026年8月）

本メモはStrategic Blueprint 2026–2035（2026年6月版）の以下の改訂を記録する。
詳細な決定過程はObsidian vault「CoColour Life MVV・ポジショニング 2026-08」参照。

1. Phase 1（2026–27）の改訂
   旧: 臨床エンジン先行（mobile/telehealth OT+PT、25–40クライアント、損益分岐）
   新: 「静かな信頼性」戦略 — 知識柱の種まき＋最小臨床（週数時間・自費・紹介のみ）。
   理由: 博士審査とアカデミアキャリア（大学勤務）を最優先するため、臨床・商業を
   前面に出さない。臨床スケールの判断はPhD取得＋ANU着任後（2027年）に再評価。

2. Valuesの「colour」を3層に拡張
   ①日常の彩り（everyday occupationsへの参加支援・個人レベル）
   ②人と文化の彩り（多様な文化・背景を持つ人々への日本企業のサービス・協働支援）
   ③共に創る彩り（原文の "we create colour together" を頂点として維持）

3. 名前の音（コーダ）の追加
   日本語でCoColourは「こっから」— こっからライフ、人生は、ここから。
   （Life starts from here.）LPの名前セクション結びに採用。

Mission・Vision・4本柱・10年ビジョンは変更なし。
```

- [ ] **Step 2: 生成物を開き直して検証**

python-docxで再度開き、段落数>0・上記3項目の見出し文字列が含まれることをassertする。

- [ ] **Step 3: vault Dashboardのタスクをチェック**

`20_Projects/Cocolour Life/Cocolour Life Dashboard.md` の「事業計画書…改訂メモを追記」を `[x]` に更新し、アドレンダムのパスを記載。vault側は `git add`（当該2ファイルのみ）+ commit。

---

### Task 6: 最終検証とプレビュー反映の確認依頼

**Files:** なし（検証のみ）

- [ ] **Step 1: 全体検証**

Run:
```bash
cd ~/Documents/GitHub/cocolourlife && python3 - <<'EOF'
import re
src = open('index.html').read()
en = len(re.findall(r'data-en="', src)); ja = len(re.findall(r'data-ja="', src))
checks = {
  'EN/JA parity': en == ja,
  'name section': 'id="name"' in src,
  'kokkara EN': 'Life starts from here' in src,
  'kokkara JA': 'こっからライフ' in src,
  'clinical sentence': 'small clinical practice' in src,
  'no ABN placeholder': 'XX XXX XXX XXX' not in src,
  'noindex kept': 'noindex' in src,
}
for k, v in checks.items(): print(('✓' if v else '✗'), k)
assert all(checks.values())
EOF
git log --oneline -5
```
Expected: 全項目✓、コミット履歴にTask 2-4の3コミット

- [ ] **Step 2: Yuhoへ報告し、push可否を確認**

pushするとVercelプレビュー（redesignブランチ）が更新される。**Yuhoの明示的な確認を得てから** `git push origin redesign` を実行する。未確認のままpushしない。
