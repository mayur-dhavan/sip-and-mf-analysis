"""
API routes for volatility prediction endpoint.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
import asyncio
from typing import Dict

from app.models.schemas import (
    PredictionRequest,
    PredictionResponse,
    HistoricalNavPoint,
    FundSearchResponse,
)
from app.services.data_fetcher import DataFetcher
from app.services.feature_calculator import FeatureCalculator
from app.services.ml_engine import MLEngine, ModelNotFoundError, PredictionError
from app.utils.exceptions import TickerNotFoundError, DataSourceUnavailableError


router = APIRouter()

# Initialize service components
data_fetcher = DataFetcher()
feature_calculator = FeatureCalculator()
ml_engine = MLEngine()


@router.post("/api/predict-volatility/", response_model=PredictionResponse)
async def predict_volatility(request: PredictionRequest):
    """
    Predict mutual fund volatility risk.
    
    Process:
    1. Fetch 5 years NAV data via DataFetcher
    2. Calculate technical indicators via FeatureCalculator
    3. Extract latest values for prediction
    4. Load ML model and predict
    5. Format response with last 6 months data
    
    Timeout: 15 seconds total
    
    Args:
        request: PredictionRequest with ticker symbol
        
    Returns:
        PredictionResponse with prediction, historical data, and metrics
        
    Raises:
        HTTPException: 404 for ticker not found, 503 for data source unavailable,
                      504 for timeout, 500 for internal errors
                      
    Requirements: 5.1, 5.2, 5.3, 5.5, 4.4, 4.5
    """
    try:
        # Wrap entire process in 15-second timeout
        result = await asyncio.wait_for(
            _process_prediction(request.ticker),
            timeout=15.0
        )
        return result
        
    except asyncio.TimeoutError:
        # Handle timeout → 504
        raise HTTPException(
            status_code=504,
            detail={
                "code": "TIMEOUT",
                "message": "Request processing exceeded 15 seconds timeout limit.",
                "details": None
            }
        )
    except TickerNotFoundError as e:
        # Handle TickerNotFoundError → 404
        raise HTTPException(
            status_code=404,
            detail={
                "code": "TICKER_NOT_FOUND",
                "message": str(e),
                "details": None
            }
        )
    except DataSourceUnavailableError as e:
        # Handle DataSourceUnavailableError → 503
        raise HTTPException(
            status_code=503,
            detail={
                "code": "DATA_SOURCE_UNAVAILABLE",
                "message": str(e),
                "details": None
            }
        )
    except (ModelNotFoundError, PredictionError) as e:
        # Handle ML model errors → 500
        raise HTTPException(
            status_code=500,
            detail={
                "code": "MODEL_ERROR",
                "message": f"ML model error: {str(e)}",
                "details": None
            }
        )
    except Exception as e:
        # Handle general exceptions → 500
        raise HTTPException(
            status_code=500,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred during processing.",
                "details": str(e)
            }
        )


async def _process_prediction(ticker: str) -> PredictionResponse:
    """
    Internal async function to orchestrate prediction workflow.
    
    Steps:
    1. Fetch 5 years NAV data
    2. Calculate technical indicators
    3. Extract latest feature values
    4. Predict volatility
    5. Format response with last 6 months data
    
    Args:
        ticker: Mutual fund ticker symbol
        
    Returns:
        PredictionResponse with all required fields
    """
    # Step 1: Fetch NAV data (5 years)
    nav_df = await asyncio.to_thread(
        data_fetcher.fetch_nav_data,
        ticker,
        period="5y"
    )

    fund_name = await asyncio.to_thread(data_fetcher.resolve_fund_name, ticker)
    fund_name = str(fund_name).strip() if fund_name is not None else ticker
    if not fund_name:
        fund_name = ticker
    
    # Step 2: Calculate all technical indicators
    features_df = await asyncio.to_thread(
        feature_calculator.calculate_all_features,
        nav_df
    )
    
    # Step 3: Extract latest complete feature row to avoid mixed-date signal leakage.
    required_feature_cols = [
        'RSI',
        'SMA_50',
        'SMA_20',
        'EMA_20',
        'Rolling_Volatility_30',
        'Rolling_Volatility_10',
        'Daily_Return',
        'ROC_10',
        'MACD',
        'MACD_Signal',
        'MACD_Hist',
        'BB_Width',
        'NAV_to_SMA50_Ratio',
        'Volatility_Ratio',
        'Return_5',
        'Return_20',
        'Sharpe_30',
        'ZScore_20',
        'Drawdown_60',
    ]
    available_feature_cols = [col for col in required_feature_cols if col in features_df.columns]
    if not available_feature_cols:
        raise PredictionError("No feature columns available for prediction")

    complete_rows = features_df.dropna(subset=available_feature_cols)
    if complete_rows.empty:
        # Fallback for sparse feeds: use latest row and default missing/NaN fields to 0.
        latest = features_df.iloc[-1]
    else:
        latest = complete_rows.iloc[-1]

    def latest_value(column_name: str) -> float:
        value = latest.get(column_name, 0.0)
        if value is None:
            return 0.0
        try:
            numeric = float(value)
            return numeric if numeric == numeric else 0.0
        except Exception:
            return 0.0

    latest_features = {
        'rsi': latest_value('RSI'),
        'sma_50': latest_value('SMA_50'),
        'sma_20': latest_value('SMA_20'),
        'ema_20': latest_value('EMA_20'),
        'rolling_volatility_30': latest_value('Rolling_Volatility_30'),
        'rolling_volatility_10': latest_value('Rolling_Volatility_10'),
        'daily_return': latest_value('Daily_Return'),
        'roc_10': latest_value('ROC_10'),
        'macd': latest_value('MACD'),
        'macd_signal': latest_value('MACD_Signal'),
        'macd_hist': latest_value('MACD_Hist'),
        'bb_width': latest_value('BB_Width'),
        'nav_to_sma50_ratio': latest_value('NAV_to_SMA50_Ratio'),
        'volatility_ratio': latest_value('Volatility_Ratio'),
        'return_5': latest_value('Return_5'),
        'return_20': latest_value('Return_20'),
        'sharpe_30': latest_value('Sharpe_30'),
        'zscore_20': latest_value('ZScore_20'),
        'drawdown_60': latest_value('Drawdown_60'),
    }
    
    # Step 4: Predict volatility
    prediction_int, risk_probability, model_confidence = await asyncio.to_thread(
        ml_engine.predict_with_confidence,
        latest_features
    )
    
    # Map prediction: 0→"Stable", 1→"High_Risk"
    prediction_str = "High_Risk" if prediction_int == 1 else "Stable"
    
    # Step 5: Filter historical_nav to last 6 months
    six_months_ago = datetime.now() - timedelta(days=180)
    # Make index tz-naive to avoid comparison errors with tz-aware yfinance data
    if nav_df.index.tz is not None:
        nav_df.index = nav_df.index.tz_localize(None)
    recent_data = nav_df[nav_df.index >= six_months_ago]
    
    # Format historical NAV data
    historical_nav = [
        HistoricalNavPoint(
            date=date.strftime("%Y-%m-%d"),
            nav=float(row['Close'])
        )
        for date, row in recent_data.iterrows()
    ]
    
    # Get current NAV (most recent value)
    current_nav = float(nav_df['Close'].iloc[-1])

    analysis_summary = _build_analysis_summary(
        prediction=prediction_str,
        confidence=model_confidence,
        risk_probability=risk_probability,
        current_rsi=float(latest_features['rsi']),
        current_nav=current_nav,
        sma_20=float(latest_features['sma_20']),
        sma_50=float(latest_features['sma_50']),
        current_volatility=float(latest_features['rolling_volatility_30']),
    )
    
    # Build response
    return PredictionResponse(
        prediction=prediction_str,
        ticker=ticker,
        fund_name=fund_name,
        historical_nav=historical_nav,
        current_rsi=float(latest_features['rsi']),
        current_volatility=float(latest_features['rolling_volatility_30']),
        current_nav=current_nav,
        risk_probability=float(risk_probability),
        model_confidence=float(model_confidence),
        analysis_summary=analysis_summary,
        current_macd=float(latest_features['macd']),
        current_macd_signal=float(latest_features['macd_signal']),
        bb_width=float(latest_features['bb_width']),
        daily_return=float(latest_features['daily_return']),
        sma_20=float(latest_features['sma_20']),
        sma_50=float(latest_features['sma_50']),
    )


@router.get("/api/search-funds/", response_model=FundSearchResponse)
async def search_funds(query: str, limit: int = 10):
    """Search mutual fund tickers by name or symbol for autocomplete UX."""
    query_clean = query.strip()
    if len(query_clean) < 2:
        return FundSearchResponse(query=query_clean, results=[])

    safe_limit = max(1, min(limit, 25))
    results = await asyncio.to_thread(data_fetcher.search_funds, query_clean, safe_limit)
    return FundSearchResponse(query=query_clean, results=results)


def _build_analysis_summary(
    prediction: str,
    confidence: float,
    risk_probability: float,
    current_rsi: float,
    current_nav: float,
    sma_20: float,
    sma_50: float,
    current_volatility: float,
) -> str:
    """Generate compact human-readable interpretation of the model output."""
    signals = []

    if current_rsi >= 70:
        signals.append("RSI indicates overbought momentum")
    elif current_rsi <= 30:
        signals.append("RSI indicates oversold conditions")
    else:
        signals.append("RSI is in neutral range")

    if sma_20 > sma_50 and current_nav >= sma_20:
        signals.append("short-term trend is bullish")
    elif sma_20 < sma_50 and current_nav < sma_20:
        signals.append("short-term trend is bearish")
    else:
        signals.append("trend signals are mixed")

    nav_volatility_ratio = (current_volatility / current_nav) if current_nav else 0.0
    if nav_volatility_ratio > 0.035:
        signals.append("recent price swings are elevated")
    elif nav_volatility_ratio < 0.015:
        signals.append("recent price action is relatively stable")
    else:
        signals.append("volatility is moderate")

    confidence_pct = confidence * 100
    risk_pct = risk_probability * 100
    return (
        f"Model predicts {prediction.replace('_', ' ')} with {confidence_pct:.1f}% confidence "
        f"(High Risk probability {risk_pct:.1f}%). "
        + "; ".join(signals)
        + "."
    )
