# LP「いただくご相談の例」追加 — 設計書

作成日: 2026-08-27
対象: `~/Documents/GitHub/cocolourlife`（単一ページLP）／ `#activities` セクション
状態: 承認済み（2026-08-27、brainstormingセッション Yuho×Claude）

---

## 1. 背景と課題

現行の Areas of activity は4カテゴリのカードで構成されている。すべて「供給側の言葉」で書かれており、読み手が自分の状況と結びつけられない。

とくに次の2つは名詞句の羅列で、同業の研究者以外には像が結ばない。

- ① Research and evaluation: "Program evaluation, health workforce and economic analysis, and implementation research."
- ③ Advisory and collaborative projects: "Selected advisory work with health services, universities and industry."

Yuho から「Areas of activity の下に支援例を足せばもっと分かりやすくなるのでは」という提案があり、3つの具体案が示された。3つとも実際に相談を受けた／実施した経験があることを本人が確認済み（2026-08-27）。

## 2. サイトの役割と、それが決めたこと

本LPの主目的は **信用確認の場**である。すでに接点のある相手（豪州の大学の研究者、日本の企業・団体の担当者、紹介者）が「この会社は何者か」を確かめに来る。新規の問い合わせを増やすための場ではない。

この確認（2026-08-27）から、以下が決まった。

- 支援例は「呼び込む装置」ではなく、抽象カテゴリを具体で理解させる**注釈**として設計する
- 一人称の悩み調（「〜が不安」「〜してほしい」）は使わず、**第三者記述**にする
- CTA・料金・実績数値・お客様の声は書かない
- `noindex` は維持（本設計のスコープ外）

## 3. MVV仕様書との関係（重要）

[[CoColour Life MVV・ポジショニング 2026-08]] §4「変更しないこと」に **「サービスページ追加なし／CTA追加なし」**、スコープ外に「顧客獲得型LPへの改修（2027年の再評価まで凍結）」とある。

本設計は §2 の3条件（第三者記述の事実／CTAなし／料金・実績数値・お客様の声なし）を守ることで、「静かな信頼性」の内側に収まると判断した。**支援例ブロックはサービスページではなく、既存カテゴリの注釈である。** この判断は 2026-08-27 に Yuho が承認した。

MVV仕様書側にも本判断を追記すること（実装計画に含める）。

## 4. 起こしたい認識変化

想定読者：紹介・照会でこのサイトに来た人。すでに Yuho 個人のことは少し知っており、「会社としては何なのか」を確かめに来ている。

| | 読む前 | 読んだ後 |
|---|---|---|
| 実体 | 研究者が作った会社らしい。何を請け負うのかは曖昧 | 評価・教育・助言・日豪連携の4領域で、実際に仕事が動いている |
| 自分との関係 | 自分の案件が該当するか判断できない | 自分の話がこの3例のどれかに近い／近くない、が判断できる |
| 信頼の質 | 肩書きは立派だが実務は未知数 | 具体的な相談が来ており、受けない場合は受けないと言う会社だ |

## 5. 文体の根拠

[[Yuho — 成果物から観察された像]] §3「媒体を確認してから文体を決める」に従い、本媒体は**教科書・学術誌に近い層**（自己開示ゼロ・主語抑制・抑制的な事実記述）を採る。X文体ガイドは口語媒体の仕様なので適用しない。

効かせた観察は3点。

| 観察ノート | 本設計への反映 |
|---|---|
| §5「自分に不利な数字も出す／豪州を売り込まない」 | 各項目に限界を書く。ブロック末に「すべては受けられない」を置く |
| §7「架け橋は比喩ではなく、登壇者構成・共著者の抄録・教材の編集という具体的な作業」 | 抽象語を実際の作業名（共同発表・共著・教材の作り直し）に置換 |
| §11-6「成果を過大に書かない」 | 効果や成功を約束する表現を置かない |

**deslop 方針**：em dash（—）を新規文面では使わない（Our name セクションの正典コピーは対象外、変更しない）。"not X but Y" の対比構文を使わない。"something a practitioner can act on" のような曖昧名詞を具体物に置き換える。日本語の体言止めを連打しない。

