# GLM (智谱 / Z.ai) 設定ガイド

## GLM Coding Plan 契約時の重要設定

**GLM Coding Lite-Monthly Plan** 等を契約している場合、**Z.ai 専用エンドポイント**を使用する必要があります。

| プラットフォーム | エンドポイント | 用途 |
|-----------------|---------------|------|
| **Z.ai (Coding Plan)** | `https://api.z.ai/api/coding/paas/v4` | サブスクリプションクォータ使用 |
| open.bigmodel.cn | `https://open.bigmodel.cn/api/paas/v4` | 残高チャージ方式 |

**config.json に以下を追加**:
```json
"glm_use_coding_plan": true
```

APIキーは [Z.ai API Keys](https://z.ai/manage-apikey/apikey-list) で取得したものを `glm_key` に設定してください。

## エラー「トークン残量がない」の原因と対処

### エラーコード 1113: 余额不足或无可用资源包

**原因（Coding Plan 契約時）**: `open.bigmodel.cn` エンドポイントを使用している。Coding Plan のクォータは **Z.ai エンドポイント** でのみ利用可能。

**対処**: `config.json` に `"glm_use_coding_plan": true` を追加し、Z.ai の API キーを使用する。

### モデル一覧（智谱公式）

| 選択肢 | モデル名 | 説明 |
|--------|----------|------|
| 4 | glm-4.7 | フラッグシップ |
| 5 | glm-4.7-flashx | 軽量高速版 |
| 6 | glm-4.7-flash | Coding Plan 無制限枠（推奨） |

### モデル名の互換

- `glm-4-flash` や `glm-4.7-flash` は、プロキシ経由で適切に処理されます。
- `glm-4.7-flash` は Coding Plan において無制限に利用可能なモデルです。

### 参考リンク

- [Z.ai サブスクリプション管理](https://z.ai/manage-apikey/subscription)
- [Z.ai API キー管理](https://z.ai/manage-apikey/apikey-list)
