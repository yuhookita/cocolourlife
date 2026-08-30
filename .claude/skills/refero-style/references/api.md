# styles.refero.design 公開 API（観測仕様・2026-08-30）

非公式。`faridjafarlee/refero-styles-mcp-server`（MIT, TypeScript）が使っている
エンドポイントを読み取って再現したもの。認証は不要。

Base: `https://styles.refero.design/api`
Headers: `Accept: application/json` / `User-Agent: <任意>`

## GET /styles?page=N

```jsonc
{
  "styles": [
    {
      "id": "uuid",
      "url": "https://<参照元サイト>",
      "siteName": "…",
      "screenshotUrl": "…", "thumbnailUrl": "…", "iconUrl": "…",
      "colorScheme": "light" | "dark" | "…",
      "colors": [{ "name": "Navy", "hex": "#1b1464" }],
      "fonts": ["Inter", "…"],
      "northStar": "その体系を一言で言うと",
      "createdAt": "ISO8601"
    }
  ],
  "nextPage": 2,          // null で終端
  "nextCursor": "…"       // 未使用
}
```

1ページ20件前後。MCP サーバーは3ページ（約60件）までを取って
クライアント側で絞り込んでいる。**サーバー側の検索パラメータは確認できていない**
（`?q=` 等があるかは未検証）。`scripts/refero.py` も同じく取得後に手元で絞る。

## GET /styles/{id}

一覧と同じフィールドに加えて:

```jsonc
{
  "style": {
    "…summary の全項目…",
    "fullResult": { "designSystem": { /* 下記 */ } }
  },
  "similar": [ /* StyleSummary[] — 任意 */ ]
}
```

（レスポンスが `style` で包まれている前提。包まれていない形も来うるので
`scripts/refero.py` は `data.get("style") or data` で両対応にしてある。）

### designSystem

| フィールド | 型 |
|---|---|
| `description`, `theme`, `northStar`, `layout`, `imagery` | string |
| `dos`, `donts`, `similar` | string[] |
| `colors` | `{ name, hex, role?, group? }[]` |
| `typography` | `{ family, weights?, fallback? }[]` |
| `typeScale` | `{ role, size?, weight?, lineHeight?, letterSpacing? }[]` |
| `spacing` | `{ radius?, elementGap?, sectionGap?, cardPadding?, pageMaxWidth? }` |
| `surfaces` | `{ name, color?, description? }[]` |
| `elevation` | `{ name?, shadow? }[]` |
| `components` | `{ name, html?, css?, description? }[]` |
| `customSections` | `{ title, content }[]` |

すべて任意。`fullResult.designSystem` 自体が無い件もあるので、
その場合は summary の `colors` / `fonts` だけを確かなものとして扱う。

## 人が見るページ

- 一覧: `https://styles.refero.design/`
- 個別: `https://styles.refero.design/style/<UUID>`
- AI 向け資料: `https://styles.refero.design/ai-agents/design-resources`