## 6. 確定文面

EN が DOM の既定テキスト（JS無効時の表示）、JA は `data-ja` 属性。

### 6.1 4カテゴリの説明文（差し替え）

**① Research and evaluation**

- EN: `Program and service evaluation, health workforce and cost analysis, and implementation research. Evaluation work is delivered as a report setting out what worked for the people using the service, what did not, and what the evidence does not yet cover.`
- JA: `プログラム・サービスの評価、保健医療人材と費用の分析、実装研究。評価の成果物は、サービスを使う人にとって何が機能し、何が機能しなかったか、そしてエビデンスがまだ及んでいない範囲を書いた報告書です。`

**② Education and knowledge translation**

- EN: `Lectures, workshops and teaching materials for health professionals and students, in English and Japanese. Existing material is rebuilt for the setting where it will be used rather than translated as it stands.`
- JA: `保健医療専門職と学生を対象とした講義・研修・教材の作成。英語と日本語の両方で行います。既存の教材は、そのまま訳すのではなく、使われる現場に合わせて作り直します。`

**③ Advisory and collaborative projects**

- EN: `Advisory work with health services, universities and industry: shaping a project before it starts, or reviewing one already running. The number we take on at a time is limited.`
- JA: `保健医療サービス・大学・企業への助言。企画が始まる前の設計や、進行中の案件の点検を行います。同時にお受けする件数は限られます。`

**④ Australia–Japan collaboration in health and rehabilitation**

- EN: `Exchange of evidence, models of care and technology in both directions. Most of the effort goes into working out what has to change for something that works in one country to work under the funding and service arrangements of the other.`
- JA: `エビデンス・ケアモデル・テクノロジーの双方向の交流。労力の大半は、一方の国で機能しているものが、もう一方の国の資金とサービス提供の仕組みの下でも機能するには何を変える必要があるかを詰めることに使われます。`

「同時にお受けする件数は限られます」と「保健医療サービス」への助言実績は、いずれも Yuho が確認済み（2026-08-27）。

綴りは豪州式（Australian Government Style Manual）に従い `Program`。`Programme` は英国式で、ページ内の `organisational` 等と揃わない。

カテゴリ名（`.area-title`）は4つとも変更しない。

### 6.2 支援例ブロック（新規）

**各例はリード行＋本文の2要素にする**（2026-08-27）。3例が同じ調子で始まるため、どれが自分の話か判断するのに全文を読む必要があった。本文を削って短くする案も比較したが、削れるのが「共同での発表や執筆」「経験から答えられる部分もあれば」といった具体性と限界の開示、つまりこのブロックが信用を作っている部分だったので却下した。

**小見出し**

- EN: `Examples of past enquiries to the founder`
- JA: `創業者がこれまでに受けたご相談の例`

見出しに現在習慣形（`we receive` /「いただく」）を使わない。**3例は Yuho 個人としての経験であり、会社（2026年設立）としての受任実績ではない**ことを本人が確認済み（2026-08-27）。会社が現に相談を受けていると読める表現は overstatement になる。

**例1**

- リード EN: `Taking a product or service into another country.`
- リード JA: `製品やサービスの、別の国への展開`
- 本文 EN: `A company or research group with a healthcare product or service already in use in one country, looking to introduce it in another. What they usually need first is a clear account of the evidence they will be asked for, and of the conditions in the setting where it would be used.`
- 本文 JA: `ある国ですでに使われている保健医療の製品やサービスを、別の国で展開したい企業・研究グループから。最初に必要になるのはたいてい、導入先で求められるエビデンスと、実際に使われる現場の条件を把握することです。`

**例2**

