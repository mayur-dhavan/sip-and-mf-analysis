"""
Basic tests for FeatureCalculator component.
"""
import pytest
import pandas as pd
import numpy as np
from app.services.feature_calculator import FeatureCalculator


def test_feature_calculator_initialization():
    """Test that FeatureCalculator can be instantiated."""
    calculator = FeatureCalculator()
    assert calculator is not None


def test_calculate_rsi_with_sufficient_data():
    """Test RSI calculation with sufficient data points."""
    calculator = FeatureCalculator()
    
    # Create sample NAV data (30 days)
    dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
    nav_values = [100 + i + np.sin(i) * 5 for i in range(30)]
    nav_series = pd.Series(nav_values, index=dates)
    
    rsi = calculator.calculate_rsi(nav_series, period=14)
    
    # Verify RSI properties
    assert isinstance(rsi, pd.Series)
    assert len(rsi) == len(nav_series)
    
    # Check that RSI values are in valid range [0, 100]
    valid_rsi = rsi.dropna()
    assert all(0 <= val <= 100 for val in valid_rsi), "RSI values must be in range [0, 100]"
    
    print(f"✓ RSI calculation successful, range: [{valid_rsi.min():.2f}, {valid_rsi.max():.2f}]")


def test_calculate_sma_with_sufficient_data():
    """Test SMA calculation with sufficient data points."""
    calculator = FeatureCalculator()
    
    # Create sample NAV data (60 days)
    dates = pd.date_range(start='2024-01-01', periods=60, freq='D')
    nav_values = [100 + i * 0.5 for i in range(60)]
    nav_series = pd.Series(nav_values, index=dates)
    
    sma = calculator.calculate_sma(nav_series, period=50)
    
    # Verify SMA properties
    assert isinstance(sma, pd.Series)
    assert len(sma) == len(nav_series)
    
    # Check that SMA values are positive
    valid_sma = sma.dropna()
    assert all(val > 0 for val in valid_sma), "SMA values must be positive"
    
    print(f"✓ SMA calculation successful, range: [{valid_sma.min():.2f}, {valid_sma.max():.2f}]")


def test_calculate_rolling_volatility_with_sufficient_data():
    """Test rolling volatility calculation with sufficient data points."""
    calculator = FeatureCalculator()
    
    # Create sample NAV data (40 days)
    dates = pd.date_range(start='2024-01-01', periods=40, freq='D')
    nav_values = [100 + np.random.randn() * 2 for _ in range(40)]
    nav_series = pd.Series(nav_values, index=dates)
    
    volatility = calculator.calculate_rolling_volatility(nav_series, period=30)
    
    # Verify volatility properties
    assert isinstance(volatility, pd.Series)
    assert len(volatility) == len(nav_series)
    
    # Check that volatility values are non-negative
    valid_volatility = volatility.dropna()
    assert all(val >= 0 for val in valid_volatility), "Volatility values must be non-negative"
    
    print(f"✓ Volatility calculation successful, range: [{valid_volatility.min():.2f}, {valid_volatility.max():.2f}]")


def test_calculate_all_features():
    """Test that calculate_all_features computes all indicators."""
    calculator = FeatureCalculator()
    
    # Create sample NAV DataFrame (60 days for sufficient data)
    dates = pd.date_range(start='2024-01-01', periods=60, freq='D')
    nav_values = [100 + i * 0.5 + np.sin(i) * 3 for i in range(60)]
    nav_df = pd.DataFrame({'Close': nav_values}, index=dates)
    nav_df.index.name = 'Date'
    
    result_df = calculator.calculate_all_features(nav_df)
    
    # Verify all features are present
    assert 'Close' in result_df.columns
    assert 'RSI' in result_df.columns
    assert 'SMA_50' in result_df.columns
    assert 'Rolling_Volatility_30' in result_df.columns
    
    # Verify data integrity
    assert len(result_df) == len(nav_df)
    
    # Check that at least some values are computed (not all NaN)
    assert result_df['RSI'].notna().sum() > 0
    assert result_df['SMA_50'].notna().sum() > 0
    assert result_df['Rolling_Volatility_30'].notna().sum() > 0
    
    print(f"✓ All features calculated successfully")
    print(f"  - RSI: {result_df['RSI'].notna().sum()} valid values")
    print(f"  - SMA_50: {result_df['SMA_50'].notna().sum()} valid values")
    print(f"  - Rolling_Volatility_30: {result_df['Rolling_Volatility_30'].notna().sum()} valid values")


def test_calculate_all_features_with_insufficient_data():
    """Test that calculate_all_features handles insufficient data gracefully."""
    calculator = FeatureCalculator()
    
    # Create sample NAV DataFrame with only 10 days (insufficient for 50-day SMA)
    dates = pd.date_range(start='2024-01-01', periods=10, freq='D')
    nav_values = [100 + i for i in range(10)]
    nav_df = pd.DataFrame({'Close': nav_values}, index=dates)
    nav_df.index.name = 'Date'
    
    result_df = calculator.calculate_all_features(nav_df)
    
    # Verify DataFrame is returned even with insufficient data
    assert isinstance(result_df, pd.DataFrame)
    assert 'RSI' in result_df.columns
    assert 'SMA_50' in result_df.columns
    assert 'Rolling_Volatility_30' in result_df.columns
    
    # SMA_50 should be all NaN with only 10 days of data
    assert result_df['SMA_50'].isna().all()
    
    print(f"✓ Insufficient data handled gracefully")
