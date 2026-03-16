# FastAPI Stock Analysis System - プロジェクト構成

完全なAIトレード分析システムが構築されました。定量データと定性ナラティブ分析を融合させたプロフェッショナルグレードのシステムです。

## 📁 プロジェクト構成

```
claude-bridge-local/
├── fastapi_stock_analysis/          # メイン株式分析システム
│   ├── main.py                      # FastAPIメインアプリケーション
│   ├── data_fetcher.py              # データ収集モジュール (Yahoo Finance)
│   ├── analyzer.py                  # LLM分析エンジン (Anthropic Claude)
│   ├── report_generator.py           # レポート生成モジュール
│   ├── requirements.txt              # Python依存関係
│   ├── .env.example                 # 環境変数テンプレート
│   ├── run.py                       # 起動スクリプト
│   ├── test_client.py               # APIテストクライアント
│   ├── start_server.bat             # Windows起動スクリプト
│   └── README.md                    # 詳細ドキュメント
│
├── main.py                          # 既存のFastAPI Memory API
└── 使い方.md                        # Claude Bridgeの使い方
```

## 🚀 クイックスタート

### 1. セットアップ

```bash
cd fastapi_stock_analysis

# 依存関係のインストール
pip install -r requirements.txt

# 環境変数の設定
cp .env.example .env
# .envファイルを編集してANTHROPIC_API_KEYを設定
```

### 2. サーバーの起動

```bash
# Windowsの場合
start_server.bat

# または直接実行
python run.py
```

サーバーが `http://localhost:8000` で起動します。

### 3. APIの使用

**ブラウザでアクセス:**
- APIドキュメント: http://localhost:8000/docs
- ヘルスチェック: http://localhost:8000/health

**プログラムから使用:**
```python
# test_client.pyを実行
python test_client.py

# またはPythonから直接
import requests
response = requests.post(
    "http://localhost:8000/api/analyze",
    json={"ticker": "6871.T", "mode": "daytrade"}
)
print(response.json()["final_report_markdown"])
```

## 🔑 主要機能

### 1. データ収集層 (Data Fetcher)
- ✅ Yahoo Financeからのリアルタイム株価データ取得
- ✅ テクニカル指標の自動計算 (ATR, VWAP, RSI, MACD, etc.)
- ✅ 移動平均線分析 (5日・25日・75日・200日)
- ✅ プライスアクションパターン検出
- ✅ 需給バランス評価

### 2. AI分析層 (Analyzer)
- ✅ **Stage 1**: ナラティブ分析 (トレンド対立、相場心理)
- ✅ **Stage 2**: 戦略分析 (If-Thenシナリオ、RRR計算)
- ✅ **Stage 3**: メタ分析 (全体評価、リスク機会)
- ✅ プロフェッショナルな思考プロセス (Chain of Thought)

### 3. レポート生成層 (Report Generator)
- ✅ 専門的マークダウンフォーマット
- ✅ 定量データと定性分析の統合
- ✅ 具体的な取引シナリオ提示
- ✅ リスク管理と免責事項

## 📊 APIエンドポイント

### POST /api/analyze
完全な株式分析を実行

```json
{
  "ticker": "6871.T",
  "mode": "daytrade",
  "include_news": true
}
```

### GET /api/analyze/{ticker}
シンプルなGETリクエスト

```
GET /api/analyze/6871.T?mode=daytrade
```

### GET /api/indicators/{ticker}
テクニカル指標のみ取得

```
GET /api/indicators/6871.T
```

### GET /health
サーバーヘルスチェック

## 🎯 分析モード

### デイトレード (daytrade)
- 当日中の取引に焦点
- 短期テクニカル指標重視
- ギャップリスク考慮

### スイングトレード (swing)
- 数日〜数週間の取引に焦点
- 中期トレンド重視
- 基本分析とテクニカル分析の融合

## 📈 出力レポートの構成

### 1. エグゼクティブサマリー
- 現在価格とセンチメント
- 市場状況の概要
- 主要な注目点

### 2. 現在の市場状況（定量データ）
- 株価情報と年初来パフォーマンス
- 主要テクニカル指標

### 3. テクニカル＆需給の文脈（定性分析）
- 移動平均の並びとトレンド
- プライスアクション分析
- 需給バランスと市場心理

### 4. 取引シナリオ（If-Then Strategy）
- 具体的なエントリー条件
- TP/SL設定とRRR
- 確度と時間ホライゾン

### 5. リスク評価
- 主要リスク要因
- 主要機会
- 取引における注意点

## 🔧 技術仕様

- **API Framework**: FastAPI (async対応)
- **データソース**: Yahoo Finance (yfinance)
- **AIエンジン**: Anthropic Claude (Sonnet 4.6)
- **データ処理**: Pandas, NumPy
- **非同期処理**: asyncio, uvicorn

## 💡 使用例

### Pythonから使用
```python
from fastapi_stock_analysis.test_client import StockAnalysisClient

client = StockAnalysisClient()
analysis = client.analyze_stock(
    ticker="6871.T",
    mode="daytrade"
)

print(analysis["final_report_markdown"])
```

### cURLから使用
```bash
curl -X POST "http://localhost:8000/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{"ticker":"6871.T","mode":"daytrade"}'
```

### JavaScriptから使用
```javascript
const response = await fetch('http://localhost:8000/api/analyze', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    ticker: '6871.T',
    mode: 'daytrade'
  })
});
const data = await response.json();
console.log(data.final_report_markdown);
```

## ⚠️ 注意点

1. **API Key**: Anthropic API Keyが必要（高度なLLM分析用）
2. **データ制限**: Yahoo Financeのレート制限に注意
3. **投資責任**: 情報提供のみが目的
4. **システム要件**: Python 3.8以上

## 📝 今後の拡張可能性

このシステムは以下の拡張に対応できます:

- [ ] モンテカルロシミュレーションの追加
- [ ] 複数銘柄の比較分析
- [ ] バックテスト機能の追加
- [ ] Telegram/Discordボット連携
- [ ] TradingViewアラート連携
- [ ] データベースでの履歴管理
- [ ] WebSocketによるリアルタイム更新

## 📚 詳細ドキュメント

詳細な使用方法やAPIドキュメントは以下を参照してください:
- [README.md](fastapi_stock_analysis/README.md)
- http://localhost:8000/docs (起動時)

## 🤝 貢献

このシステムはオープンソースプロジェクトとして開発されています。機能の改善やバグ修正は大歓迎です。

## ⚖️ ライセンス

MIT License

---

*このシステムはClaude Codeによって生成・最適化されています*
