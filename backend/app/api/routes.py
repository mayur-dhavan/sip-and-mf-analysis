"""
API routes for volatility prediction endpoint.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
import asyncio
from typing import Dict

from app.models.schemas import PredictionRequest, PredictionResponse, HistoricalNavPoint, ErrorResponse
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
    1. Fetch 3 years NAV data via DataFetcher
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
    1. Fetch 3 years NAV data
    2. Calculate technical indicators
    3. Extract latest feature values
    4. Predict volatility
    5. Format response with last 6 months data
    
    Args:
        ticker: Mutual fund ticker symbol
        
    Returns:
        PredictionResponse with all required fields
    """
    # Step 1: Fetch NAV data (3 years)
    nav_df = await asyncio.to_thread(
        data_fetcher.fetch_nav_data,
        ticker,
        period="3y"
    )
    
    # Step 2: Calculate all technical indicators
    features_df = await asyncio.to_thread(
        feature_calculator.calculate_all_features,
        nav_df
    )
    
    # Step 3: Extract latest values (most recent non-NaN) for all features
    def safe_last(series):
        dropped = series.dropna()
        return float(dropped.iloc[-1]) if len(dropped) > 0 else 0.0
    
    latest_features = {
        'rsi': safe_last(features_df['RSI']),
        'sma_50': safe_last(features_df['SMA_50']),
        'sma_20': safe_last(features_df['SMA_20']),
        'ema_20': safe_last(features_df['EMA_20']),
        'rolling_volatility_30': safe_last(features_df['Rolling_Volatility_30']),
        'rolling_volatility_10': safe_last(features_df['Rolling_Volatility_10']),
        'daily_return': safe_last(features_df['Daily_Return']),
        'roc_10': safe_last(features_df['ROC_10']),
        'macd': safe_last(features_df['MACD']),
        'macd_signal': safe_last(features_df['MACD_Signal']),
        'macd_hist': safe_last(features_df['MACD_Hist']),
        'bb_width': safe_last(features_df['BB_Width']),
        'nav_to_sma50_ratio': safe_last(features_df['NAV_to_SMA50_Ratio']),
        'volatility_ratio': safe_last(features_df['Volatility_Ratio']),
    }
    
    # Step 4: Predict volatility
    prediction_int = await asyncio.to_thread(
        ml_engine.predict_volatility,
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
    
    # Build response
    return PredictionResponse(
        prediction=prediction_str,
        historical_nav=historical_nav,
        current_rsi=float(latest_features['rsi']),
        current_volatility=float(latest_features['rolling_volatility_30']),
        current_nav=current_nav,
        current_macd=float(latest_features['macd']),
        current_macd_signal=float(latest_features['macd_signal']),
        bb_width=float(latest_features['bb_width']),
        daily_return=float(latest_features['daily_return']),
        sma_20=float(latest_features['sma_20']),
        sma_50=float(latest_features['sma_50']),
    )
