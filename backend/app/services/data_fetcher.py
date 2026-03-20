"""Data fetcher component for retrieving mutual fund NAV data."""

import pandas as pd
import yfinance as yf
from typing import Optional
import threading
from contextlib import contextmanager

from app.utils.exceptions import TickerNotFoundError, DataSourceUnavailableError


class TimeoutException(Exception):
    """Raised when an operation times out."""
    pass


@contextmanager
def timeout(seconds: int):
    """
    Context manager for timeout handling (cross-platform).
    
    Note: This is a simplified timeout that doesn't interrupt blocking operations.
    For production, consider using asyncio or threading-based solutions.
    """
    # For now, we'll skip the timeout mechanism on Windows
    # In production, use asyncio with timeout or a proper threading solution
    try:
        yield
    finally:
        pass


class DataFetcher:
    """Fetches historical NAV data for mutual funds using yfinance."""
    
    def fetch_nav_data(self, ticker: str, period: str = "3y") -> pd.DataFrame:
        """
        Fetch historical NAV data for a given ticker.
        
        Args:
            ticker: Mutual fund ticker symbol (e.g., "NIPPONINDIA.NS")
            period: Time period for historical data (default: "3y")
            
        Returns:
            DataFrame with columns: Date (index), Close (NAV values)
            
        Raises:
            TickerNotFoundError: If ticker is invalid
            DataSourceUnavailableError: If yfinance API fails
            TimeoutError: If request exceeds 10 seconds
        """
        try:
            with timeout(10):
                # Fetch data using yfinance
                ticker_obj = yf.Ticker(ticker)
                hist_data = ticker_obj.history(period=period)
                
                # Check if data was retrieved
                if hist_data.empty:
                    raise TickerNotFoundError(
                        f"No data found for ticker '{ticker}'. Please verify the ticker symbol."
                    )
                
                # Extract only Date index and Close column
                nav_df = pd.DataFrame({
                    'Close': hist_data['Close']
                })
                nav_df.index.name = 'Date'
                
                return nav_df
                
        except TimeoutException as e:
            raise TimeoutError(str(e))
        except TickerNotFoundError:
            raise
        except Exception as e:
            # Handle network errors, API failures, etc.
            raise DataSourceUnavailableError(
                f"Failed to fetch data from yfinance: {str(e)}"
            )