- リード EN: `Introducing a way of working to the other country.`
- リード JA: `取り組みの、もう一方の国への紹介`
- 本文 EN: `A practitioner or organisation that has seen a way of working take hold in Australia or in Japan, and wants to bring it to the other country with colleagues there rather than on their own. In practice this often means joint presentations, co-authored writing, and rebuilding existing material together.`
- 本文 JA: `オーストラリア（あるいは日本）の現場で定着している取り組みを、もう一方の国に紹介したい実践者・団体から。ひとりで進めるのではなく、現地の人たちと一緒に進めたいというご相談です。実際の作業は、共同での発表や執筆、既存の教材を一緒に作り直すことが多くなります。`

**例3**

- リード EN: `Setting up an international project or study.`
- リード JA: `国際的なプロジェクト・研究の立ち上げ`
- 本文 EN: `Researchers or clinicians with an international project or study in mind, who know the question they want to ask but not how a collaboration across two systems is set up and kept going. We can answer some of this from experience. Some of it we work out together.`
- 本文 JA: `国際的なプロジェクトや研究を考えている研究者・臨床家から。問いは決まっているが、二つの制度をまたぐ協働をどう立ち上げ、どう続けるかが分からない、というご相談です。経験から答えられる部分もあれば、一緒に考えながら進める部分もあります。`

**結び**

- EN: `The examples above all involve both countries, but work within one country follows the same four areas. Not every enquiry is a fit. Where it is not, we say so, and, where we can, we point to someone better placed.`
- JA: `上の例はいずれも二国にまたがるものですが、一方の国だけで完結する仕事も同じ4領域で行います。すべてのご相談をお受けできるわけではありません。適さない場合はその旨をお伝えし、可能であればより適した先をお示しします。`

### 6.4 EN と JA は必ず対で編集する

2026-08-27、judge の指摘を反映する際に英語側の案と日本語側の案を別々に採用し、対になっていた6箇所がずれた（見出しは両言語が別の文になり、例1は EN が、例2は語義が、カード③は主体が、例3は網羅性が、結びは約束の強さが食い違った）。同日さらに、小見出しと例3リードを直した際に設計書の再生成を忘れ、正本と設計書がずれた。

**片方の言語だけを直さない。設計書だけを直さない。** 手順は次の1本に固定する。

1. 対ごとに「何を言うか」を1つ決める
2. `tools/verify_lp_copy.py` の定数（正本）を両言語とも書き換える
3. その定数から `index.html` を生成する
4. その定数から設計書 §6.1 / §6.2 を生成する
5. ガードと描画・印刷の検証を実行する

この種のずれは機械では判定できない（日本語は英語1文を2文に割ることが普通にあるため、文数の一致は使えない）。反映のたびに対で読み直すこと。

### 6.3 意図的に書かないこと

**"regulatory"（規制）という語を例1から外している。** 「規制条件の把握を支援する」と書くと、TGA等の薬機・医療機器規制への助言と読まれうる。責任の重い領域であり、実際に受けている相談の内容とも異なるため、`evidence and service conditions`（エビデンスと現場の受け入れ条件）に留める。Yuho 確認済み（2026-08-27）。

## 7. 実装方針

### 7.1 区切りにドットディバイダを使わない（設計中に撤回した案）

当初は既存の `.dot-divider` の流用を検討したが、次の2点により却下した。

1. `style.css:556` で `.dot-divider` は `@media print` の `display: none` に入っている。本LPは印刷参照版を明示的に設計している（`/* print — clean reference copy */`）ため、印刷で消える部品は構造の区切りに使えない。
2. MVV仕様書 §2 の実装注記により、ドットディバイダは「コーダの前に一拍置く」ための Our name セクション固有の記号として定義されている。他所で使うと記号としての意味が薄まる。

代わりに **1px のヘアライン**を使う。border は印刷時に落ちない（ブラウザが印刷で落とすのは背景色と背景画像）。

### 7.2 DOM 構造

`#activities .wrap` の子として、既存の `ul.areas` の後ろに1要素（ラッパー）を追加する。

```html
<div class="enquiries-block">
  <h3 class="enquiries-title" data-en="…" data-ja="…">…</h3>
  <ul class="enquiries">
    <li class="enquiry" data-en="…" data-ja="…">…</li>   <!-- ×3 -->
  </ul>
  <p class="enquiries-note" data-en="…" data-ja="…">…</p>
</div>
```

