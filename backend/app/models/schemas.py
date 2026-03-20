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
    historical_nav: List[HistoricalNavPoint] = Field(..., description="Last 6 months of NAV data")
    current_rsi: float = Field(..., description="Current Relative Strength Index (0-100)")
    current_volatility: float = Field(..., description="Current 30-day rolling volatility")
    current_nav: float = Field(..., description="Most recent Net Asset Value")
    current_macd: Optional[float] = Field(None, description="Current MACD value")
    current_macd_signal: Optional[float] = Field(None, description="Current MACD signal line")
    bb_width: Optional[float] = Field(None, description="Current Bollinger Band width")
    daily_return: Optional[float] = Field(None, description="Most recent daily return %")
    sma_20: Optional[float] = Field(None, description="20-day Simple Moving Average")
    sma_50: Optional[float] = Field(None, description="50-day Simple Moving Average")


class ErrorResponse(BaseModel):
    """Error response model for API errors."""
    code: str = Field(..., description="Error code (e.g., 'TICKER_NOT_FOUND')")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[str] = Field(None, description="Additional error details")
