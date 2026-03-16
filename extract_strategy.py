"""
MDレポートからトレード戦略に必要な情報のみを
構造化JSONに抽出する。
LLMに渡す前の前処理として使用。
"""

import re
import json
from pathlib import Path


def extract_from_md(md_path: str) -> dict:
    text = Path(md_path).read_text(encoding="utf-8")

    strategy = {
        "meta": _extract_meta(text),
        "judgment": _extract_judgment(text),
        "key_levels": _extract_key_levels(text),
        "scenarios": _extract_scenarios(text),
        "contingencies": _extract_contingencies(text),
        "filters": _extract_filters(text),
        "risk_management": _extract_risk(text),
        "action_summary": None,  # Step 2でLLMが埋める
    }

    return strategy


def _extract_meta(text: str) -> dict:
    return {
        "ticker": _find(r"# (\d{4})", text),
        "company": _find(r"# \d{4}\s+(.+?)\s+デイトレード", text),
        "date": _find(r"実行日時:\s*(\S+)", text),
        "atr": _find_number(r"日足ATR\(14\):\s*([\d,]+)", text),
        "trend": _find(r"トレンド\(日足\):\s*(\S+)", text),
        "env_score": _find_number(r"環境スコア:\s*([\d.]+)", text),
        "risk_level": _find(r"リスク水準:\s*(\S+)", text),
        "volume_surge": _find_number(
            r"ボリュームサージ比[=:]\s*([\d.]+)", text
        ),
    }


def _extract_judgment(text: str) -> dict:
    summary = _find(r"\*\*総合判定\*\*:\s*(.+?)$", text, re.M)
    return {
        "summary": summary,
        "has_ev_warning": "EV警告" in (summary or ""),
        "liquidity_warning": "流動性不足" in (summary or ""),
        "actionable": "エントリー可" in (summary or ""),
    }


def _extract_key_levels(text: str) -> dict:
    return {
        "pmh": _find_number(r"高値\(PMH\)\s*([\d,]+)", text),
        "pml": _find_number(r"安値\(PML\)\s*([\d,]+)", text),
        "pdc": _find_number(r"終値\(PDC\)\s*([\d,]+)", text),
        "r1": _find_number(r"R1\s*([\d,]+)", text),
        "r2": _find_number(r"R2\s*([\d,]+)", text),
        "s1": _find_number(r"S1\s*([\d,]+)", text),
        "s2": _find_number(r"S2\s*([\d,]+)", text),
        "vwap": _find_number(r"VWAP予測:\s*([\d,]+)", text),
        "gap_level": _find_number(
            r"理論寄り付き付近:\s*([\d,]+)", text
        ),
        "poc": _find_number(r"POC:\s*([\d,]+)", text),
    }


def _extract_scenarios(text: str) -> list:
    scenarios = []

    # S1（メインシナリオ）
    s1_match = re.search(
        r"\[S1\].*?(?=## |\*\*S1/C1)", text, re.DOTALL
    )
    if s1_match:
        s1_text = s1_match.group()
        scenarios.append({
            "id": "S1",
            "name": _find(r"\[S1\]\s*(.+?)\s*—", s1_text),
            "direction": "LONG",
            "entry": _find_number(r"\*\*Entry\*\*:\s*([\d,]+)", s1_text),
            "sl": _find_number(r"\*\*SL\*\*:\s*([\d,]+)", s1_text),
            "tp": _find_number(r"\*\*TP\*\*:\s*([\d,]+)", s1_text),
            "rrr": _find_number(r"\*\*RRR\*\*:\s*([\d.]+)", s1_text),
            "ev": _find_number(r"期待値=([-\d]+)円", s1_text),
            "tp_prob": _find_number(
                r"TP到達確率.*?:\s*([\d.]+)%", s1_text
            ),
            "valid_from": _find(r"有効時間.*?(\d{2}:\d{2})", s1_text),
            "valid_until": _find(
                r"有効時間.*?\d{2}:\d{2}〜(\d{2}:\d{2})", s1_text
            ),
            "status": "ACTIVE",
            "warnings": _extract_warnings(s1_text),
        })

    # S2, S3（見送り）
    for sid in ["S2", "S3"]:
        pattern = rf"\[{sid}\](.+?)(?=\n- \[S|$)"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            s_text = match.group()
            scenarios.append({
                "id": sid,
                "entry": _find_number(
                    r"Entry\s*([\d,]+)", s_text
                ),
                "sl": _find_number(r"SL\s*([\d,]+)", s_text),
                "tp": _find_number(r"TP\s*([\d,]+)", s_text),
                "rrr": _find_number(r"RRR=([\d.]+)", s_text),
                "status": "EXCLUDED",
                "optimization": _find(
                    r"改善余地:\s*(.+?)$", s_text, re.M
                ),
            })

    return scenarios