**ラッパーは実装中の検証で追加した**（当初はラッパーなしの3要素を予定していた）。印刷したところ、3例が3ページ目、結びの「すべてはお受けできません」が4ページ目の先頭に取り残された。3例だけが載った紙が単独で渡ると、限定のない申し出として読まれる。`break-before: avoid` を結びに与える方法は Chrome の印刷エンジンが無視したため、ブロック全体を1ページに保つ方式に変えた（§7.6）。

### 7.3 既存レイアウトとの適合（変更不要な箇所）

- **広幅（≥900px）の左レール**: `style.css:449` の `.section > .wrap > *:not(.section-title) { grid-column: 2 }` により、追加要素は自動で本文カラムに入る。
- **sticky タイトルの行スパン**: `grid-row: 1 / span 20`。コメントは「最長セクション（`#name` の7要素）を超えていればよい」と記す。`#activities` は2要素から5要素になるが 20 の枠内であり、コメントの記述も引き続き正確なので、どちらも変更しない。

### 7.4 i18n の制約

`script.js` の `apply()` は `[data-en][data-ja]` のノードを **`textContent` で丸ごと置換**する。したがって追加要素は**子マークアップを持たないリーフ**でなければならない（既存の `.area-title` / `.area-desc` と同じ形）。本設計の文面はすべてプレーンテキストで、この制約を満たす。

### 7.5 見た目

カード chrome（`--surface` の背景、`--line` の枠、`border-top: 3px` のアクセント、円モチーフの透かし）を**一切与えない**。これが「5つ目の活動領域ではない」ことを伝える主要な手段である。

各項目には左に 2px の縦罫を1本引き、色はロゴのパステル（mint / peri / peach）を順に当てる。カードのアクセントと同じ色系統なので上のブロックとの血縁は保たれるが、面ではなく線なので重さが違い、並列とは読まれない。

```css
/* ---------- examples of enquiries ---------- */
/* deliberately not cards: the four areas above are the taxonomy; these three
   cut across it. Equal visual weight would read as a fifth area. The rules are
   borders, not the dot divider, because the divider is hidden in print and the
   separation has to survive the reference copy. */
/* a label for the three below, not a peer of them: at the leads' size and
   colour it read as a fourth item */
.enquiries-title {
  margin-top: 2.6rem;
  padding-top: 2.6rem;
  border-top: 1px solid var(--line);
  font-size: var(--t-xs);
  font-weight: 600;
  letter-spacing: 0.04em;
  color: var(--muted-text);
}
/* the size sits on the list, not on the items: 66ch resolves against the
   element's own font-size, so the list and the closing note below have to
   carry the same one or the two measures drift apart (they did: 759 vs 707
   at 880px, where the list inherited the 19px body size) */
.enquiries {
  margin-top: 1.8rem;
  max-width: 66ch;
  font-size: var(--t-sm);
}
.enquiries li {
  border-left: 2px solid var(--peri);
  padding-left: 1.15rem;
  color: var(--muted-text);
}
.enquiries li + li { margin-top: 1.35rem; }
/* a short scan line in ink above each detail: three cases that open the same
   way cannot be told apart without reading all of them */
.enquiry-lead {
  display: block;
  font-weight: 600;
  color: var(--ink);
}
.enquiry-detail {
  display: block;
  margin-top: 0.15rem;
  color: var(--muted-text);
}
.enquiries-note {
  margin-top: 2.4rem;
  max-width: 66ch;
  font-size: var(--t-sm);
  color: var(--muted-text);
}
```

`max-width: 66ch` は `.founder-bio` と `.name-logo` が使う既存の行長。新しい数値は導入しない。

**`font-size` は `li` ではなく `ul` に置く。** `ch` は各要素自身の `font-size` で解決されるため、`ul` が本文サイズ（19px）を継承したまま結びだけ `--t-sm`（17px）だと、同じ「66ch」が別の幅になる。実装中の検証で 880px 幅において 759px 対 707px のズレとして表面化した。

