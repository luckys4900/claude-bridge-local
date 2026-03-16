"""
Test Client for Stock Analysis API

Demonstrates how to use the API from Python
"""

import requests
import json
from typing import Dict, Any

# API configuration
API_BASE_URL = "http://localhost:8000"


class StockAnalysisClient:
    """Simple client for the Stock Analysis API"""

    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url.rstrip('/')

    def analyze_stock(
        self,
        ticker: str,
        mode: str = "daytrade",
        include_news: bool = True
    ) -> Dict[str, Any]:
        """
        Perform comprehensive stock analysis

        Args:
            ticker: Stock ticker symbol (e.g., "6871.T")
            mode: Analysis mode ("daytrade" or "swing")
            include_news: Whether to include news in analysis

        Returns:
            Dictionary containing analysis results
        """
        url = f"{self.base_url}/api/analyze"
        payload = {
            "ticker": ticker,
            "mode": mode,
            "include_news": include_news
        }

        try:
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Error requesting analysis: {e}")
            return {}

    def get_analysis_simple(
        self,
        ticker: str,
        mode: str = "daytrade",
        include_news: bool = True
    ) -> Dict[str, Any]:
        """
        Simple GET request for stock analysis

        Args:
            ticker: Stock ticker symbol
            mode: Analysis mode
            include_news: Whether to include news

        Returns:
            Dictionary containing analysis results
        """
        url = f"{self.base_url}/api/analyze/{ticker}"
        params = {
            "mode": mode,
            "include_news": include_news
        }

        try:
            response = requests.get(url, params=params, timeout=60)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Error requesting analysis: {e}")
            return {}

    def get_technical_indicators(self, ticker: str) -> Dict[str, Any]:
        """
        Get technical indicators only

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dictionary containing technical indicators
        """
        url = f"{self.base_url}/api/indicators/{ticker}"

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Error getting indicators: {e}")
            return {}

    def health_check(self) -> Dict[str, Any]:
        """
        Check API health status

        Returns:
            Dictionary containing health status
        """
        url = f"{self.base_url}/health"

        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Error checking health: {e}")
            return {"status": "error"}


def main():
    """Demonstration of client usage"""
    print("=" * 60)
    print("Stock Analysis API - Test Client")
    print("=" * 60)

    # Initialize client
    client = StockAnalysisClient()

    # Check API health
    print("\n🏥 Checking API health...")
    health = client.health_check()
    print(f"Status: {health.get('status', 'unknown')}")

    if health.get('status') != 'healthy':
        print("❌ API is not healthy. Please start the server first.")
        print("   Run: python run.py")
        return

    # Test 1: Get technical indicators
    print("\n" + "=" * 60)
    print("Test 1: Technical Indicators")
    print("=" * 60)

    ticker = "6871.T"
    print(f"\n📊 Fetching technical indicators for {ticker}...")

    indicators = client.get_technical_indicators(ticker)
    if indicators:
        print("✅ Technical indicators retrieved successfully!")

        # Display key indicators
        if 'indicators' in indicators:
            ind = indicators['indicators']
            print(f"\nKey Indicators:")
            if 'atr' in ind:
                print(f"  ATR: {ind['atr'].get('current', 0):.0f}")
            if 'vwap' in ind:
                print(f"  VWAP: {ind['vwap']:,.0f}")
            if 'rsi' in ind:
                print(f"  RSI: {ind['rsi'].get('current', 0):.1f}")

    # Test 2: Full analysis
    print("\n" + "=" * 60)
    print("Test 2: Comprehensive Analysis")
    print("=" * 60)

    print(f"\n🔍 Performing full analysis for {ticker}...")
    print("   Mode: daytrade")
    print("   (This may take 30-60 seconds...)")

    analysis = client.analyze_stock(
        ticker=ticker,
        mode="daytrade",
        include_news=True
    )

    if analysis:
        print("✅ Analysis completed successfully!")

        # Display summary
        print(f"\n📈 Analysis Summary:")
        print(f"  Ticker: {analysis.get('ticker', 'N/A')}")
        print(f"  Mode: {analysis.get('mode', 'N/A')}")
        print(f"  Generated at: {analysis.get('generated_at', 'N/A')}")

        # Show thought process
        thought_process = analysis.get('thought_process', {})
        print(f"\n🧠 Thought Process Stages:")
        for stage_name in thought_process.keys():
            print(f"  ✓ {stage_name}")

        # Show metadata
        if 'raw_data' in analysis:
            metadata = analysis['raw_data'].get('metadata', {})
            print(f"\n📋 Data Metadata:")
            for key, value in metadata.items():
                if key != 'fetched_at':
                    print(f"  {key}: {value}")

        # Show sample of the report
        if 'final_report_markdown' in analysis:
            report = analysis['final_report_markdown']
            print(f"\n📄 Report Preview (first 500 chars):")
            print("-" * 60)
            print(report[:500] + "...")
            print("-" * 60)

        # Save report to file
        report_filename = f"{ticker.replace('.', '_')}_report.md"
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n💾 Full report saved to: {report_filename}")

        # Save raw JSON data
        json_filename = f"{ticker.replace('.', '_')}_analysis.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
        print(f"💾 JSON data saved to: {json_filename}")

    else:
        print("❌ Analysis failed")

    print("\n" + "=" * 60)
    print("Test Completed")
    print("=" * 60)


if __name__ == "__main__":
    main()
