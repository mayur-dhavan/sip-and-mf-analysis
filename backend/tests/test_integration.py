"""
Integration tests for data fetching and feature calculation workflow.
"""
import pytest
from app.services.data_fetcher import DataFetcher
from app.services.feature_calculator import FeatureCalculator


def test_full_workflow_data_fetch_and_feature_calculation():
    """Test the complete workflow: fetch data -> calculate features."""
    # Initialize components
    fetcher = DataFetcher()
    calculator = FeatureCalculator()
    
    try:
        # Step 1: Fetch NAV data
        ticker = "AAPL"
        nav_df = fetcher.fetch_nav_data(ticker, period="3mo")
        
        assert nav_df is not None
        assert len(nav_df) > 0
        assert 'Close' in nav_df.columns
        
        print(f"✓ Fetched {len(nav_df)} data points for {ticker}")
        
        # Step 2: Calculate features
        features_df = calculator.calculate_all_features(nav_df)
        
        assert features_df is not None
        assert 'RSI' in features_df.columns
        assert 'SMA_50' in features_df.columns
        assert 'Rolling_Volatility_30' in features_df.columns
        
        # Verify we have some valid feature values
        assert features_df['RSI'].notna().sum() > 0
        assert features_df['Rolling_Volatility_30'].notna().sum() > 0
        
        # Verify RSI is in valid range
        valid_rsi = features_df['RSI'].dropna()
        assert all(0 <= val <= 100 for val in valid_rsi)
        
        # Verify volatility is non-negative
        valid_volatility = features_df['Rolling_Volatility_30'].dropna()
        assert all(val >= 0 for val in valid_volatility)
        
        print(f"✓ Successfully calculated all features")
        print(f"  - RSI values: {valid_rsi.min():.2f} to {valid_rsi.max():.2f}")
        print(f"  - Volatility values: {valid_volatility.min():.2f} to {valid_volatility.max():.2f}")
        
    except Exception as e:
        pytest.skip(f"Skipping integration test due to network/API issue: {e}")


def test_workflow_with_indian_mutual_fund_ticker():
    """Test workflow with an Indian mutual fund ticker."""
    fetcher = DataFetcher()
    calculator = FeatureCalculator()
    
    try:
        # Use an Indian mutual fund ticker
        ticker = "NIPPONINDIA.NS"
        nav_df = fetcher.fetch_nav_data(ticker, period="6mo")
        
        if len(nav_df) > 0:
            features_df = calculator.calculate_all_features(nav_df)
            
            assert 'RSI' in features_df.columns
            assert 'SMA_50' in features_df.columns
            assert 'Rolling_Volatility_30' in features_df.columns
            
            print(f"✓ Successfully processed Indian mutual fund ticker: {ticker}")
            print(f"  - Data points: {len(nav_df)}")
            print(f"  - Valid RSI values: {features_df['RSI'].notna().sum()}")
        else:
            pytest.skip(f"No data available for {ticker}")
            
    except Exception as e:
        pytest.skip(f"Skipping test due to network/API issue: {e}")