def _extract_contingencies(text: str) -> list:
    contingencies = []

    c1_match = re.search(
        r"\[C1\].*?(?=→ 上記|※ショート)", text, re.DOTALL
    )
    if c1_match:
        c1_text = c1_match.group()
        contingencies.append({
            "id": "C1",
            "name": _find(r"\[C1\]\s*(.+?)$", c1_text, re.M),
            "direction": "LONG",
            "entry": _find_number(
                r"\*\*Entry\*\*:\s*([\d,]+)", c1_text
            ),
            "sl": _find_number(r"\*\*SL\*\*:\s*([\d,]+)", c1_text),
            "tp1": _find_number(r"\*\*TP1\*\*:\s*([\d,]+)", c1_text),
            "tp2": _find_number(r"\*\*TP2\*\*:\s*([\d,]+)", c1_text),
            "rrr": _find_number(r"\*\*RRR\*\*:\s*([\d.]+)", c1_text),
            "ev": _find_number(r"期待値=([-\d]+)円", c1_text),
            "valid_from": _find(
                r"有効時間.*?(\d{2}:\d{2})", c1_text
            ),
            "valid_until": _find(
                r"有効時間.*?\d{2}:\d{2}〜(\d{2}:\d{2})", c1_text
            ),
            "executable_bands": _find(
                r"執行可能帯:\s*(.+?)$", c1_text, re.M
            ),
            "status": "CONTINGENCY",
        })

    return contingencies


def _extract_filters(text: str) -> dict:
    return {
        "rvol_min": 1.5,
        "rvol_high": 2.0,
        "time_bands": [
            {"range": "09:00-10:30", "min_rrr": 1.0,
             "type": "active"},
            {"range": "10:30-11:30", "min_rrr": 1.2,
             "type": "quiet"},
            {"range": "12:30-13:00", "min_rrr": 1.0,
             "type": "reopen"},
            {"range": "13:00-14:00", "min_rrr": 1.2,
             "type": "quiet"},
            {"range": "14:30-15:00", "min_rrr": 1.0,
             "type": "active"},
        ],
        "sl_atr_range": [0.20, 0.35],
        "liquidity_floor": 0.3,
    }


def _extract_risk(text: str) -> dict:
    return {
        "max_loss_per_trade": "0.1%",
        "position_reduction": "50%",
        "short_restriction": "空売り価格規制に注意",
        "no_trade_conditions": [
            "寄り後15分でATR80%消化",
            "板が極端に薄い",
        ],
    }


def _extract_warnings(text: str) -> list:
    warnings = []
    if "RRR品質" in text:
        warnings.append("RRR_QUALITY")
    if "期待値" in text and "マイナス" in text:
        warnings.append("NEGATIVE_EV")
    if "流動性" in text:
        warnings.append("LOW_LIQUIDITY")
    if "実務制約" in text:
        warnings.append("CAPITAL_REQUIREMENT")
    return warnings


def _find(pattern, text, flags=0):
    m = re.search(pattern, text, flags)
    return m.group(1).strip() if m else None


def _find_number(pattern, text, flags=0):
    m = re.search(pattern, text, flags)
    if not m:
        return None
    return float(m.group(1).replace(",", ""))


if __name__ == "__main__":
    import sys
    import io
    # UTF-8エンコーディングを設定
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    md_file = sys.argv[1] if len(sys.argv) > 1 else "report.md"
    result = extract_from_md(md_file)
    print(json.dumps(result, ensure_ascii=False, indent=2))
