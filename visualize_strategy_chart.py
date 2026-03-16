"""
トレーディングチャート図解付きHTML戦略カード。
視覚的なチャートでエントリータイミングを示す。
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
    padding: 16px; max-width: 900px; margin: 0 auto;
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

  /* 新規：チャートコンテナ */
  .chart-container {{
    background: #161b22; padding: 16px; margin: 12px 0;
    border-radius: 6px; border: 1px solid #30363d;
  }}
  .chart-title {{
    font-size: 14px; font-weight: bold; margin-bottom: 12px;
    color: #8b949e;
  }}
  .chart-legend {{
    display: flex; gap: 16px; margin-top: 8px;
    font-size: 11px; color: #8b949e;
  }}
  .legend-item {{
    display: flex; align-items: center; gap: 6px;
  }}
  .legend-color {{
    width: 12px; height: 12px; border-radius: 2px;
  }}
  .chart-notes {{
    margin-top: 12px; font-size: 11px; color: #8b949e;
    line-height: 1.5;
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

  <!-- 新規：チャート図解 -->
  <h3 style="color:#8b949e;margin:16px 0 8px">📈 エントリータイミングチャート</h3>
  <div class="chart-container">
    <div class="chart-title">価格推移とエントリーポイント（S1/C1）</div>
    {chart_svg}
    <div class="chart-legend">
      <div class="legend-item">
        <div class="legend-color" style="background: #3fb950;"></div>
        <span>エントリー</span>
      </div>
      <div class="legend-item">
        <div class="legend-color" style="background: #f85149;"></div>
        <span>ストップロス (SL)</span>
      </div>
      <div class="legend-item">
        <div class="legend-color" style="background: #58a6ff;"></div>
        <span>ターゲット (TP)</span>
      </div>
      <div class="legend-item">
        <div class="legend-color" style="background: #d29922;"></div>
        <span>キーレベル</span>
      </div>
    </div>
    <div class="chart-notes">
      <strong>チャートの読み方：</strong><br>
      • 縦軸：価格（円）｜横軸：時間（09:00〜15:00）<br>
      • <span style="color:#3fb950">緑の矢印</span>：エントリータイミング｜<span style="color:#f85149">赤い線</span>：ストップロス<br>
      • <span style="color:#58a6ff">青い線</span>：利益確定ポイント｜<span style="color:#d29922">黄色い点</span>：キーレベル
    </div>
  </div>

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


def generate_chart_svg(kl: dict, s1: dict, c1: dict) -> str:
    """視覚的なチャートSVGを生成"""

    # 価格レンジ
    prices = [
        kl.get("s2"), kl.get("s1"), s1.get("entry"), s1.get("sl"),
        s1.get("tp"), c1.get("entry"), c1.get("sl"), c1.get("tp1"), c1.get("tp2")
    ]
    valid_prices = [p for p in prices if p is not None]

    if not valid_prices:
        return "<div>チャートデータ不足</div>"

    p_min = min(valid_prices) - 50
    p_max = max(valid_prices) + 50
    p_range = p_max - p_min

    # SVG設定
    svg_width = 800
    svg_height = 250
    chart_width = 700
    chart_height = 200
    margin_left = 60
    margin_bottom = 30

    # 価格をY座標に変換
    def price_to_y(price):
        if price is None:
            return chart_height / 2
        return chart_height - ((price - p_min) / p_range * chart_height)

    # 時間をX座標に変換（09:00〜15:00）
    def time_to_x(time_str):
        hour, minute = map(int, time_str.split(':'))
        minutes = hour * 60 + minute - 9 * 60
        return margin_left + (minutes / 360 * chart_width)

    svg_parts = []

    # 価格軸
    for i, price in enumerate([p_min, (p_min + p_max) / 2, p_max]):
        y = price_to_y(price)
        svg_parts.append(f'''
          <line x1="{margin_left}" y1="{y}" x2="{svg_width - margin_left}" y2="{y}"
                stroke="#30363d" stroke-width="1" stroke-dasharray="4,4"/>
          <text x="{margin_left - 10}" y="{y + 4}" fill="#8b949e"
                font-size="10" text-anchor="end">{price:,.0f}</text>
        ''')

    # 時間軸
    for hour in range(9, 16):
        x = time_to_x(f"{hour}:00")
        svg_parts.append(f'''
          <line x1="{x}" y1="0" x2="{x}" y2="{chart_height}"
                stroke="#30363d" stroke-width="1" stroke-dasharray="4,4"/>
          <text x="{x}" y="{chart_height + 15}" fill="#8b949e"
                font-size="10" text-anchor="middle">{hour}:00</text>
        ''')

    # キーレベル
    key_levels = {
        "PDC": kl.get("pdc"),
        "PMH": kl.get("pmh"),
        "R1": kl.get("r1"),
    }

    for name, price in key_levels.items():
        if price is not None:
            y = price_to_y(price)
            svg_parts.append(f'''
              <line x1="{margin_left}" y1="{y}" x2="{svg_width - margin_left}" y2="{y}"
                    stroke="#d29922" stroke-width="1" stroke-dasharray="2,2"/>
              <circle cx="{svg_width - margin_left - 5}" cy="{y}" r="3" fill="#d29922"/>
              <text x="{svg_width - margin_left - 10}" y="{y + 3}" fill="#d29922"
                    font-size="9" text-anchor="end">{name}</text>
            ''')

    # S1ライン
    if s1.get("entry"):
        entry_y = price_to_y(s1["entry"])
        sl_y = price_to_y(s1["sl"])
        tp_y = price_to_y(s1["tp"])
        entry_x = time_to_x("09:30")

        # Entryポイント（緑矢印）
        svg_parts.append(f'''
          <polygon points="{entry_x},{entry_y + 5} {entry_x - 5},{entry_y - 5} {entry_x + 5},{entry_y - 5}"
                   fill="#3fb950" stroke="#2da44e" stroke-width="1"/>
          <text x="{entry_x + 10}" y="{entry_y}" fill="#3fb950" font-size="10">S1 Entry</text>
          <text x="{entry_x + 10}" y="{entry_y + 12}" fill="#8b949e" font-size="9">{s1["entry"]:,.0f}</text>
        ''')

        # SLライン（赤）
        svg_parts.append(f'''
          <line x1="{entry_x}" y1="{entry_y}" x2="{time_to_x('15:00')}" y2="{sl_y}"
                stroke="#f85149" stroke-width="2" stroke-dasharray="4,4"/>
          <text x="{time_to_x('14:30')}" y="{sl_y - 5}" fill="#f85149" font-size="9">S1 SL: {s1["sl"]:,.0f}</text>
        ''')

        # TPライン（青）
        svg_parts.append(f'''
          <line x1="{entry_x}" y1="{entry_y}" x2="{time_to_x('15:00')}" y2="{tp_y}"
                stroke="#58a6ff" stroke-width="2" stroke-dasharray="4,4"/>
          <text x="{time_to_x('14:30')}" y="{tp_y + 15}" fill="#58a6ff" font-size="9">S1 TP: {s1["tp"]:,.0f}</text>
        ''')

    # C1ライン
    if c1.get("entry"):
        entry_y = price_to_y(c1["entry"])
        sl_y = price_to_y(c1["sl"])
        tp1_y = price_to_y(c1["tp1"])
        tp2_y = price_to_y(c1["tp2"])
        entry_x = time_to_x("12:45")

        # Entryポイント（緑矢印）
        svg_parts.append(f'''
          <polygon points="{entry_x},{entry_y + 5} {entry_x - 5},{entry_y - 5} {entry_x + 5},{entry_y - 5}"
                   fill="#3fb950" stroke="#2da44e" stroke-width="1"/>
          <text x="{entry_x + 10}" y="{entry_y}" fill="#3fb950" font-size="10">C1 Entry</text>
          <text x="{entry_x + 10}" y="{entry_y + 12}" fill="#8b949e" font-size="9">{c1["entry"]:,.0f}</text>
        ''')

        # SLライン（赤）
        svg_parts.append(f'''
          <line x1="{entry_x}" y1="{entry_y}" x2="{time_to_x('15:00')}" y2="{sl_y}"
                stroke="#f85149" stroke-width="2" stroke-dasharray="4,4"/>
          <text x="{time_to_x('14:30')}" y="{sl_y - 5}" fill="#f85149" font-size="9">C1 SL: {c1["sl"]:,.0f}</text>
        ''')

        # TPライン（青）
        svg_parts.append(f'''
          <line x1="{entry_x}" y1="{entry_y}" x2="{time_to_x('15:00')}" y2="{tp1_y}"
                stroke="#58a6ff" stroke-width="2" stroke-dasharray="4,4"/>
          <text x="{time_to_x('14:30')}" y="{tp1_y - 5}" fill="#58a6ff" font-size="9">C1 TP1: {c1["tp1"]:,.0f}</text>
        ''')

        svg_parts.append(f'''
          <line x1="{entry_x}" y1="{entry_y}" x2="{time_to_x('15:00')}" y2="{tp2_y}"
                stroke="#58a6ff" stroke-width="2" stroke-dasharray="4,4"/>
          <text x="{time_to_x('14:30')}" y="{tp2_y - 5}" fill="#58a6ff" font-size="9">C1 TP2: {c1["tp2"]:,.0f}</text>
        ''')

    # サンプル価格推移（ギザギザ線）
    sample_prices = [10440, 10460, 10440, 10420, 10430, 10450, 10440, 10460]
    for i in range(len(sample_prices) - 1):
        x1 = margin_left + (i / len(sample_prices) * chart_width)
        x2 = margin_left + ((i + 1) / len(sample_prices) * chart_width)
        y1 = price_to_y(sample_prices[i])
        y2 = price_to_y(sample_prices[i + 1])

        svg_parts.append(f'''
          <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"
                stroke="#8b949e" stroke-width="1.5"/>
        ''')

    svg_content = f'''
      <svg width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}">
        <rect width="{svg_width}" height="{svg_height}" fill="#161b22" rx="6"/>
        {"".join(svg_parts)}
      </svg>
    '''

    return svg_content


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

    # チャートSVGを生成
    chart_svg = generate_chart_svg(kl, s1, c1)

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
        chart_svg=chart_svg,
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
        output_file = sys.argv[2] if len(sys.argv) > 2 else "output/6871_strategy_card_chart.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f'ファイル保存成功: {output_file}')

        print('✅ チャート図解付きHTML戦略カードを生成しました')
    except Exception as e:
        print(f'エラー: {e}')
        import traceback
        traceback.print_exc()
