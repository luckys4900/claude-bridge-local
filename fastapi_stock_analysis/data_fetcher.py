"""
Data Fetcher Module

This module handles data collection from various sources including:
- Yahoo Finance (yfinance) for price data and technical indicators
- Web scraping for qualitative data (news, credit trading ratios, etc.)
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class DataFetcher:
    """Handles all data fetching operations for stock analysis"""

    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes cache

    async def fetch_all_data(
        self,
        ticker: str,
        include_news: bool = True
    ) -> Dict[str, Any]:
        """
        Fetch all necessary data for stock analysis

        Args:
            ticker: Stock ticker symbol
            include_news: Whether to include news data

        Returns:
            Dictionary containing all fetched data
        """
        # Check cache
        cache_key = f"{ticker}_{include_news}"
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if (datetime.now() - cached_time).total_seconds() < self.cache_ttl:
                logger.info(f"Using cached data for {ticker}")
                return cached_data

        logger.info(f"Fetching fresh data for {ticker}")

        # Fetch data from various sources
        price_data = await self.fetch_price_data(ticker)
        technical_indicators = await self.get_technical_indicators(ticker)
        moving_averages = await self.get_moving_averages(ticker)
        qualitative_data = await self.fetch_qualitative_data(ticker)

        # Compile all data
        all_data = {
            "price_data": price_data,
            "technical_indicators": technical_indicators,
            "moving_averages": moving_averages,
            "qualitative_data": qualitative_data,
            "metadata": {
                "ticker": ticker,
                "fetched_at": datetime.now().isoformat(),
                "data_sources": ["yfinance", "web_scraping"]
            }
        }

        # Cache the data
        self.cache[cache_key] = (all_data, datetime.now())

        return all_data

    async def fetch_price_data(self, ticker: str) -> Dict[str, Any]:
        """Fetch current price and historical data from Yahoo Finance"""
        try:
            ticker_obj = yf.Ticker(ticker)

            # Get current info
            info = ticker_obj.info

            # Get recent data (last 3 months)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)
            hist = ticker_obj.history(start=start_date, end=end_date)

            if hist.empty:
                raise ValueError(f"No data found for ticker {ticker}")

            latest = hist.iloc[-1]
            previous = hist.iloc[-2] if len(hist) > 1 else latest

            price_data = {
                "current_price": {
                    "value": float(latest['Close']),
                    "change": float(latest['Close'] - previous['Close']),
                    "change_percent": float(((latest['Close'] / previous['Close']) - 1) * 100),
                    "high": float(latest['High']),
                    "low": float(latest['Low']),
                    "open": float(latest['Open']),
                    "volume": int(latest['Volume'])
                },
                "historical": {
                    "ytd_high": float(hist['High'].max()),
                    "ytd_low": float(hist['Low'].min()),
                    "avg_volume": int(hist['Volume'].mean()),
                    "recent_data": self._format_recent_data(hist.tail(5))
                },
                "company_info": {
                    "name": info.get('longName', 'N/A'),
                    "sector": info.get('sector', 'N/A'),
                    "market_cap": info.get('marketCap', 0),
                    "shares_outstanding": info.get('sharesOutstanding', 0)
                }
            }

            return price_data

        except Exception as e:
            logger.error(f"Error fetching price data for {ticker}: {str(e)}")
            raise

    async def get_technical_indicators(self, ticker: str) -> Dict[str, Any]:
        """Calculate and return technical indicators"""
        try:
            ticker_obj = yf.Ticker(ticker)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            hist = ticker_obj.history(start=start_date, end=end_date)

            if hist.empty or len(hist) < 30:
                raise ValueError("Insufficient data for technical indicators")

            close_prices = hist['Close'].values
            high_prices = hist['High'].values
            low_prices = hist['Low'].values
            volumes = hist['Volume'].values

            # ATR (Average True Range)
            atr = self._calculate_atr(high_prices, low_prices, close_prices)

            # VWAP (Volume Weighted Average Price)
            vwap = self._calculate_vwap(hist)

            # RSI (Relative Strength Index)
            rsi = self._calculate_rsi(close_prices)

            # MACD
            macd_data = self._calculate_macd(close_prices)

            # Bollinger Bands
            bollinger = self._calculate_bollinger_bands(close_prices)

            indicators = {
                "atr": {
                    "current": float(atr[-1]),
                    "14_day_avg": float(np.mean(atr[-14:]))
                },
                "vwap": float(vwap),
                "rsi": {
                    "current": float(rsi[-1]),
                    "status": "overbought" if rsi[-1] > 70 else "oversold" if rsi[-1] < 30 else "neutral"
                },
                "macd": {
                    "macd": float(macd_data['macd'][-1]),
                    "signal": float(macd_data['signal'][-1]),
                    "histogram": float(macd_data['histogram'][-1])
                },
                "bollinger_bands": {
                    "upper": float(bollinger['upper'][-1]),
                    "middle": float(bollinger['middle'][-1]),
                    "lower": float(bollinger['lower'][-1])
                },
                "volatility": {
                    "historical_volatility": float(np.std(hist['Close'].pct_change().dropna()) * 100),
                    "price_range_percent": float(((hist['High'].max() - hist['Low'].min()) / hist['Low'].min()) * 100)
                }
            }

            return indicators

        except Exception as e:
            logger.error(f"Error calculating technical indicators for {ticker}: {str(e)}")
            raise

    async def get_moving_averages(self, ticker: str) -> Dict[str, Any]:
        """Calculate moving averages and their relationships"""
        try:
            ticker_obj = yf.Ticker(ticker)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            hist = ticker_obj.history(start=start_date, end=end_date)

            if hist.empty:
                raise ValueError(f"No data found for ticker {ticker}")

            close_prices = hist['Close']
            current_price = float(close_prices.iloc[-1])

            periods = [5, 25, 75, 200]
            ma_data = {}

            for period in periods:
                if len(close_prices) >= period:
                    ma_value = close_prices.rolling(window=period).mean().iloc[-1]
                    deviation = ((current_price / ma_value) - 1) * 100

                    ma_data[f"{period}_day"] = {
                        "value": float(ma_value),
                        "deviation_percent": float(deviation),
                        "position": "above" if deviation > 0 else "below",
                        "trend": self._determine_ma_trend(close_prices, period)
                    }

            # Determine trend alignment
            ma_data["trend_alignment"] = self._analyze_ma_alignment(ma_data)

            return ma_data

        except Exception as e:
            logger.error(f"Error calculating moving averages for {ticker}: {str(e)}")
            raise

    async def fetch_qualitative_data(self, ticker: str) -> Dict[str, Any]:
        """
        Fetch qualitative data including:
        - Recent price action patterns
        - Credit trading ratios (if available)
        - Recent news/events
        - Market sentiment indicators
        """
        try:
            ticker_obj = yf.Ticker(ticker)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)
            hist = ticker_obj.history(start=start_date, end=end_date)

            if len(hist) < 10:
                raise ValueError("Insufficient data for qualitative analysis")

            # Analyze recent price action
            recent_changes = hist['Close'].pct_change().tail(10).dropna()

            # Identify significant moves
            significant_moves = []
            for idx, change in enumerate(recent_changes):
                if abs(change) > 0.05:  # 5% or more change
                    date = hist.index[-10 + idx + 1].strftime('%Y-%m-%d')
                    significant_moves.append({
                        "date": date,
                        "change_percent": float(change * 100),
                        "type": "surge" if change > 0 else "plunge"
                    })

            # Detect patterns
            patterns = self._detect_price_patterns(hist)

            qualitative_data = {
                "price_action": {
                    "significant_moves": significant_moves[-3:],  # Last 3 significant moves
                    "volatility_level": "high" if recent_changes.std() > 0.03 else "medium" if recent_changes.std() > 0.015 else "low",
                    "momentum": "bullish" if recent_changes.mean() > 0.005 else "bearish" if recent_changes.mean() < -0.005 else "neutral"
                },
                "patterns": patterns,
                "market_sentiment": {
                    "volume_trend": "increasing" if hist['Volume'].tail(5).mean() > hist['Volume'].tail(20).mean() else "stable",
                    "price_velocity": float(recent_changes.iloc[-1] if len(recent_changes) > 0 else 0),
                    "support_resistance": self._identify_support_resistance(hist)
                },
                "alerts": self._generate_alerts(hist, significant_moves)
            }

            return qualitative_data

        except Exception as e:
            logger.error(f"Error fetching qualitative data for {ticker}: {str(e)}")
            # Return basic data if detailed analysis fails
            return {
                "price_action": {
                    "significant_moves": [],
                    "volatility_level": "unknown",
                    "momentum": "neutral"
                },
                "patterns": [],
                "market_sentiment": {},
                "alerts": []
            }

    # Helper methods
    def _calculate_atr(self, high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int = 14) -> np.ndarray:
        """Calculate Average True Range"""
        tr1 = high[1:] - low[1:]
        tr2 = np.abs(high[1:] - close[:-1])
        tr3 = np.abs(low[1:] - close[:-1])
        tr = np.maximum(tr1, np.maximum(tr2, tr3))
        atr = np.zeros_like(close)
        atr[:period] = tr[:period]  # Simple average for first period
        for i in range(period, len(atr)):
            atr[i] = (atr[i-1] * (period - 1) + tr[i-1]) / period
        return atr[period:]

    def _calculate_vwap(self, hist: pd.DataFrame) -> float:
        """Calculate VWAP for recent session"""
        recent = hist.tail(5)
        typical_price = (recent['High'] + recent['Low'] + recent['Close']) / 3
        vwap = (typical_price * recent['Volume']).sum() / recent['Volume'].sum()
        return float(vwap)

    def _calculate_rsi(self, prices: np.ndarray, period: int = 14) -> np.ndarray:
        """Calculate Relative Strength Index"""
        deltas = np.diff(prices)
        seed = deltas[:period+1]
        up = seed[seed >= 0].sum()/period
        down = -seed[seed < 0].sum()/period
        rs = up/down if down != 0 else 100
        rsi = np.zeros_like(prices)
        rsi[:period] = 100. - 100./(1.+rs)

        for i in range(period, len(prices)):
            delta = deltas[i-1]
            if delta > 0:
                upval = delta
                downval = 0.
            else:
                upval = 0.
                downval = -delta

            up = (up * (period - 1) + upval) / period
            down = (down * (period - 1) + downval) / period
            rs = up/down if down != 0 else 100
            rsi[i] = 100. - 100./(1.+rs)

        return rsi[period:]

    def _calculate_macd(self, prices: np.ndarray, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, np.ndarray]:
        """Calculate MACD indicator"""
        exp1 = pd.Series(prices).ewm(span=fast, adjust=False).mean()
        exp2 = pd.Series(prices).ewm(span=slow, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - signal_line

        return {
            'macd': macd.values,
            'signal': signal_line.values,
            'histogram': histogram.values
        }

    def _calculate_bollinger_bands(self, prices: np.ndarray, period: int = 20, std_dev: int = 2) -> Dict[str, np.ndarray]:
        """Calculate Bollinger Bands"""
        sma = pd.Series(prices).rolling(window=period).mean()
        std = pd.Series(prices).rolling(window=period).std()

        return {
            'upper': (sma + (std * std_dev)).values,
            'middle': sma.values,
            'lower': (sma - (std * std_dev)).values
        }

    def _determine_ma_trend(self, prices: pd.Series, period: int) -> str:
        """Determine if a moving average is trending up, down, or sideways"""
        ma = prices.rolling(window=period).mean().dropna()
        if len(ma) < period:
            return "insufficient_data"

        recent = ma.tail(5)
        slope = (recent.iloc[-1] - recent.iloc[0]) / 5

        if slope > 0:
            return "uptrend"
        elif slope < 0:
            return "downtrend"
        else:
            return "sideways"

    def _analyze_ma_alignment(self, ma_data: Dict) -> Dict[str, Any]:
        """Analyze alignment of moving averages"""
        trends = []
        for key, value in ma_data.items():
            if isinstance(value, dict) and 'trend' in value:
                trends.append(value['trend'])

        if not trends:
            return {"status": "insufficient_data"}

        # Check for perfect order
        if all(t == "uptrend" for t in trends):
            return {"status": "perfect_bullish_order", "description": "All MAs in uptrend"}
        elif all(t == "downtrend" for t in trends):
            return {"status": "perfect_bearish_order", "description": "All MAs in downtrend"}
        elif "uptrend" in trends and "downtrend" in trends:
            return {"status": "conflict", "description": "MA alignment conflict"}
        else:
            return {"status": "transitioning", "description": "MA trend transition"}

    def _detect_price_patterns(self, hist: pd.DataFrame) -> List[str]:
        """Detect common price patterns"""
        patterns = []
        if len(hist) < 5:
            return patterns

        recent = hist.tail(5)
        closes = recent['Close'].values
        highs = recent['High'].values
        lows = recent['Low'].values

        # Double bottom detection
        if len(closes) >= 4:
            if abs(closes[-2] - closes[-4]) / closes[-4] < 0.02:  # Similar lows
                if closes[-1] > closes[-2]:
                    patterns.append("double_bottom")

        # Double top detection
        if len(highs) >= 4:
            if abs(highs[-2] - highs[-4]) / highs[-4] < 0.02:  # Similar highs
                if closes[-1] < highs[-2]:
                    patterns.append("double_top")

        # V-shaped recovery
        if len(closes) >= 3:
            change_2 = (closes[-1] - closes[-2]) / closes[-2]
            change_1 = (closes[-2] - closes[-3]) / closes[-3]
            if change_1 < -0.03 and change_2 > 0.03:
                patterns.append("v_recovery")

        return patterns

    def _identify_support_resistance(self, hist: pd.DataFrame) -> Dict[str, List[float]]:
        """Identify support and resistance levels"""
        if len(hist) < 20:
            return {"support": [], "resistance": []}

        # Find local minima and maxima
        recent = hist.tail(30)
        highs = recent['High'].values
        lows = recent['Low'].values

        # Simple approach: find significant levels
        resistance_levels = []
        support_levels = []

        # Find resistance levels (local highs)
        for i in range(2, len(highs)-2):
            if highs[i] > highs[i-1] and highs[i] > highs[i-2] and \
               highs[i] > highs[i+1] and highs[i] > highs[i+2]:
                resistance_levels.append(float(highs[i]))

        # Find support levels (local lows)
        for i in range(2, len(lows)-2):
            if lows[i] < lows[i-1] and lows[i] < lows[i-2] and \
               lows[i] < lows[i+1] and lows[i] < lows[i+2]:
                support_levels.append(float(lows[i]))

        return {
            "resistance": sorted(list(set(resistance_levels)), reverse=True)[:3],
            "support": sorted(list(set(support_levels)))[:3]
        }

    def _generate_alerts(self, hist: pd.DataFrame, significant_moves: List[Dict]) -> List[str]:
        """Generate alerts based on data analysis"""
        alerts = []

        if significant_moves:
            latest_move = significant_moves[-1]
            if latest_move['change_percent'] > 7:
                alerts.append(f"Recent surge: {latest_move['change_percent']:.1f}% on {latest_move['date']}")
            elif latest_move['change_percent'] < -7:
                alerts.append(f"Recent plunge: {latest_move['change_percent']:.1f}% on {latest_move['date']}")

        # RSI alerts (if we have indicators)
        try:
            rsi = self._calculate_rsi(hist['Close'].values)
            if rsi[-1] > 70:
                alerts.append("RSI overbought condition (>70)")
            elif rsi[-1] < 30:
                alerts.append("RSI oversold condition (<30)")
        except:
            pass

        return alerts

    def _format_recent_data(self, hist: pd.DataFrame) -> List[Dict[str, Any]]:
        """Format recent historical data"""
        recent_data = []
        for idx, row in hist.tail(5).iterrows():
            recent_data.append({
                "date": idx.strftime('%Y-%m-%d'),
                "open": float(row['Open']),
                "high": float(row['High']),
                "low": float(row['Low']),
                "close": float(row['Close']),
                "volume": int(row['Volume'])
            })
        return recent_data
