"""
FastAPI Stock Analysis System - Main Application

This is a comprehensive stock analysis API that combines quantitative data
with qualitative narrative reasoning to provide professional-grade trading analysis.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import asyncio
import logging
from datetime import datetime

# Import local modules
from data_fetcher import DataFetcher
from analyzer import StockAnalyzer
from report_generator import ReportGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Stock Analysis API",
    description="Professional-grade stock analysis combining quantitative data with qualitative reasoning",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
data_fetcher = DataFetcher()
analyzer = StockAnalyzer()
report_generator = ReportGenerator()

# Request models
class AnalysisRequest(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol (e.g., '6871.T' for Japan Micronics)")
    mode: str = Field(default="daytrade", description="Analysis mode: 'daytrade' or 'swing'")
    include_news: bool = Field(default=True, description="Include recent news in analysis")

class AnalysisResponse(BaseModel):
    ticker: str
    mode: str
    raw_data: Dict[str, Any]
    thought_process: Dict[str, Any]
    final_report_markdown: str
    generated_at: str

# Endpoints
@app.get("/")
async def root():
    """API root endpoint with basic information"""
    return {
        "message": "AI Stock Analysis API",
        "version": "1.0.0",
        "endpoints": {
            "analyze": "/api/analyze",
            "health": "/health",
            "docs": "/docs"
        },
        "features": [
            "Quantitative technical analysis (ATR, VWAP, Moving Averages)",
            "Qualitative narrative reasoning (Trend conflicts, Price action patterns)",
            "Monte Carlo simulations for probability scenarios",
            "Professional-grade trading reports with If-Then scenarios"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "data_fetcher": "operational",
            "analyzer": "operational",
            "report_generator": "operational"
        }
    }

@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_stock(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """
    Main analysis endpoint

    This endpoint performs a comprehensive stock analysis including:
    1. Data fetching (prices, technical indicators, news)
    2. LLM reasoning (narrative analysis + quantitative strategy)
    3. Report generation (professional markdown format)

    Args:
        request: AnalysisRequest containing ticker and analysis mode

    Returns:
        AnalysisResponse containing raw data, thought process, and final report
    """
    logger.info(f"Starting analysis for ticker: {request.ticker}, mode: {request.mode}")

    try:
        # Step 1: Data Collection
        logger.info("Step 1: Fetching stock data...")
        raw_data = await data_fetcher.fetch_all_data(
            ticker=request.ticker,
            include_news=request.include_news
        )

        # Step 2: LLM Reasoning Pipeline
        logger.info("Step 2: Running LLM reasoning pipeline...")
        thought_process = await analyzer.analyze_stock(
            ticker=request.ticker,
            raw_data=raw_data,
            mode=request.mode
        )

        # Step 3: Report Generation
        logger.info("Step 3: Generating final report...")
        final_report = report_generator.generate_report(
            ticker=request.ticker,
            raw_data=raw_data,
            thought_process=thought_process,
            mode=request.mode
        )

        # Construct response
        response = AnalysisResponse(
            ticker=request.ticker,
            mode=request.mode,
            raw_data=raw_data,
            thought_process=thought_process,
            final_report_markdown=final_report,
            generated_at=datetime.now().isoformat()
        )

        logger.info(f"Analysis completed successfully for {request.ticker}")
        return response

    except Exception as e:
        logger.error(f"Error during analysis for {request.ticker}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )

@app.get("/api/analyze/{ticker}")
async def analyze_stock_simple(
    ticker: str,
    mode: str = "daytrade",
    include_news: bool = True
):
    """
    Simplified GET endpoint for stock analysis

    Args:
        ticker: Stock ticker symbol
        mode: Analysis mode ('daytrade' or 'swing')
        include_news: Whether to include news analysis

    Returns:
        AnalysisResponse with complete analysis results
    """
    request = AnalysisRequest(
        ticker=ticker,
        mode=mode,
        include_news=include_news
    )
    return await analyze_stock(request, BackgroundTasks())

@app.get("/api/indicators/{ticker}")
async def get_technical_indicators(ticker: str):
    """
    Get technical indicators only (no full analysis)

    Useful for quick reference or integration with other systems
    """
    try:
        indicators = await data_fetcher.get_technical_indicators(ticker)
        return {
            "ticker": ticker,
            "indicators": indicators,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get indicators: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
