"""
構造化JSONをLLMに投入し、
視覚的なトレード戦略カードを生成する。
"""

SYSTEM_PROMPT = """
あなたはプロのデイトレード戦略アドバイザーです。
構造化された分析データを受け取り、
トレーダーが即座に判断できるアクションプランに変換します。

出力ルール:
1. 結論を最初に。理由は後。
2. 数値は全て検算済みの入力値をそのまま使う。自分で再計算しない。
3. 曖昧な表現（「おそらく」「かもしれない」）は禁止。
4. 出力はMarkdown形式。視覚的な区切りを多用する。
5. 全体を1画面（60行以内）に収める。
"""


def build_prompt(strategy_json: dict) -> str:
    j = strategy_json
    meta = j["meta"]
    judgment = j["judgment"]
    kl = j["key_levels"]
    scenarios = j["scenarios"]
    contingencies = j["contingencies"]

    active = [s for s in scenarios if s.get("status") == "ACTIVE"]
    excluded = [s for s in scenarios if s.get("status") == "EXCLUDED"]

    prompt = f"""
以下の構造化データから、デイトレード戦略カードを生成してください。

## 入力データ

銘柄: {meta["ticker"]} {meta["company"]}
日付: {meta["date"]}
トレンド: {meta["trend"]}
ATR: {meta["atr"]}円
環境スコア: {meta["env_score"]}/100
リスク水準: {meta["risk_level"]}
流動性（サージ比）: {meta["volume_surge"]}

### キーレベル
PMH: {kl["pmh"]} / PML: {kl["pml"]} / PDC: {kl["pdc"]}
R1: {kl["r1"]} / R2: {kl["r2"]}
S1: {kl["s1"]} / S2: {kl["s2"]}
VWAP: {kl["vwap"]} / POC: {kl["poc"]}
ギャップ予測: {kl["gap_level"]}

### メインシナリオ
"""

    for s in active:
        prompt += f"""
{s["id"]}: {s["name"]} ({s["direction"]})
  Entry: {s["entry"]} / SL: {s["sl"]} / TP: {s["tp"]}
  RRR: {s["rrr"]} / EV: {s["ev"]}円/株
  TP到達確率: {s["tp_prob"]}%
  有効: {s["valid_from"]}〜{s["valid_until"]}
  警告: {", ".join(s.get("warnings", []))}
"""

    if contingencies:
        prompt += "\n### コンティンジェンシー\n"
        for c in contingencies:
            prompt += f"""
{c["id"]}: {c["name"]} ({c["direction"]})
  Entry: {c["entry"]} / SL: {c["sl"]}
  TP1: {c["tp1"]} / TP2: {c["tp2"]}
  RRR: {c["rrr"]} / EV: {c["ev"]}円/株
  有効: {c["valid_from"]}〜{c["valid_until"]}
  執行可能帯: {c["executable_bands"]}
"""

    if excluded:
        prompt += "\n### 除外シナリオ\n"
        for s in excluded:
            prompt += f"""
{s["id"]}: RRR={s.get("rrr","N/A")} → 除外
  改善余地: {s.get("optimization", "なし")}
"""

    prompt += f"""
### 判定サマリ
総合: {judgment["summary"]}
流動性警告: {judgment["liquidity_warning"]}
EV警告: {judgment["has_ev_warning"]}
実行可能: {judgment["actionable"]}

## 出力フォーマット

以下の構造で出力してください:

### 🎯 今日の1行結論
（トレードするか/しないか。する場合の条件。15文字以内。）

### 📊 戦略カード
（Entry/SL/TP/RRRを表形式で。S1とC1を並列比較。）

### ⏰ タイムライン
（時間帯別の行動指示。箇条書き5-7行。）

### 🚦 Go/No-Go チェック
（エントリー直前に確認する3-5項目。Yes/Noで判定。）

### 🛡️ リスクサマリ
（最大損失額・必要資金・撤退条件を3行で。）
"""

    return prompt


def generate_strategy_card(strategy_json: dict) -> str:
    prompt = build_prompt(strategy_json)
    return prompt
