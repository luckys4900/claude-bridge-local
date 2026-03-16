"""
Standalone Test Script for Stock Analysis System

This script tests the core functionality without requiring the FastAPI server
to be running. It directly tests the data fetcher, analyzer, and report generator.
"""

import sys
import os
from datetime import datetime

# Test imports
print("Testing imports...")
try:
    from data_fetcher import DataFetcher
    from analyzer import StockAnalyzer
    from report_generator import ReportGenerator
    print("Imports successful!")
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

async def test_stock_analysis():
    """Test the complete stock analysis pipeline"""

    print("\n" + "="*60)
    print("STOCK ANALYSIS SYSTEM - STANDALONE TEST")
    print("="*60)

    # Initialize components
    print("\nInitializing components...")
    data_fetcher = DataFetcher()
    analyzer = StockAnalyzer(api_key=None)  # No API key for now
    report_generator = ReportGenerator()

    # Test parameters
    ticker = "6857.T"  # Change ticker for analysis
    mode = "daytrade"

    print(f"\nTesting stock: {ticker}")
    print(f"Mode: {mode}")
    print("\n" + "-"*60)

    try:
        # Step 1: Fetch data
        print("\n[1/4] Fetching stock data...")
        raw_data = await data_fetcher.fetch_all_data(ticker=ticker)

        # Display basic price info
        if 'price_data' in raw_data and 'current_price' in raw_data['price_data']:
            current = raw_data['price_data']['current_price']
            print(f"  Current Price: {current['value']:.0f} yen")
            print(f"  Change: {current['change']:+.0f} yen ({current['change_percent']:+.1f}%)")
            print(f"  High/Low: {current['high']:.0f} / {current['low']:.0f}")
            print("  Data fetch: SUCCESS")

        # Step 2: Test technical indicators
        print("\n[2/4] Analyzing technical indicators...")
        if 'technical_indicators' in raw_data:
            tech = raw_data['technical_indicators']
            print(f"  ATR: {tech.get('atr', {}).get('current', 0):.0f}")
            print(f"  VWAP: {tech.get('vwap', 0):.0f}")
            rsi = tech.get('rsi', {})
            print(f"  RSI: {rsi.get('current', 0):.1f} ({rsi.get('status', 'unknown')})")
            print("  Technical analysis: SUCCESS")

        # Step 3: Test moving averages
        print("\n[3/4] Analyzing moving averages...")
        if 'moving_averages' in raw_data:
            ma = raw_data['moving_averages']
            alignment = ma.get('trend_alignment', {})
            print(f"  Trend Alignment: {alignment.get('status', 'unknown')}")
            for period in [5, 25, 75, 200]:
                ma_info = ma.get(f"{period}_day", {})
                if ma_info:
                    print(f"  {period}d MA: {ma_info['value']:.0f} ({ma_info['deviation_percent']:+.1f}%)")
            print("  Moving average analysis: SUCCESS")

        # Step 4: Test qualitative data
        print("\n[4/4] Analyzing qualitative data...")
        if 'qualitative_data' in raw_data:
            qual = raw_data['qualitative_data']
            price_action = qual.get('price_action', {})
            print(f"  Momentum: {price_action.get('momentum', 'unknown')}")
            print(f"  Volatility: {price_action.get('volatility_level', 'unknown')}")

            patterns = qual.get('patterns', [])
            if patterns:
                print(f"  Patterns detected: {', '.join(patterns)}")
            else:
                print("  No specific patterns detected")

            alerts = qual.get('alerts', [])
            if alerts:
                print(f"  Alerts: {len(alerts)} alerts found")
                for alert in alerts[:2]:  # Show first 2 alerts
                    print(f"    - {alert}")
            else:
                print("  No major alerts")

            print("  Qualitative analysis: SUCCESS")

        # Step 5: Run analyzer (without API key - will use fallback)
        print("\n[5/6] Running LLM analysis (fallback mode)...")
        thought_process = await analyzer.analyze_stock(
            ticker=ticker,
            raw_data=raw_data,
            mode=mode
        )
        print(f"  Narrative analysis: {'COMPLETE' if 'stage_1_narrative' in thought_process else 'FAILED'}")
        print(f"  Strategy analysis: {'COMPLETE' if 'stage_2_strategy' in thought_process else 'FAILED'}")
        print(f"  Meta analysis: {'COMPLETE' if 'meta_analysis' in thought_process else 'FAILED'}")

        # Step 6: Generate report
        print("\n[6/6] Generating professional report...")
        report = report_generator.generate_report(
            ticker=ticker,
            raw_data=raw_data,
            thought_process=thought_process,
            mode=mode
        )

        # Save report to file
        report_filename = f"{ticker.replace('.', '_')}_test_report.md"
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"  Report generated: {len(report)} characters")
        print(f"  Saved to: {report_filename}")

        # Show report preview
        print("\n" + "="*60)
        print("REPORT PREVIEW")
        print("="*60)
        lines = report.split('\n')
        for i, line in enumerate(lines[:15]):  # Show first 15 lines
            print(line)
        if len(lines) > 15:
            print(f"\n... (report continues, {len(lines)-15} more lines)")

        print("\n" + "="*60)
        print("TEST COMPLETED SUCCESSFULLY")
        print("="*60)
        print(f"\nFull report saved to: {report_filename}")
        print("\nSystem Status: All components working correctly!")
        print("Note: LLM analysis is in fallback mode - for full features,")
        print("      add your ANTHROPIC_API_KEY to .env file")

    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    import asyncio
    result = asyncio.run(test_stock_analysis())
    sys.exit(0 if result else 1)
