"""
Report Generator Module

This module formats the analysis results into professional markdown reports
combining quantitative data with qualitative narrative analysis.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generates professional trading analysis reports"""

    def __init__(self):
        """Initialize the report generator"""
        self.report_template = self._get_report_template()

    def generate_report(
        self,
        ticker: str,
        raw_data: Dict[str, Any],
        thought_process: Dict[str, Any],
        mode: str = "daytrade"
    ) -> str:
        """
        Generate a professional markdown report

        Args:
            ticker: Stock ticker symbol
            raw_data: Raw data from DataFetcher
            thought_process: Analysis results from Analyzer
            mode: Analysis mode ('daytrade' or 'swing')

        Returns:
            Formatted markdown report
        """
        logger.info(f"Generating report for {ticker}")

        try:
            # Extract data components
            price_data = raw_data.get('price_data', {})
            technical_indicators = raw_data.get('technical_indicators', {})
            moving_averages = raw_data.get('moving_averages', {})
            qualitative_data = raw_data.get('qualitative_data', {})
            metadata = raw_data.get('metadata', {})

            # Extract thought process components
            narrative_analysis = thought_process.get('stage_1_narrative', {})
            strategy_analysis = thought_process.get('stage_2_strategy', {})
            meta_analysis = thought_process.get('meta_analysis', {})

            # Build report sections
            report_parts = []

            # 1. Header Section
            report_parts.append(self._generate_header(ticker, mode, metadata))

            # 2. Executive Summary
            report_parts.append(self._generate_executive_summary(
                ticker, price_data, meta_analysis
            ))

            # 3. Current Market Situation (Quantitative)
            report_parts.append(self._generate_current_situation(
                ticker, price_data, technical_indicators
            ))

            # 4. Technical & Supply-Demand Narrative (Qualitative)
            report_parts.append(self._generate_narrative_section(
                narrative_analysis, moving_averages, qualitative_data
            ))

            # 5. Trading Scenarios (If-Then Strategy)
            report_parts.append(self._generate_strategy_section(
                strategy_analysis, technical_indicators, mode
            ))

            # 6. Risk Assessment
            report_parts.append(self._generate_risk_section(
                meta_analysis, technical_indicators
            ))

            # 7. Disclaimer
            report_parts.append(self._generate_disclaimer())

            # Combine all sections
            full_report = "\n\n".join(report_parts)

            return full_report

        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            return f"Report generation failed: {str(e)}"

    def _generate_header(
        self,
        ticker: str,
        mode: str,
        metadata: Dict[str, Any]
    ) -> str:
        """Generate report header"""
        timestamp = metadata.get('fetched_at', datetime.now().isoformat())
        company_name = metadata.get('company_name', 'Unknown Company')

        header = f"""# {company_name} ({ticker}) 株式分析レポート

**分析モード**: {mode.upper()}トレード
**生成日時**: {timestamp.replace('T', ' ')}

---

"""
        return header

    def _generate_executive_summary(
        self,
        ticker: str,
        price_data: Dict[str, Any],
        meta_analysis: Dict[str, Any]
    ) -> str:
        """Generate executive summary section"""
        current_price = price_data.get('current_price', {})
        overall_sentiment = meta_analysis.get('overall_sentiment', 'neutral')
        confidence = meta_analysis.get('confidence_level', 'medium')

        sentiment_emoji = {
            'bullish': '📈',
            'bearish': '📉',
            'neutral': '➡️'
        }.get(overall_sentiment, '➡️')

        summary = f"""## 1. エグゼクティブサマリー

**現在値**: {current_price.get('value', 0):,.0f}円 ({current_price.get('change', 0):+,.0f}円 / {current_price.get('change_percent', 0):+.1f}%)
**全体センチメント**: {sentiment_emoji} {overall_sentiment.upper()}
**分析信頼度**: {confidence.upper()}

### 市場状況の概要
現在の相場は **{overall_sentiment}** トレンドです。移動平均線の分析から、{self._get_market_phase_description(meta_analysis)}。

### 主要な注目点
{self._generate_key_points(meta_analysis, price_data)}

---

"""
        return summary

    def _generate_current_situation(
        self,
        ticker: str,
        price_data: Dict[str, Any],
        technical_indicators: Dict[str, Any]
    ) -> str:
        """Generate current market situation section"""
        current_price = price_data.get('current_price', {})
        historical = price_data.get('historical', {})

        situation = f"""## 2. 現在の市場状況（定量データ）

### 株価情報
| 指標 | 数値 |
|------|------|
| 現在値 | {current_price.get('value', 0):,.0f}円 |
| 前日比 | {current_price.get('change', 0):+,.0f}円 ({current_price.get('change_percent', 0):+.1f}%) |
| 当日高値 | {current_price.get('high', 0):,.0f}円 |
| 当日安値 | {current_price.get('low', 0):,.0f}円 |
| 出来高 | {current_price.get('volume', 0):,}株 |

### 年初来パフォーマンス
| 指標 | 数値 |
|------|------|
| 年初来高値 | {historical.get('ytd_high', 0):,.0f}円 |
| 年初来安値 | {historical.get('ytd_low', 0):,.0f}円 |
| 平均出来高 | {historical.get('avg_volume', 0):,}株 |

### 主要テクニカル指標
{self._format_technical_indicators_table(technical_indicators)}

---

"""
        return situation

    def _generate_narrative_section(
        self,
        narrative_analysis: Dict[str, Any],
        moving_averages: Dict[str, Any],
        qualitative_data: Dict[str, Any]
    ) -> str:
        """Generate narrative context section"""
        # Extract narrative text
        narrative_text = narrative_analysis.get('analysis_text', '')

        # Generate MA context
        ma_context = self._generate_ma_context(moving_averages)

        # Generate price action context
        price_action_context = self._generate_price_action_context(qualitative_data)

        narrative = f"""## 3. テクニカル＆需給の文脈（Narrative Context）

### 移動平均の並び（MAコンテクスト）
{ma_context}

### プライスアクションと需給
{price_action_context}

### LLMによる詳細分析
{narrative_text if narrative_text else "*詳細な分析データが利用可能になると表示されます*"}

---

"""
        return narrative

    def _generate_strategy_section(
        self,
        strategy_analysis: Dict[str, Any],
        technical_indicators: Dict[str, Any],
        mode: str
    ) -> str:
        """Generate trading strategy section"""
        strategy_text = strategy_analysis.get('strategy_text', '')
        atr = technical_indicators.get('atr', {}).get('current', 0)

        # Generate basic scenarios based on ATR
        current_price = technical_indicators.get('current_price', 0)  # Would need to be passed
        basic_scenarios = self._generate_basic_atr_scenarios(atr, mode)

        strategy = f"""## 4. 取引シナリオ（If-Then Strategy）

### 基本シナリオ（ATRベース）
{basic_scenarios}

### LLMによる高度な戦略
{strategy_text if strategy_text else "*高度な戦略分析データが利用可能になると表示されます*"}

### リスク管理の原則
- **ATRに基づく損切り**: ボラティリティを考慮した動的ストップロス
- **最小RRR**: 1.0以上、推奨は1.5-2.0以上
- **ポジションサイジング**: ATRと口座リスクに基づくサイズ調整
- **ギャップリスク**: デイトレードでは特にギャップリスクを考慮

---

"""
        return strategy

    def _generate_risk_section(
        self,
        meta_analysis: Dict[str, Any],
        technical_indicators: Dict[str, Any]
    ) -> str:
        """Generate risk assessment section"""
        risks = meta_analysis.get('risks', [])
        opportunities = meta_analysis.get('opportunities', [])

        # Add technical-based risks
        rsi_status = technical_indicators.get('rsi', {}).get('status', 'neutral')
        if rsi_status == 'overbought':
            risks.insert(0, "RSIが70以上でオーバーバイト状態 - 調整リスク")
        elif rsi_status == 'oversold':
            risks.insert(0, "RSIが30以下でオーバーセル状態 - 反発または急落の可能性")

        risk_assessment = f"""## 5. リスク評価

### 主要リスク要因
{self._format_list_items(risks) if risks else "- 特定のリスク要因は検出されていません"}

### 主要機会
{self._format_list_items(opportunities) if opportunities else "- 特定の機会は検出されていません"}

### 取引における注意点
1. **データの制限**: 過去のデータが未来を保証するものではありません
2. **不確実性**: 市場は予測不可能であり、急変する可能性があります
3. **リスク管理**: 常に損切りルールを厳守し、適切なポジションサイズを維持してください
4. **情報の検証**: 重要な判断をする前に、複数の情報源を確認することをお勧めします

---

"""
        return risk_assessment

    def _generate_disclaimer(self) -> str:
        """Generate disclaimer section"""
        disclaimer = """## 免責事項

このレポートは情報提供のみを目的としており、投資助言を意図するものではありません。ここに含まれる情報は信頼できる情報源に基づいていますが、その正確性や完全性は保証されません。

このレポートに基づいて行われるいかなる投資決定も、読者ご自身の判断と責任において行われるべきです。投資には元本を失うリスクが伴います。投資決定を行う前に、必要な調査と専門家の助言を受けることを強くお勧めします。

**免責**: このレポートの作成者および提供者は、この情報の使用により生じたいかなる損失についても責任を負いません。

---

*このレポートはAI分析システムによって生成されました*
"""
        return disclaimer

    # Helper methods
    def _get_market_phase_description(self, meta_analysis: Dict[str, Any]) -> str:
        """Get description of current market phase"""
        conditions = meta_analysis.get('key_conditions', {})
        trend = conditions.get('trend_alignment', 'unknown')

        descriptions = {
            'perfect_bullish_order': '短期・中期・長期のトレンドが一致しており、強気相場が継続中です',
            'perfect_bearish_order': '全てのトレンドが弱気方向を示しており、下降トレンドが継続中です',
            'conflict': '短期と長期のトレンドが対立しており、相場の転換期または調整期の可能性があります',
            'transitioning': 'トレンドの転換期であり、方向性が定まりつつあります'
        }

        return descriptions.get(trend, '相場の方向性を分析中')

    def _generate_key_points(
        self,
        meta_analysis: Dict[str, Any],
        price_data: Dict[str, Any]
    ) -> str:
        """Generate bullet points of key observations"""
        points = []

        # Add sentiment-based point
        sentiment = meta_analysis.get('overall_sentiment', 'neutral')
        if sentiment == 'bullish':
            points.append("- ✅ 上昇モメンタムが継続しており、押し目買いの機会がある可能性")
        elif sentiment == 'bearish':
            points.append("- ⚠️ 下降圧力が強く、戻り売りまたは様子見が推奨される可能性")
        else:
            points.append("- ⏳ トレンドが不透明であり、明確な方向性が出るまで慎重な姿勢が必要")

        # Add volatility-based point
        volatility = meta_analysis.get('key_conditions', {}).get('volatility_level', 'medium')
        if volatility == 'high':
            points.append("- 📊 ボラティリティが高く、急変動のリスクがあるため適切な損切りが重要")

        # Add technical-based point
        current_price = price_data.get('current_price', {}).get('value', 0)
        if current_price:
            points.append(f"- 💹 現在値 {current_price:,.0f}円 での需給バランスを注視")

        return "\n".join(points) if points else "- 注目すべき特記事項はありません"

    def _format_technical_indicators_table(self, technical: Dict[str, Any]) -> str:
        """Format technical indicators as markdown table"""
        table_lines = [
            "| 指標 | 値 | 状態 |",
            "|------|-----|------|"
        ]

        # Add indicators
        atr = technical.get('atr', {})
        table_lines.append(f"| ATR | {atr.get('current', 0):.0f} | - |")

        vwap = technical.get('vwap', 0)
        table_lines.append(f"| VWAP | {vwap:.0f} | - |")

        rsi = technical.get('rsi', {})
        table_lines.append(f"| RSI | {rsi.get('current', 0):.1f} | {rsi.get('status', 'neutral')} |")

        macd = technical.get('macd', {})
        table_lines.append(f"| MACD | {macd.get('macd', 0):.0f} | シグナル: {macd.get('signal', 0):.0f} |")

        return "\n".join(table_lines)

    def _generate_ma_context(self, ma_data: Dict[str, Any]) -> str:
        """Generate moving average context"""
        context_lines = []

        # Analyze MA alignment
        alignment = ma_data.get('trend_alignment', {})
        alignment_status = alignment.get('status', 'unknown')

        # Generate individual MA descriptions
        for period in [5, 25, 75, 200]:
            ma_info = ma_data.get(f"{period}_day", {})
            if ma_info:
                value = ma_info.get('value', 0)
                deviation = ma_info.get('deviation_percent', 0)
                position = ma_info.get('position', 'unknown')
                trend = ma_info.get('trend', 'unknown')

                trend_jp = {"uptrend": "上昇中", "downtrend": "下降中", "sideways": "横ばい"}.get(trend, '不明')
                position_jp = {"above": "上回っている", "below": "下回っている"}.get(position, '不明')

                context_lines.append(
                    f"- **{period}日MA**: {value:,.0f}円 ({deviation:+.1f}%) - "
                    f"現在値から{position_jp}、{trend_jp}"
                )

        # Add overall trend assessment
        if alignment_status == 'perfect_bullish_order':
            context_lines.append("\n📈 **全体トレンド**: パーフェクトブルオーダー - 強い上昇トレンド")
        elif alignment_status == 'perfect_bearish_order':
            context_lines.append("\n📉 **全体トレンド**: パーフェクトベアオーダー - 強い下降トレンド")
        elif alignment_status == 'conflict':
            context_lines.append("\n⚠️ **全体トレンド**: トレンド対立 - 短期と長期の方向が異なっています")
        else:
            context_lines.append("\n➡️ **全体トレンド**: トレンド転換期または形成中")

        return "\n".join(context_lines)

    def _generate_price_action_context(self, qual_data: Dict[str, Any]) -> str:
        """Generate price action context"""
        context_lines = []

        price_action = qual_data.get('price_action', {})
        momentum = price_action.get('momentum', 'neutral')
        volatility = price_action.get('volatility_level', 'medium')

        momentum_emoji = {"bullish": "🐂", "bearish": "🐻", "neutral": "😐"}.get(momentum, "😐")
        context_lines.append(f"- **勢い**: {momentum_emoji} {momentum} - {'買い優勢' if momentum == 'bullish' else '売り優勢' if momentum == 'bearish' else '均衡'}")

        volatility_emoji = {"high": "🔥", "medium": "⚡", "low": "🌊"}.get(volatility, "🌊")
        context_lines.append(f"- **ボラティリティ**: {volatility_emoji} {volatility}")

        # Check for significant moves
        significant_moves = price_action.get('significant_moves', [])
        if significant_moves:
            context_lines.append("- **直近の大きな動き**:")
            for move in significant_moves[-2:]:  # Last 2 moves
                date = move['date']
                change = move['change_percent']
                move_type = move['type']
                emoji = "🚀" if move_type == "surge" else "💥"
                context_lines.append(f"  - {emoji} {date}: {change:+.1f}%")

        # Check for patterns
        patterns = qual_data.get('patterns', [])
        if patterns:
            pattern_emojis = {
                "double_bottom": "🔻",
                "double_top": "🔺",
                "v_recovery": "V"
            }
            pattern_display = ", ".join([
                f"{pattern_emojis.get(p, '📊')}{p}"
                for p in patterns
            ])
            context_lines.append(f"- **検出されたパターン**: {pattern_display}")

        # Check alerts
        alerts = qual_data.get('alerts', [])
        if alerts:
            context_lines.append("\n⚠️ **アラート**:")
            for alert in alerts:
                context_lines.append(f"  - {alert}")

        return "\n".join(context_lines)

    def _generate_basic_atr_scenarios(self, atr: float, mode: str) -> str:
        """Generate basic trading scenarios based on ATR"""
        if atr <= 0:
            return "ATRデータが利用できません。詳細な分析を待ってください。"

        scenarios = []

        # Scenario 1: Conservative
        scenarios.append(f"""**シナリオ1: 保守的アプローチ**
- **Entry**: 現在の価格レベルでエントリーを検討
- **TP**: 現在値 + (ATR × 1.5) = 約 +{atr * 1.5:.0f}円
- **SL**: 現在値 - (ATR × 1.0) = 約 -{atr:.0f}円
- **RRR**: 1.5
- **Probability**: High
- **Time Horizon**: {'当日中' if mode == 'daytrade' else '3-5日'}
- **Position Size**: 1% of capital""")

        # Scenario 2: Aggressive
        scenarios.append(f"""
**シナリオ2: 積極的アプローチ**
- **Entry**: 強いトレンド確認後の追い買い
- **TP**: 現在値 + (ATR × 2.5) = 約 +{atr * 2.5:.0f}円
- **SL**: 現在値 - (ATR × 1.0) = 約 -{atr:.0f}円
- **RRR**: 2.5
- **Probability**: Medium
- **Time Horizon**: {'当日中' if mode == 'daytrade' else '5-7日'}
- **Position Size**: 0.5% of capital""")

        return "\n".join(scenarios)

    def _format_list_items(self, items: list) -> str:
        """Format a list as bullet points"""
        if not items:
            return "- 該当なし"
        return "\n".join([f"- {item}" for item in items])

    def _get_report_template(self) -> str:
        """Get the report template structure"""
        return """
# {Company Name} ({Ticker}) Analysis Report

## 1. Executive Summary
[Summary content]

## 2. Current Market Situation
[Quantitative data]

## 3. Technical & Supply-Demand Narrative
[Qualitative analysis]

## 4. Trading Scenarios
[If-Then strategies]

## 5. Risk Assessment
[Risk analysis]

## Disclaimer
[Legal disclaimer]
"""