### 7.6 印刷

追加の print ルールは2行。

```css
@media print {
  .enquiries li { border-left-color: #000; }
  .enquiries-block { break-inside: avoid; }
}
```

ヘアラインと縦罫はどちらも border なので印刷に残り、構造がそのまま紙に出る。2行目は §7.2 の理由により実装中に追加した。副作用として、直前のページの下部に余白が出る（4カードで区切れる自然な位置なので許容する）。

## 8. 完了条件（実行して確認する）

感想ではなく実行結果で判定する。

1. `index.html` をパースし、`[data-en][data-ja]` を持つ全ノードが子要素を持たない（`textContent` 方式が壊れない）
2. 新規5要素（小見出し・例3つ・結び）と差し替えた4つの `.area-desc` すべてに `data-en` と `data-ja` が存在し、DOM の既定テキストが `data-en` と完全一致する
3. Chrome headless で 360 / 600 / 900 / 1400px の4幅をレンダリングし、`document.documentElement.scrollWidth <= clientWidth`（横スクロールなし）
4. Chrome headless の PDF 出力に、ヘアラインと3本の縦罫が残っている
5. EN / JA 両方でレイアウトが崩れない（日本語は行が長くなる）
6. 新規文面に em dash（`—`）が含まれない

## 9. スコープ外

- Hero のタグライン
- ~~About の lead 段落~~ → 2026-08-27、Yuho の承認によりスコープに入れた（§11.3 の1件目）
- `noindex` の解除
- 解析・CTA・料金表・お客様の声・SEO（MVV仕様書のスコープ外を踏襲）
- 本設計の `main` への push とデプロイ（Yuho の判断を待つ）

## 関連

- `docs/superpowers/specs/2026-08-16-lp-brand-alignment-design.md`
- Vault: `20_Projects/Cocolour Life/CoColour Life MVV・ポジショニング 2026-08.md`
- Vault: `70_Portfolio/Yuho — 成果物から観察された像.md`

## 10. 独立検査の記録（2026-08-27）

自作の文面を自己採点しないという方針（`~/.claude/CLAUDE.md`）に従い、独立した judge 2本で検査した。

### 10.1 文体・誇張の検査

| 観点 | 判定 |
|---|---|
| Yuhoらしいか（観察ノート §3/§5/§7） | PASS |
| 宣伝しすぎていないか（MVV §3/§4） | PASS |
| overstatement | UNVERIFIED → 本人確認で解消 |
| 英語表現の質 | PASS（Minor 5件） |

Critical 0件・Major 0件。指摘のうち次を反映した。

- `health` / 「保健医療」の欠落（Founder 略歴の既存訳語と不一致）
- EN/JA の主張の強度のずれ3件（例1は JA が強い、例2は EN が強い、カード③は JA が強い）
- 英語の粗さ3件（`works` の重複、`who want` の数の不一致、`where we can we` のコンマ欠落）
- 「多くの場合」という頻度の主張を削除

**反映しなかった指摘**: 結びの2文を崩す提案は、代案に `client`（顧客）という商業語が入るため不採用。1文目の倒置だけ解消した。`rather than` が2回出る点は、対比が内容そのものであり言い換えると不正確になるため維持。

### 10.2 立場・規制リスクの検査

| 観点 | 判定 |
|---|---|
| AHPRA 広告規制（s133） | UNVERIFIED |
| 博士提出前のリスク | UNVERIFIED |
| 事実の裏付け | UNVERIFIED → 本人確認で解消 |
| 既存文書との矛盾 | FAIL → 一部反映 |

Critical 0件・Major 4件。次を反映した。

- **「どう資金を得て」/ `funded` を削除**（Major）。本人は同時期に研究助成に応募する側であり、「研究費獲得を有償で助言する主体」と読まれると審査・採用の場面で不利に働きうる。1語削るだけで回避できる。
- **見出しから現在習慣形を削除**（Major）。§6.2 に記載。
- JA「絞っています」→「限られます」（希少性の演出に読めるため EN の事実記述に揃える）
- JA「成果を上げている」→「使われている」（医療製品の有効性評価に踏み込む語を避ける）

