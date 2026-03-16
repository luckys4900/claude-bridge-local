"""
株式分析システムの設定ファイル
"""

# API設定
ANTHROPIC_API_KEY = None  # 環境変数から取得する

# データ取得設定
DEFAULT_TICKER = "6871.T"  # デフォルト銘柄（日本マイクロニクス）
TIMEFRAMES = ["1d", "1w", "1m"]  # 取得する時間足
MOVING_AVERAGES = [5, 25, 75, 200]  # 移動平均線期間

# テクニカル指標設定
ATR_PERIOD = 14  # ATR期間
RSI_PERIOD = 14  # RSI期間
MACD_FAST = 12  # MACD短期
MACD_SLOW = 26  # MACD長期
MACD_SIGNAL = 9  # MACDシグナル

# モンテカルロ設定
MONTE_CARLO_SIMULATIONS = 1000  # シミュレーション回数
MONTE_CARLO_DAYS = 20  # 予測日数

# 出力設定
OUTPUT_DIR = "./reports"  # レポート出力ディレクトリ
LOG_LEVEL = "INFO"  # ログレベル

# データソース設定
USE_YAHOO_FINANCE = True  # Yahoo Financeを使用
USE_KABUTAN = True  # 株探を使用
