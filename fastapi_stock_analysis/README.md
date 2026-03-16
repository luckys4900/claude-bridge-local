# AI Stock Analysis API

プロフェッショナルグレードの株式分析システム。定量データと定性的ナラティブ分析を融合させた最強のトレード分析API。

## 特徴

- 🤖 **AIによる思考プロセス**: LLMを活用したプロレベルの相場分析
- 📊 **包括的テクニカル分析**: ATR、VWAP、RSI、MACD、ボリンジャーバンドなど
- 📈 **移動平均分析**: 5日・25日・75日・200日移動平均線の並びとトレンド分析
- 🎯 **If-Then取引シナリオ**: RRR 1.0以上の具体的なエントリー/イグジット戦略
- 🚨 **リスク管理**: 自動化されたリスク評価とアラート生成
- 🌐 **RESTful API**: あらゆるシステムから呼び出せるWeb API

## システム構成

```
fastapi_stock_analysis/
├── main.py              # FastAPIメインアプリケーション
├── data_fetcher.py      # データ収集モジュール
├── analyzer.py          # LLM分析エンジン
├── report_generator.py  # レポート生成モジュール
├── requirements.txt     # Python依存関係
├── .env.example         # 環境変数テンプレート
├── README.md           # このファイル
└── run.py              # 起動スクリプト
```

## セットアップ

### 1. 依存関係のインストール

```bash
cd fastapi_stock_analysis
pip install -r requirements.txt
```

### 2. 環境変数の設定

`.env.example` を `.env` にコピーして、必要な設定を行います。

```bash
cp .env.example .env
```

`.env` ファイルで設定:

```env
# Anthropic API Key (必須 - 高度なLLM分析用)
ANTHROPIC_API_KEY=your_api_key_here

# API設定 (オプション)
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
```

### 3. APIの起動

```bash
# 方法1: 直接起動
python main.py

# 方法2: uvicornを使用
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 方法3: 起動スクリプト使用
python run.py
```

## APIエンドポイント

### 1. 株式分析メインエンドポイント

**POST** `/api/analyze`

完全な株式分析を実行します。

**リクエスト例**:
```json
{
  "ticker": "6871.T",
  "mode": "daytrade",
  "include_news": true
}
```

**レスポンス**:
```json
{
  "ticker": "6871.T",
  "mode": "daytrade",
  "raw_data": {
    "price_data": {...},
    "technical_indicators": {...},
    "moving_averages": {...},
    "qualitative_data": {...}
  },
  "thought_process": {
    "stage_1_narrative": {...},
    "stage_2_strategy": {...},
    "meta_analysis": {...}
  },
  "final_report_markdown": "# 完全なマークダウンレポート...",
  "generated_at": "2026-03-15T10:30:00"
}
```

### 2. シンプル分析エンドポイント

**GET** `/api/analyze/{ticker}?mode=daytrade&include_news=true`

シンプルなGETリクエストで分析を取得します。

### 3. テクニカル指標のみ

**GET** `/api/indicators/{ticker}`

テクニカル指標のみを取得します（高速）。

### 4. ヘルスチェック

**GET** `/health`
**GET** `/`

APIのステータスを確認します。

## 使用例

### Pythonから使用

```python
import requests

# 分析リクエスト
response = requests.post(
    "http://localhost:8000/api/analyze",
    json={
        "ticker": "6871.T",
        "mode": "daytrade",
        "include_news": True
    }
)

data = response.json()

# マークダウンレポートを表示
print(data["final_report_markdown"])
```

### cURLから使用

```bash
# 基本分析
curl -X POST "http://localhost:8000/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "6871.T",
    "mode": "daytrade",
    "include_news": true
  }'

# シンプルGET
curl "http://localhost:8000/api/analyze/6871.T?mode=daytrade"
```

### JavaScriptから使用

```javascript
// Fetch APIを使用
const response = await fetch('http://localhost:8000/api/analyze', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    ticker: '6871.T',
    mode: 'daytrade',
    include_news: true
  })
});

const data = await response.json();
console.log(data.final_report_markdown);
```

## 分析モード

### デイトレード (daytrade)
- 当日中の取引に焦点
- 短期テクニカル指標重視
- ギャップリスク考慮
- 時間足: 1分〜15分

### スイングトレード (swing)
- 数日〜数週間の取引に焦点
- 中期トレンド重視
- 基本分析とテクニカル分析の融合
- 時間足: 日足〜週足

## 出力される分析内容

### 1. エグゼクティブサマリー
- 現在価格とセンチメント
- 市場状況の概要
- 主要な注目点

### 2. 現在の市場状況（定量データ）
- 株価情報
- 年初来パフォーマンス
- 主要テクニカル指標

### 3. テクニカル＆需給の文脈（定性分析）
- 移動平均の並びとトレンド
- プライスアクション分析
- 需給バランスと市場心理

### 4. 取引シナリオ（If-Then Strategy）
- 具体的なエントリー条件
- テイクプロフィット目標
- ストップロス設定
- リスクリワード比率 (RRR)
- 予想確度と時間ホライゾン

### 5. リスク評価
- 主要リスク要因
- 主要機会
- 取引における注意点

## LLM分析機能

このシステムでは以下の2段階のLLM推論を実装しています:

### Stage 1: Narrative & Trend Analysis
- 移動平均線のトレンド対立評価
- 直近のプライスアクションパターン分析
- 需給バランスと市場心理の評価

### Stage 2: Actionable Strategy Development
- 定量データと定性分析の統合
- RRR 1.0以上の具体的な取引シナリオ設計
- プロフェッショナルなリスク管理戦略

## 技術スタック

- **API Framework**: FastAPI
- **Data Source**: Yahoo Finance (yfinance)
- **AI Engine**: Anthropic Claude
- **Data Processing**: Pandas, NumPy
- **Async Support**: asyncio, uvicorn

## 注意点

1. **API Key**: 高度なLLM分析を行うにはAnthropic API Keyが必要です
2. **データの制限**: Yahoo Financeからのデータ取得にはレート制限があります
3. **投資の責任**: このレポートは情報提供のみを目的としています
4. **システム要件**: Python 3.8以上が必要

## トラブルシューティング

### APIキーが動作しない
- `.env` ファイルが正しく設定されているか確認
- APIキーが有効であるか確認

### データ取得エラー
- インターネット接続を確認
- Yahoo Financeのサーバーステータスを確認
- 銘柄コードが正しいか確認

### レスポンスが遅い
- 初回はデータ取得と分析に時間がかかります
- キャッシュ機能が自動的に有効化されます

## 開発

### テスト

```bash
# テストクライアントを実行
python test_client.py
```

### モジュールの追加

新しい分析モジュールを追加する場合:

1. `data_fetcher.py` にデータ取得関数を追加
2. `analyzer.py` に分析ロジックを追加
3. `report_generator.py` に出力フォーマットを追加

## ライセンス

MIT License

## 免責事項

このシステムは教育目的および情報提供のみを目的としています。ここに含まれる情報に基づいて行われるいかなる投資決定も、使用者自身の判断と責任において行われるべきです。投資には元本を失うリスクが伴います。

---

*このシステムはAIによって生成・最適化されています*
