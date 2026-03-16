"""
Stock Analyzer Module

This module handles LLM-based reasoning and analysis combining
quantitative data with qualitative narrative reasoning.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
import os
from datetime import datetime

# Import ZhipuAI SDK
from zhipuai import ZhipuAI

logger = logging.getLogger(__name__)


class StockAnalyzer:
    """LLM-based stock analysis engine with Chain of Thought reasoning"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the analyzer with ZhipuAI API client"""
        self.api_key = api_key or os.getenv("GLM_KEY")
        if not self.api_key:
            logger.warning("GLM_KEY not found. Some features may be limited.")

        self.client = ZhipuAI(api_key=self.api_key) if self.api_key else None
        self.model = "glm-4.7-flashx"  # 智谱公式モデル名 (glm-4.7-flashは非公式)

    async def analyze_stock(
        self,
        ticker: str,
        raw_data: Dict[str, Any],
        mode: str = "daytrade"
    ) -> Dict[str, Any]:
        """
        Perform comprehensive stock analysis using LLM reasoning

        This implements a two-stage Chain of Thought process:
        1. Narrative & Trend Analysis (qualitative reasoning)
        2. Actionable Strategy Development (quantitative + qualitative synthesis)

        Args:
            ticker: Stock ticker symbol
            raw_data: Fetched data from DataFetcher
            mode: Analysis mode ('daytrade' or 'swing')

        Returns:
            Dictionary containing thought process and analysis results
        """
        logger.info(f"Starting LLM analysis for {ticker} in {mode} mode")

        thought_process = {
            "stage_1_narrative": await self._perform_narrative_analysis(ticker, raw_data, mode),
            "stage_2_strategy": await self._perform_strategy_analysis(ticker, raw_data, mode),
            "meta_analysis": await self._perform_meta_analysis(ticker, raw_data, mode)
        }

        return thought_process

    async def _perform_narrative_analysis(
        self,
        ticker: str,
        raw_data: Dict[str, Any],
        mode: str
    ) -> Dict[str, Any]:
        """
        Stage 1: Narrative & Trend Analysis

        This stage focuses on understanding:
        - MA alignment and trend conflicts
        - Recent price action patterns
        - Market sentiment and supply-demand dynamics
        """

        # Prepare data summary for LLM
        data_summary = self._prepare_narrative_data_summary(raw_data, mode)

        prompt = f"""You are a professional stock market analyst specializing in Japanese equities.

## Your Task
Analyze the following stock data and provide a narrative understanding of the current market situation.

## Stock Information
- Ticker: {ticker}
- Analysis Mode: {mode.upper()}
- Current Price: {raw_data.get('price_data', {}).get('current_price', {}).get('value', 'N/A')}

## Market Data
{data_summary}

## Required Analysis
Please analyze the following three aspects and provide detailed insights:

### 1. Trend Conflict Analysis
- Analyze the alignment of moving averages (5, 25, 75, 200 days)
- Identify if there's a conflict between short-term and long-term trends
- Determine if we have a "perfect order" or trend transition

### 2. Recent Price Action
- Analyze recent price movements and patterns
- Identify any significant surges, plunges, or V-shaped recoveries
- Determine the current phase (correction, rebound, consolidation, etc.)

### 3. Supply-Demand Dynamics
- Assess market sentiment from volume and price velocity
- Identify potential short squeeze (踏み上げ) or profit-taking risks
- Evaluate the balance between buyers and sellers

## Output Format
Please provide your analysis in a structured format:
1. **Trend Analysis**: [Your analysis of MA alignment and trends]
2. **Price Action**: [Your analysis of recent movements]
3. **Supply-Demand**: [Your analysis of market dynamics]
4. **Narrative Conclusion**: [A 2-3 sentence summary of the current market situation]

Focus on professional, actionable insights that would be valuable for a {mode} trader."""

        try:
            if self.client:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=2000
                )
                analysis_text = response.choices[0].message.content
            else:
                # Fallback to simple analysis if no API key
                analysis_text = self._fallback_narrative_analysis(raw_data, mode)

            # Parse the analysis into structured format
            parsed_analysis = self._parse_narrative_analysis(analysis_text)

            return {
                "analysis_text": analysis_text,
                "structured_insights": parsed_analysis,
                "confidence": "high" if self.client else "low",
                "generated_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error in narrative analysis: {str(e)}")
            return {
                "analysis_text": f"Analysis unavailable: {str(e)}",
                "structured_insights": {},
                "confidence": "error",
                "error": str(e)
            }

    async def _perform_strategy_analysis(
        self,
        ticker: str,
        raw_data: Dict[str, Any],
        mode: str
    ) -> Dict[str, Any]:
        """
        Stage 2: Actionable Strategy Development

        This stage combines:
        - Quantitative data (ATR, VWAP, technical indicators)
        - Qualitative insights from Stage 1
        - Professional trading principles (RRR >= 1.0)

        Output: Concrete If-Then scenarios with entry/exit points
        """

        # Prepare technical data summary
        tech_summary = self._prepare_technical_data_summary(raw_data, mode)

        prompt = f"""You are an expert technical analyst and {mode} trading strategist.

## Your Task
Based on the technical data below, design high-probability trading scenarios with proper risk management.

## Stock Information
- Ticker: {ticker}
- Analysis Mode: {mode.upper()}

## Technical Data
{tech_summary}

## Required Analysis
Design 2-3 If-Then trading scenarios that meet professional standards:

### For Each Scenario Provide:
1. **Entry Condition**: Clear trigger (price level, pattern break, etc.)
2. **Take Profit (TP)**: Target with rationale
3. **Stop Loss (SL)**: Protection level with rationale
4. **Risk-Reward Ratio (RRR)**: Must be >= 1.0
5. **Probability Assessment**: Your confidence level (High/Medium/Low)
6. **Time Horizon**: Expected duration of the trade
7. **Position Size Recommendation**: Based on ATR and account risk

### Risk Management Rules:
- Always use ATR-based stop losses where possible
- Minimum RRR of 1.0, preferably 1.5-2.0+
- Consider volatility in position sizing
- Account for gap risk (especially for day trading)

## Output Format
Provide scenarios in this exact format:

**Scenario 1: [Brief Name]**
- **Entry**: When price breaks [level] with [volume confirmation]
- **TP**: [price level] (Rationale: [reason])
- **SL**: [price level] (Rationale: [reason])
- **RRR**: [X.X] (Calculated as [TP-Entry] / [Entry-SL])
- **Probability**: [High/Medium/Low]
- **Time Horizon**: [expected duration]
- **Position Size**: [percentage of capital]

(Repeat for Scenario 2 and 3 if applicable)

**Overall Strategy Summary**: [1-2 sentence summary of the best opportunity]"""

        try:
            if self.client:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=2000
                )
                strategy_text = response.choices[0].message.content
            else:
                # Fallback to simple strategy if no API key
                strategy_text = self._fallback_strategy_analysis(raw_data, mode)

            # Parse the strategy into structured format
            parsed_strategy = self._parse_strategy_analysis(strategy_text)

            return {
                "strategy_text": strategy_text,
                "structured_scenarios": parsed_strategy,
                "confidence": "high" if self.client else "low",
                "generated_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error in strategy analysis: {str(e)}")
            return {
                "strategy_text": f"Strategy unavailable: {str(e)}",
                "structured_scenarios": [],
                "confidence": "error",
                "error": str(e)
            }

    async def _perform_meta_analysis(
        self,
        ticker: str,
        raw_data: Dict[str, Any],
        mode: str
    ) -> Dict[str, Any]:
        """
        Meta Analysis: Combine insights from both stages and provide overall assessment

        This stage:
        - Validates consistency between narrative and strategy
        - Identifies any red flags or conflicts
        - Provides overall trading recommendation
        """

        # Get insights from previous stages (would normally be passed as parameters)
        # For now, create a summary based on raw data
        price_data = raw_data.get('price_data', {})
        technical = raw_data.get('technical_indicators', {})
        qualitative = raw_data.get('qualitative_data', {})

        # Analyze overall conditions
        current_price = price_data.get('current_price', {}).get('value', 0)
        rsi_status = technical.get('rsi', {}).get('status', 'neutral')
        momentum = qualitative.get('price_action', {}).get('momentum', 'neutral')

        # Generate meta assessment
        conditions = {
            "price_momentum": momentum,
            "rsi_condition": rsi_status,
            "volatility_level": qualitative.get('price_action', {}).get('volatility_level', 'medium'),
            "trend_alignment": raw_data.get('moving_averages', {}).get('trend_alignment', {}).get('status', 'unknown')
        }

        # Determine overall recommendation
        if conditions['price_momentum'] == 'bullish' and conditions['rsi_condition'] in ['neutral', 'oversold']:
            overall_sentiment = 'bullish'
        elif conditions['price_momentum'] == 'bearish' and conditions['rsi_condition'] in ['neutral', 'overbought']:
            overall_sentiment = 'bearish'
        else:
            overall_sentiment = 'neutral'

        # Identify key risks
        risks = []
        if conditions['volatility_level'] == 'high':
            risks.append("High volatility may cause rapid price movements")
        if conditions['rsi_condition'] == 'overbought':
            risks.append("Overbought RSI suggests potential pullback")
        if conditions['rsi_condition'] == 'oversold':
            risks.append("Oversold RSI suggests potential bounce or further decline")

        # Identify key opportunities
        opportunities = []
        if conditions['price_momentum'] == 'bullish':
            opportunities.append("Positive momentum may continue if support holds")
        if conditions['rsi_condition'] == 'oversold':
            opportunities.append("Oversold conditions may present bargain hunting opportunity")

        meta_analysis = {
            "overall_sentiment": overall_sentiment,
            "trading_mode": mode,
            "key_conditions": conditions,
            "risks": risks,
            "opportunities": opportunities,
            "confidence_level": self._calculate_confidence(raw_data),
            "generated_at": datetime.now().isoformat()
        }

        return meta_analysis

    # Helper methods
    def _prepare_narrative_data_summary(self, raw_data: Dict[str, Any], mode: str) -> str:
        """Prepare a summary of data for narrative analysis"""
        summary_lines = []

        # Moving Averages
        ma_data = raw_data.get('moving_averages', {})
        summary_lines.append("### Moving Averages")
        for period in [5, 25, 75, 200]:
            ma_info = ma_data.get(f"{period}_day", {})
            if ma_info:
                summary_lines.append(
                    f"- {period}日MA: {ma_info.get('value', 0):.0f} "
                    f"({ma_info.get('deviation_percent', 0):+.1f}%), "
                    f"トレンド: {ma_info.get('trend', 'unknown')}"
                )

        # Price Action
        qual_data = raw_data.get('qualitative_data', {})
        price_action = qual_data.get('price_action', {})
        summary_lines.append("\n### Recent Price Action")
        summary_lines.append(f"- 勢い: {price_action.get('momentum', 'unknown')}")
        summary_lines.append(f"- ボラティリティ: {price_action.get('volatility_level', 'unknown')}")

        significant_moves = price_action.get('significant_moves', [])
        if significant_moves:
            summary_lines.append("- 直近の大きな動き:")
            for move in significant_moves[-2:]:  # Last 2 moves
                summary_lines.append(
                    f"  - {move['date']}: {move['change_percent']:+.1f}% ({move['type']})"
                )

        # Patterns
        patterns = qual_data.get('patterns', [])
        if patterns:
            summary_lines.append(f"- 検出されたパターン: {', '.join(patterns)}")

        # Market Sentiment
        sentiment = qual_data.get('market_sentiment', {})
        summary_lines.append(f"\n### Market Sentiment")
        summary_lines.append(f"- 出来高トレンド: {sentiment.get('volume_trend', 'unknown')}")

        # Alerts
        alerts = qual_data.get('alerts', [])
        if alerts:
            summary_lines.append(f"\n### Alerts")
            for alert in alerts:
                summary_lines.append(f"- {alert}")

        return "\n".join(summary_lines)

    def _prepare_technical_data_summary(self, raw_data: Dict[str, Any], mode: str) -> str:
        """Prepare a summary of technical data for strategy analysis"""
        summary_lines = []

        price_data = raw_data.get('price_data', {})
        technical = raw_data.get('technical_indicators', {})

        # Current Price
        current = price_data.get('current_price', {})
        summary_lines.append("### Current Price")
        summary_lines.append(f"- 現在値: {current.get('value', 0):.0f}")
        summary_lines.append(f"- 前日比: {current.get('change', 0):+.0f} ({current.get('change_percent', 0):+.1f}%)")
        summary_lines.append(f"- 当日高値: {current.get('high', 0):.0f}")
        summary_lines.append(f"- 当日安値: {current.get('low', 0):.0f}")

        # Technical Indicators
        summary_lines.append("\n### Technical Indicators")
        atr = technical.get('atr', {})
        summary_lines.append(f"- ATR (現在): {atr.get('current', 0):.0f}")
        summary_lines.append(f"- VWAP: {technical.get('vwap', 0):.0f}")

        rsi = technical.get('rsi', {})
        summary_lines.append(f"- RSI: {rsi.get('current', 0):.1f} ({rsi.get('status', 'neutral')})")

        macd = technical.get('macd', {})
        summary_lines.append(f"- MACD: {macd.get('macd', 0):.0f} (シグナル: {macd.get('signal', 0):.0f})")

        bollinger = technical.get('bollinger_bands', {})
        summary_lines.append(f"- ボリンジャーバンド: 上 {bollinger.get('upper', 0):.0f} / 中 {bollinger.get('middle', 0):.0f} / 下 {bollinger.get('lower', 0):.0f}")

        # Support/Resistance
        sentiment = raw_data.get('qualitative_data', {}).get('market_sentiment', {})
        support_resistance = sentiment.get('support_resistance', {})
        if support_resistance:
            summary_lines.append("\n### Key Levels")
            if support_resistance.get('resistance'):
                summary_lines.append("- 抵抗線: " + ", ".join([f"{x:.0f}" for x in support_resistance['resistance']]))
            if support_resistance.get('support'):
                summary_lines.append("- 支持線: " + ", ".join([f"{x:.0f}" for x in support_resistance['support']]))

        return "\n".join(summary_lines)

    def _parse_narrative_analysis(self, analysis_text: str) -> Dict[str, Any]:
        """Parse narrative analysis text into structured format"""
        # Simple parsing - in production, use more sophisticated NLP
        return {
            "trend_analysis": "Extracted trend insights",
            "price_action_analysis": "Extracted price action insights",
            "supply_demand_analysis": "Extracted supply-demand insights",
            "narrative_conclusion": "Extracted conclusion"
        }

    def _parse_strategy_analysis(self, strategy_text: str) -> List[Dict[str, Any]]:
        """Parse strategy analysis text into structured scenarios"""
        # Simple parsing - in production, use more sophisticated NLP
        return [
            {
                "name": "Example Scenario",
                "entry": "Example entry condition",
                "tp": "Example TP",
                "sl": "Example SL",
                "rrr": 1.5,
                "probability": "Medium",
                "time_horizon": "1-2 days"
            }
        ]

    def _fallback_narrative_analysis(self, raw_data: Dict[str, Any], mode: str) -> str:
        """Fallback narrative analysis when API is unavailable"""
        ma_data = raw_data.get('moving_averages', {})
        qual_data = raw_data.get('qualitative_data', {})

        trends = []
        for period in [5, 25, 75, 200]:
            ma_info = ma_data.get(f"{period}_day", {})
            if ma_info:
                trend_jp = {"uptrend": "上昇トレンド", "downtrend": "下降トレンド", "sideways": "横ばい"}.get(ma_info.get('trend', 'sideways'), '不明')
                trends.append(f"{period}日: {trend_jp}")

        momentum = qual_data.get('price_action', {}).get('momentum', 'neutral')

        return f"""**Trend Analysis**: {', '.join(trends)} - 移動平均線の並びを分析中

**Price Action**: 勢いは {momentum} です。直近のプライスアクションを分析中。

**Supply-Demand**: 需給バランスを評価中。ボラティリティと出来高を考慮。

**Narrative Conclusion**: APIキーがないため詳細分析は利用できません。詳細な分析にはANTHROPIC_API_KEYを設定してください。"""

    def _fallback_strategy_analysis(self, raw_data: Dict[str, Any], mode: str) -> str:
        """Fallback strategy analysis when API is unavailable"""
        current_price = raw_data.get('price_data', {}).get('current_price', {}).get('value', 0)
        atr = raw_data.get('technical_indicators', {}).get('atr', {}).get('current', 0)

        return f"""**Scenario 1: 基本シナリオ**
- **Entry**: {current_price:.0f}円付近でのエントリーを検討
- **TP**: {current_price + (atr * 2):.0f}円 (ATRの2倍をターゲット)
- **SL**: {current_price - atr:.0f}円 (ATRに基づく損切り)
- **RRR**: 2.0
- **Probability**: Medium
- **Time Horizon**: {'当日中' if mode == 'daytrade' else '3-5日'}
- **Position Size**: 1-2% of capital

**Overall Strategy Summary**: APIキーがないため詳細な戦略分析は利用できません。詳細な分析にはANTHROPIC_API_KEYを設定してください。"""

    def _calculate_confidence(self, raw_data: Dict[str, Any]) -> str:
        """Calculate overall confidence level in the analysis"""
        # Check data completeness
        price_data = raw_data.get('price_data', {})
        technical = raw_data.get('technical_indicators', {})
        qualitative = raw_data.get('qualitative_data', {})

        completeness = 0
        if price_data.get('current_price'):
            completeness += 0.3
        if technical.get('atr'):
            completeness += 0.3
        if qualitative.get('price_action'):
            completeness += 0.4

        if completeness >= 0.8:
            return "high"
        elif completeness >= 0.5:
            return "medium"
        else:
            return "low"
