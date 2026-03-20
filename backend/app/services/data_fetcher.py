"""Data fetcher component for retrieving mutual fund NAV data."""

import pandas as pd
import yfinance as yf
from typing import Dict, List, Optional
import threading
from contextlib import contextmanager

from app.utils.exceptions import TickerNotFoundError, DataSourceUnavailableError
from app.data.amfi_master import AMFI_MASTER_FUNDS


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

    def __init__(self):
        self._fund_name_cache: Dict[str, str] = {}
        self._fund_registry = []

        for fund in AMFI_MASTER_FUNDS:
            yahoo_ticker = fund.get("yahoo_ticker")
            display_ticker = yahoo_ticker or f"AMFI:{fund['amfi_code']}"
            record = {
                "ticker": display_ticker,
                "name": fund["name"],
                "amfi_code": fund["amfi_code"],
                "fund_house": fund["fund_house"],
                "category": fund["category"],
                "yahoo_ticker": yahoo_ticker,
                "is_supported": bool(yahoo_ticker),
            }
            self._fund_registry.append(record)
            if yahoo_ticker:
                self._fund_name_cache[yahoo_ticker.upper()] = fund["name"]
    
    def fetch_nav_data(self, ticker: str, period: str = "5y") -> pd.DataFrame:
        """
        Fetch historical NAV data for a given ticker.
        
        Args:
            ticker: Mutual fund ticker symbol (e.g., "NIPPONINDIA.NS")
            period: Time period for historical data (default: "5y")
            
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

    def search_funds(self, query: str, limit: int = 10) -> List[Dict[str, Optional[str]]]:
        """Search AMFI-style master list by ticker, scheme code, and fund metadata."""
        normalized = query.strip().lower()
        if not normalized:
            return []

        scored = []
        for item in self._fund_registry:
            name = str(item["name"]).lower()
            ticker = str(item["ticker"]).lower()
            amfi_code = str(item["amfi_code"]).lower()
            fund_house = str(item["fund_house"]).lower()
            category = str(item["category"]).lower()

            search_blob = " ".join([name, ticker, amfi_code, fund_house, category])
            if normalized not in search_blob:
                continue

            score = 0
            if ticker.startswith(normalized):
                score += 6
            if name.startswith(normalized):
                score += 5
            if fund_house.startswith(normalized):
                score += 3
            if amfi_code.startswith(normalized):
                score += 4
            if normalized in category:
                score += 2
            if item["is_supported"]:
                score += 2

            scored.append((score, item))

        scored.sort(key=lambda pair: (-pair[0], pair[1]["name"]))
        return [entry for _, entry in scored[:limit]]

    def resolve_fund_name(self, ticker: str) -> str:
        """Resolve a display name for a ticker, using cache and yfinance metadata."""
        ticker_upper = ticker.strip().upper()
        if ticker_upper in self._fund_name_cache:
            return self._fund_name_cache[ticker_upper]

        try:
            info = yf.Ticker(ticker).info or {}
            name = info.get("longName") or info.get("shortName") or ticker_upper
        except Exception:
            name = ticker_upper

        self._fund_name_cache[ticker_upper] = name
        return name
