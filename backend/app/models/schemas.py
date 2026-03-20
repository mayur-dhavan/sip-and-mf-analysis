"""
Pydantic schemas for API request/response models.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class PredictionRequest(BaseModel):
    """Request model for volatility prediction endpoint."""
    ticker: str = Field(..., description="Mutual fund ticker symbol (e.g., 'NIPPONINDIA.NS')")


class HistoricalNavPoint(BaseModel):
    """Single historical NAV data point."""
    date: str = Field(..., description="Date in ISO format (YYYY-MM-DD)")
    nav: float = Field(..., description="Net Asset Value")


class PredictionResponse(BaseModel):
    """Response model for volatility prediction endpoint."""
    prediction: str = Field(..., description="Prediction result: 'Stable' or 'High_Risk'")
    ticker: str = Field(..., description="Mutual fund ticker symbol used for prediction")
    fund_name: str = Field(..., description="Display name of the mutual fund")
    historical_nav: List[HistoricalNavPoint] = Field(..., description="Last 6 months of NAV data")
    current_rsi: float = Field(..., description="Current Relative Strength Index (0-100)")
    current_volatility: float = Field(..., description="Current 30-day rolling volatility")
    current_nav: float = Field(..., description="Most recent Net Asset Value")
    risk_probability: Optional[float] = Field(None, description="Model probability of High_Risk (0-1)")
    model_confidence: Optional[float] = Field(None, description="Model confidence score (0-1)")
    analysis_summary: Optional[str] = Field(None, description="Human-readable analysis summary")
    current_macd: Optional[float] = Field(None, description="Current MACD value")
    current_macd_signal: Optional[float] = Field(None, description="Current MACD signal line")
    bb_width: Optional[float] = Field(None, description="Current Bollinger Band width")
    daily_return: Optional[float] = Field(None, description="Most recent daily return %")
    sma_20: Optional[float] = Field(None, description="20-day Simple Moving Average")
    sma_50: Optional[float] = Field(None, description="50-day Simple Moving Average")


class FundSearchResult(BaseModel):
    """Mutual fund search result item."""
    ticker: str = Field(..., description="Mutual fund ticker symbol")
    name: str = Field(..., description="Mutual fund display name")
    amfi_code: Optional[str] = Field(None, description="AMFI scheme code")
    fund_house: Optional[str] = Field(None, description="Fund house name")
    category: Optional[str] = Field(None, description="Fund category")
    yahoo_ticker: Optional[str] = Field(None, description="Yahoo Finance ticker when available")
    is_supported: bool = Field(..., description="Whether this fund can be analyzed directly")


class FundSearchResponse(BaseModel):
    """Response model for fund search endpoint."""
    query: str = Field(..., description="Search query")
    results: List[FundSearchResult] = Field(..., description="Matching funds")


class ErrorResponse(BaseModel):
    """Error response model for API errors."""
    code: str = Field(..., description="Error code (e.g., 'TICKER_NOT_FOUND')")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[str] = Field(None, description="Additional error details")
