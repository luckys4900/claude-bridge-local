"""
LLM出力をHTML戦略カードに変換する。
"""

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: 'Noto Sans JP', sans-serif;
    background: #0d1117; color: #c9d1d9;
    padding: 16px; max-width: 800px; margin: 0 auto;
  }}
  .header {{
    display: flex; justify-content: space-between;
    align-items: center; margin-bottom: 16px;
    border-bottom: 2px solid #30363d; padding-bottom: 8px;
  }}
  .ticker {{ font-size: 24px; font-weight: bold; color: #58a6ff; }}
  .badge {{
    padding: 4px 12px; border-radius: 12px;
    font-size: 12px; font-weight: bold;
  }}
  .badge-warn {{ background: #d29922; color: #000; }}
  .badge-danger {{ background: #f85149; color: #fff; }}
  .badge-ok {{ background: #3fb950; color: #000; }}

  .conclusion {{
    background: #161b22; border-left: 4px solid #58a6ff;
    padding: 12px 16px; margin: 12px 0; font-size: 18px;
  }}

  table {{
    width: 100%; border-collapse: collapse; margin: 12px 0;
  }}
  th {{
    background: #21262d; padding: 8px; text-align: left;
    font-size: 12px; color: #8b949e;
  }}
  td {{
    padding: 8px; border-bottom: 1px solid #21262d;
  }}
  .long {{ color: #3fb950; }}
  .short {{ color: #f85149; }}
  .neutral {{ color: #d29922; }}

  .timeline {{
    background: #161b22; padding: 12px; margin: 12px 0;
    border-radius: 6px;
  }}
  .timeline-item {{
    display: flex; padding: 6px 0;
    border-left: 2px solid #30363d; padding-left: 12px;
    margin-left: 8px;
  }}
  .timeline-time {{
    min-width: 80px; color: #58a6ff; font-weight: bold;
  }}

  .checklist {{ margin: 12px 0; }}
  .check-item {{
    display: flex; align-items: center; padding: 4px 0;
  }}
  .check-box {{
    width: 18px; height: 18px; border: 2px solid #30363d;
    border-radius: 3px; margin-right: 8px; flex-shrink: 0;
  }}

  .risk-box {{
    background: #1c0a0a; border: 1px solid #f85149;
    border-radius: 6px; padding: 12px; margin: 12px 0;
  }}

  .level-bar {{
    background: #21262d; height: 24px; border-radius: 4px;
    position: relative; margin: 8px 0;
  }}
  .level-marker {{
    position: absolute; top: -4px; width: 2px; height: 32px;
  }}
  .level-label {{
    position: absolute; top: -20px; font-size: 10px;
    transform: translateX(-50%); white-space: nowrap;
  }}
</style>
</head>
<body>
  <div class="header">
    <span class="ticker">{ticker} {company}</span>
    <div>
      <span class="badge badge-{judgment_class}">{judgment_label}</span>
      <span class="badge badge-{liquidity_class}">{liquidity_label}</span>
    </div>
  </div>

  <div class="conclusion">{conclusion}</div>

  <h3 style="color:#8b949e;margin:16px 0 8px">📊 戦略比較</h3>
  <table>
    <tr>
      <th></th><th>S1（メイン）</th><th>C1（高精度版）</th>
    </tr>
    <tr>
      <td>Entry</td>
      <td class="long">{s1_entry}</td>
      <td class="long">{c1_entry}</td>
    </tr>
    <tr>
      <td>SL</td>
      <td>{s1_sl}</td><td>{c1_sl}</td>
    </tr>
    <tr>
      <td>TP</td>
      <td>{s1_tp}</td><td>{c1_tp1} → {c1_tp2}</td>
    </tr>
    <tr>
      <td>RRR</td>
      <td class="{s1_rrr_class}">{s1_rrr}</td>
      <td class="{c1_rrr_class}">{c1_rrr}</td>
    </tr>
    <tr>
      <td>EV</td>
      <td class="short">{s1_ev}円</td>
      <td class="neutral">{c1_ev}円</td>
    </tr>
    <tr>
      <td>有効時間</td>
      <td>{s1_valid}</td><td>{c1_valid}</td>
    </tr>
    <tr>
      <td>必要資金</td>
      <td>{s1_capital}</td><td>{c1_capital}</td>
    </tr>
  </table>

  <h3 style="color:#8b949e;margin:16px 0 8px">📍 価格マップ</h3>
  <div class="level-bar">
    {level_markers}
  </div>

  <h3 style="color:#8b949e;margin:16px 0 8px">⏰ タイムライン</h3>
  <div class="timeline">
    {timeline_items}
  </div>

  <h3 style="color:#8b949e;margin:16px 0 8px">🚦 Go/No-Go</h3>
  <div class="checklist">
    {checklist_items}
  </div>

  <div class="risk-box">
    <strong>🛡️ リスク</strong><br>
    {risk_summary}
  </div>

  <div style="color:#484f58;font-size:11px;margin-top:16px;text-align:center">
    本カードは投資助言ではなくトレード設計メモ。
    執行は板・歩み値・流動性を確認すること。
  </div>
</body>
</html>"""


def generate_html(strategy_json: dict) -> str:
    j = strategy_json
    meta = j["meta"]
    kl = j["key_levels"]

    s1 = next(
        (s for s in j["scenarios"] if s["id"] == "S1"), {}
    )
    c1 = next(
        (c for c in j["contingencies"] if c["id"] == "C1"), {}
    )

    # 価格マップのマーカー生成
    all_levels = {
        "SL(S1)": s1.get("sl"),
        "S2": kl.get("s2"),
        "Entry": s1.get("entry"),
        "VWAP": kl.get("vwap"),
        "S1": kl.get("s1"),
        "PDC": kl.get("pdc"),
        "PMH": kl.get("pmh"),
        "R1": kl.get("r1"),
    }

    prices = [v for v in all_levels.values() if v]
    if not prices:
        level_markers = ""
    else:
        p_min = min(prices) - 50
        p_max = max(prices) + 50
        p_range = p_max - p_min

        markers = []
        colors = {
            "SL(S1)": "#f85149", "S2": "#d29922",
            "Entry": "#3fb950", "VWAP": "#58a6ff",
            "S1": "#8b949e", "PDC": "#c9d1d9",
            "PMH": "#8b949e", "R1": "#8b949e",
        }
        for name, price in all_levels.items():
            if price is None:
                continue
            pct = (price - p_min) / p_range * 100
            color = colors.get(name, "#8b949e")
            markers.append(
                f'<div class="level-marker" '
                f'style="left:{pct:.1f}%;background:{color}">'
                f'<span class="level-label" '
                f'style="color:{color}">'
                f'{name}<br>{price:,.0f}</span></div>'
            )
        level_markers = "\n".join(markers)

    # タイムライン
    timeline_data = [
        ("09:00-09:15", "観察のみ（Toxic flow回避）"),
        ("09:15-10:30", "S1発動判定（RVOL≥1.5確認）"),
        ("10:30-11:30", "C1待機（S2保持確認中）"),
        ("12:30-13:00", "C1執行帯（唯一のRRR適合帯）"),
        ("13:00-14:00", "RRR不足帯（新規不可）"),
        ("14:00-14:30", "最終判断・手仕舞い"),
    ]
    timeline_items = "\n".join(
        f'<div class="timeline-item">'
        f'<span class="timeline-time">{t}</span>'
        f'<span>{desc}</span></div>'
        for t, desc in timeline_data
    )

    # チェックリスト
    checks = [
        "RVOL≥1.5を確認したか",
        "板の厚さ（売買気配100株以上）を確認したか",
        "寄り後15分の値幅がATR80%未満か",
        "ニュース・イベントを確認したか",
        "1トレード最大損失額を計算したか",
    ]
    checklist_items = "\n".join(
        f'<div class="check-item">'
        f'<div class="check-box"></div>{c}</div>'
        for c in checks
    )

    # 判定バッジ
    if s1.get("ev", 0) and s1["ev"] < 0:
        judgment_class = "warn"
        judgment_label = "条件付き"
    else:
        judgment_class = "ok"
        judgment_label = "エントリー可"

    surge = meta.get("volume_surge", 1.0)
    if surge and surge < 0.3:
        liquidity_class = "danger"
        liquidity_label = f"流動性⚠ {surge}"
    else:
        liquidity_class = "ok"
        liquidity_label = "流動性OK"

    return HTML_TEMPLATE.format(
        ticker=meta.get("ticker", ""),
        company=meta.get("company", ""),
        judgment_class=judgment_class,
        judgment_label=judgment_label,
        liquidity_class=liquidity_class,
        liquidity_label=liquidity_label,
        conclusion="S1条件付き。EV警告あり。C1(12:30-)が優位。",
        s1_entry=f"{s1.get('entry', 0):,.0f}",
        s1_sl=f"{s1.get('sl', 0):,.0f}",
        s1_tp=f"{s1.get('tp', 0):,.0f}",
        s1_rrr=s1.get("rrr", "N/A"),
        s1_rrr_class="neutral" if (
            s1.get("rrr", 0) and s1["rrr"] < 1.1
        ) else "long",
        s1_ev=f"{s1.get('ev', 0):+,.0f}",
        s1_valid=f"{s1.get('valid_from','')}〜{s1.get('valid_until','')}",
        s1_capital="6,200万円",
        c1_entry=f"{c1.get('entry', 0):,.0f}",
        c1_sl=f"{c1.get('sl', 0):,.0f}",
        c1_tp1=f"{c1.get('tp1', 0):,.0f}",
        c1_tp2=f"{c1.get('tp2', 0):,.0f}",
        c1_rrr=c1.get("rrr", "N/A"),
        c1_rrr_class="long",
        c1_ev=f"{c1.get('ev', 0):+,.0f}",
        c1_valid=f"{c1.get('valid_from','')}〜{c1.get('valid_until','')}",
        c1_capital="4,400万円",
        level_markers=level_markers,
        timeline_items=timeline_items,
        checklist_items=checklist_items,
        risk_summary=(
            f"1トレード最大損失: 総資金の0.1%以内（50%縮小後）<br>"
            f"SLタッチで即決済。逆指値を事前設定。<br>"
            f"14:00までに未発動なら本日終了。"
        ),
    )


if __name__ == "__main__":
    import sys
    import json
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    try:
        # JSONを読み込み
        json_file = sys.argv[1] if len(sys.argv) > 1 else "strategy.json"
        with open(json_file, 'r', encoding='utf-8') as f:
            strategy_json = json.load(f)
        print('JSON読み込み成功')

        # HTMLを生成
        html = generate_html(strategy_json)
        print('HTML生成成功')

        # ファイルに保存
        output_file = sys.argv[2] if len(sys.argv) > 2 else "output/6871_strategy_card.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f'ファイル保存成功: {output_file}')

        print('✅ HTML戦略カードを生成しました')
    except Exception as e:
        print(f'エラー: {e}')
        import traceback
        traceback.print_exc()