**反映しなかった指摘**:

- 「見出しを供給側に戻す」「結びの受付方針の記述を落とす」という2件の Major は不採用。これは設計の是非そのものへの異論であり、欠陥ではない。本LPの目的を「信用確認」と定め、読み手が自分の案件の該当を判断できるようにするのが本設計の核（§2・§4）。供給側の見出しに戻すとこの目的が失われる。結びの一文は、観察ノート §5 の「豪州を売り込まない」を体現する部分であり、削るとブロックが限定のない申し出に近づく。文体側の judge も同じ一文を PASS と判定している。
- `.coi` 段落とプライバシー通知の拡張提案は、いずれも `#about` / `#privacy` という本設計のスコープ外（§9）であり、かつ実際の運用手続についての事実主張を含むため、こちらの判断では追加しない。**Yuho の判断待ちとして記録する。**

### 10.3 未解決（専門家の確認が要る）

| 項目 | 内容 |
|---|---|
| AHPRA s133 の適用範囲 | 「規制対象保健医療サービスを提供する事業の広告」に本サイト全体が分類されうるか。Governance Pack の `PP-01_privacy-policy.md` が自社を "an occupational therapy practice in Melbourne" と定義しているため論点になる。**弁護士または Ahpra への確認が要る。** なお追加文面の中身に s133(1)(a)-(e) 該当箇所は見当たらない。 |
| 大学の外部業務・COI 規程 | 在籍大学の候補者外部業務規程および ANU の outside work / COI ポリシーが vault に記録なし。現在の `.coi` 段落で足りるかを確認できていない。 |

### 10.4 公開判断への申し送り

**`noindex` を解除する時点で、このブロックを再評価すること。** 現在 `noindex` が生きているため MVV §5 の「臨床・商業の前面化は検索時の印象リスク」は顕在化していないが、解除の判断はその前提を外す。Dashboard の公開前チェックリストに項目として追加する。

## 11. 2回目の独立検査（2026-08-27）

judge 3本（英日の対応 / 見た目 / 文脈）。

| 検査 | 判定 |
|---|---|
| 英日の対応（12対を1対ずつ照合） | **PASS**（12対すべて一致） |
| 見た目 | 要修正 → 反映済み |
| 文脈 | 要修正 → 一部反映、一部は判断待ち |

### 11.1 見た目の指摘と対応

| 指摘 | 対応 |
|---|---|
| `.enquiries-title` が `.enquiry-lead` と同一（17px / 600 / `--ink`）で、小見出しが4件目の項目に見える | `--t-xs` ＋ `--muted-text` ＋ `letter-spacing: 0.04em` のラベルに。カード見出しと同値になる方向（19px）は採らない |
| `.area-title` にサイズ指定がなく本文継承のため、日本語（18px）ではリード行（17px）との差が1pxしかない | `.area-title { font-size: 1.2rem; }` を明示 |
| 縦罫の mint / peri / peach がカードのアクセント順（1・2・4番目）と一致し、例とカードの1対1対応に読める | 3本とも `var(--peri)` の単色に。3例は複数のカテゴリを要するので、色で分ける根拠がない |
| 結びの `margin-top: 1.6rem` が項目間（1.35rem）とほぼ同じで、縦罫を失った4件目に見える | `2.4rem` に |
| `#activities::before` だけが上下とも切れず、円形が完全に見えて「置かれた図形」になっている | `left: -215px; top: -70px; width/height: 460px` に。他の3つと同じく2辺で切る |
| 印刷で背景グラフィックOFF（ブラウザ既定）だとカードの塗りが消え、縦罫の黒2pxが紙面で最も強い図形になり重みが反転する | 実際に検証して確認。縦罫を `#444` に落とし、`.areas li { border-color: #999 }` でカードの輪郭を保持 |

### 11.2 文脈の指摘と対応

反映したもの。

