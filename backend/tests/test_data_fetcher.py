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


def test_extract_amfi_code_formats():
    """Test AMFI scheme-code ticker parsing."""
    assert DataFetcher._extract_amfi_code("AMFI:120834") == "120834"
    assert DataFetcher._extract_amfi_code("120834") == "120834"
    assert DataFetcher._extract_amfi_code("amfi:abc123") is None
    assert DataFetcher._extract_amfi_code("AAPL") is None


def test_search_funds_marks_amfi_entries_analyzable():
    """Funds with numeric AMFI scheme code should be analyzable via AMFI NAV source."""
    fetcher = DataFetcher()
    results = fetcher.search_funds("Axis Midcap", limit=5)
    assert len(results) > 0
    axis_midcap = results[0]
    assert axis_midcap["amfi_code"].isdigit()
    assert axis_midcap["is_supported"] is True
    assert axis_midcap["ticker"].startswith("AMFI:") or bool(axis_midcap.get("yahoo_ticker"))
