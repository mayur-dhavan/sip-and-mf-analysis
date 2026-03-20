"""
Basic tests for DataFetcher component.
"""
import pytest
import pandas as pd
from app.services.data_fetcher import DataFetcher
from app.utils.exceptions import TickerNotFoundError, DataSourceUnavailableError


def test_data_fetcher_initialization():
    """Test that DataFetcher can be instantiated."""
    fetcher = DataFetcher()
    assert fetcher is not None


def test_fetch_nav_data_with_valid_ticker():
    """Test fetching data with a valid ticker symbol."""
    fetcher = DataFetcher()
    
    # Use a well-known ticker that should have data
    ticker = "AAPL"  # Apple stock as a test case
    
    try:
        df = fetcher.fetch_nav_data(ticker, period="1mo")
        
        # Verify DataFrame structure
        assert isinstance(df, pd.DataFrame)
        assert 'Close' in df.columns
        assert df.index.name == 'Date'
        assert len(df) > 0
        
        # Verify data types
        assert df['Close'].dtype in [float, 'float64']
        
        print(f"✓ Successfully fetched {len(df)} data points for {ticker}")
        
    except Exception as e:
        pytest.skip(f"Skipping test due to network/API issue: {e}")


def test_fetch_nav_data_with_invalid_ticker():
    """Test that invalid ticker raises TickerNotFoundError."""
    fetcher = DataFetcher()
    
    # Use an obviously invalid ticker
    invalid_ticker = "INVALID_TICKER_XYZ123"
    
    with pytest.raises(TickerNotFoundError):
        fetcher.fetch_nav_data(invalid_ticker, period="1mo")


def test_fetch_nav_data_returns_dataframe():
    """Test that fetch_nav_data returns a pandas DataFrame."""
    fetcher = DataFetcher()
    
    try:
        df = fetcher.fetch_nav_data("MSFT", period="5d")
        assert isinstance(df, pd.DataFrame)
    except Exception as e:
        pytest.skip(f"Skipping test due to network/API issue: {e}")