- `Programme` → `Program`（豪州式。元のサイトは `Program` であり、こちらの差し替えで英国式に変えてしまっていた）
- ①に受益者を明記。「名前に込めた想い」が語る一人ひとりの日常を受ける語がセクション全体に無かった → `what worked for the people using the service` /「サービスを使う人にとって何が機能し」
- ②に対象者を明記。①③④は相手が書かれているのに②だけ無かった → `for health professionals and students` /「保健医療専門職と学生を対象とした」
- JA の用語をページ全体の「保健医療」に統一（「医療サービス」→「保健医療サービス」、「医療・ヘルスケアの製品」→「保健医療の製品」）
- JA「制度と資金の仕組み」→「資金とサービス提供の仕組み」。EN は `funding and service arrangements` であり、「制度」は法規制まで含意して §6.3 の方針から JA だけがずれていた
- `organisation who` → `that`、`in Australia, or in Japan,` のコンマを削除
- 例3の JA 本文「海外との共同プロジェクトや研究」→「国際的なプロジェクトや研究」（同じ例のリードと語が揃っていなかった）
- 非カード化の根拠の書き方を修正（「4カテゴリを横断する」は不正確。正しくは「いずれも④に属しつつ①②③を組み合わせて使うので、どれか1枚の下には収まらない」）

反映しなかったもの。理由とともに §12 に判断待ちとして記録する。

### 11.3 判断待ちだった5件の処理（2026-08-27、Yuho が全件反映を指示）

| # | 指摘 | 決定と対応 |
|---|---|---|
| 1 | `#about` の lead が活動領域を3つしか挙げず、`#activities` の4つと食い違う | **反映。** About lead の列挙に④を追加（EN/JA）。本設計のスコープ外だったので §9 を更新。なお同段落は前段で「特に日豪間の連携に重点を置き」とも述べるが、前者は目的、後者は領域の列挙であり役割が違うため重複としない |
| 2 | 小見出しの主語が省略され、2026年設立の会社のページ上では「当社が受けた相談」と読めうる | **反映。** 見出しを `Examples of past enquiries to the founder` /「創業者がこれまでに受けたご相談の例」に。注記を1文足すより、帰属を見出しに畳み込むほうが短く、要素も増えない |
| 3 | 3例がすべて越境案件のため、一方の国だけで完結する相談者が「非該当」と誤読しうる | **反映。** 結びの冒頭に1文追加。`The examples above all involve both countries, but work within one country follows the same four areas.` /「上の例はいずれも二国にまたがるものですが、一方の国だけで完結する仕事も同じ4領域で行います。」 |
| 4 | Governance Pack の `PP-01_privacy-policy.md` が会社を "an occupational therapy practice in Melbourne" と定義しており、LP の名乗りと食い違う | **LP は変更しない。** どちらが現行の正かは事実の決定であり、こちらでは決められない。PP-01 は 2026-09-01 発効予定でまだ発効しておらず、電話番号・住所も `要確認` のまま。そこで vault の `Governance Pack/発効ブロッカー チェックリスト.md` §A に発効ブロッカーとして記録した。**発効前に Yuho が決めること** |
| 5 | 900〜1041px でカードが1列になり左レールが空洞化する | **反映。** `@media (min-width: 900px)` を `1040px` に。サイト全体に及ぶ変更なので、9つの幅（360/600/880/900/1000/1039/1040/1200/1400）で列数・レールの有無・横スクロールを実測して確認した。880px 以降は一貫して2列、レールは2列が成立する1040px から出る |

### 11.4 5件反映後の実測（2026-08-27）

| 幅 | カードの列数 | 左レール | 横スクロール EN/JA |
|---|---|---|---|
| 360 / 600 | 1 | なし | 0 / 0 |
| 880 / 900 / 1000 / 1039 | 2 | なし | 0 / 0 |
| 1040 / 1200 / 1400 | 2 | あり | 0 / 0 |

印刷は5ページ、支援例ブロック全体が4ページ目に収まる。ガード2種とも通過。
