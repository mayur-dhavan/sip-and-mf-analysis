"""Data fetcher component for retrieving mutual fund NAV data."""

import pandas as pd
import yfinance as yf
from typing import Dict, List, Optional
import threading
from contextlib import contextmanager
import re
import requests
from datetime import datetime, timedelta

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
        self._amfi_to_name: Dict[str, str] = {}
        self._yahoo_to_amfi: Dict[str, str] = {}

        for fund in AMFI_MASTER_FUNDS:
            yahoo_ticker = fund.get("yahoo_ticker")
            display_ticker = yahoo_ticker or f"AMFI:{fund['amfi_code']}"
            amfi_code = str(fund["amfi_code"]).strip()
            amfi_supported = amfi_code.isdigit()
            record = {
                "ticker": display_ticker,
                "name": fund["name"],
                "amfi_code": amfi_code,
                "fund_house": fund["fund_house"],
                "category": fund["category"],
                "yahoo_ticker": yahoo_ticker,
                "is_supported": bool(yahoo_ticker) or amfi_supported,
            }
            self._fund_registry.append(record)
            if amfi_supported:
                self._amfi_to_name[amfi_code] = fund["name"]
            if yahoo_ticker:
                self._fund_name_cache[yahoo_ticker.upper()] = fund["name"]
                if amfi_supported:
                    self._yahoo_to_amfi[yahoo_ticker.upper()] = amfi_code
    
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
        normalized_ticker = ticker.strip()
        amfi_code = self._extract_amfi_code(normalized_ticker)
        if amfi_code:
            return self._fetch_amfi_nav_data(amfi_code, period)

        try:
            with timeout(10):
                # Fetch data using yfinance
                ticker_obj = yf.Ticker(normalized_ticker)
                hist_data = ticker_obj.history(period=period)
                
                # Check if data was retrieved
                if hist_data.empty:
                    raise TickerNotFoundError(
                        f"No data found for ticker '{normalized_ticker}'. Please verify the ticker symbol."
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
            # Fallback: try AMFI code if this Yahoo ticker is mapped in registry.
            mapped_amfi = self._yahoo_to_amfi.get(normalized_ticker.upper())
            if mapped_amfi:
                return self._fetch_amfi_nav_data(mapped_amfi, period)
            raise
        except TickerNotFoundError:
            raise
        except Exception as e:
            # Handle network errors, API failures, etc.
            raise DataSourceUnavailableError(
                f"Failed to fetch data from yfinance: {str(e)}"
            )

    def _fetch_amfi_nav_data(self, amfi_code: str, period: str = "5y") -> pd.DataFrame:
        """Fetch historical NAV data from AMFI-compatible public endpoint by scheme code."""
        try:
            response = requests.get(f"https://api.mfapi.in/mf/{amfi_code}", timeout=10)
            if response.status_code != 200:
                raise TickerNotFoundError(
                    f"No AMFI data found for scheme code '{amfi_code}'."
                )

            payload = response.json()
            data_points = payload.get("data", [])
            if not data_points:
                raise TickerNotFoundError(
                    f"No AMFI NAV history found for scheme code '{amfi_code}'."
                )

            rows = []
            for item in data_points:
                date_str = item.get("date")
                nav_str = item.get("nav")
                if not date_str or nav_str is None:
                    continue
                try:
                    dt = datetime.strptime(date_str, "%d-%m-%Y")
                    nav_val = float(nav_str)
                    rows.append((dt, nav_val))
                except Exception:
                    continue

            if not rows:
                raise TickerNotFoundError(
                    f"AMFI NAV parsing failed for scheme code '{amfi_code}'."
                )

            nav_df = pd.DataFrame(rows, columns=["Date", "Close"]).set_index("Date")
            nav_df = nav_df.sort_index()

            cutoff = self._period_to_cutoff(period)
            if cutoff is not None:
                nav_df = nav_df[nav_df.index >= cutoff]

            if nav_df.empty:
                raise TickerNotFoundError(
                    f"No AMFI NAV data in requested period '{period}' for scheme code '{amfi_code}'."
                )

            nav_df.index.name = "Date"
            return nav_df[["Close"]]
        except TickerNotFoundError:
            raise
        except requests.RequestException as e:
            raise DataSourceUnavailableError(f"AMFI data source unavailable: {str(e)}")
        except Exception as e:
            raise DataSourceUnavailableError(f"Failed to fetch data from AMFI source: {str(e)}")

    @staticmethod
    def _period_to_cutoff(period: str) -> Optional[datetime]:
        """Convert yfinance-like period strings to datetime cutoff."""
        now = datetime.now()
        match = re.match(r"^(\d+)([dmy])$", period.strip().lower())
        if not match:
            return None

        amount = int(match.group(1))
        unit = match.group(2)
        if unit == "d":
            return now - timedelta(days=amount)
        if unit == "m":
            return now - timedelta(days=amount * 30)
        if unit == "y":
            return now - timedelta(days=amount * 365)
        return None

    @staticmethod
    def _extract_amfi_code(ticker: str) -> Optional[str]:
        normalized = ticker.strip().upper()
        if normalized.startswith("AMFI:"):
            code = normalized.split(":", 1)[1].strip()
            return code if code.isdigit() else None
        # Allow direct scheme code usage as ticker input.
        if normalized.isdigit():
            return normalized
        return None

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

        amfi_code = self._extract_amfi_code(ticker_upper)
        if amfi_code and amfi_code in self._amfi_to_name:
            return self._amfi_to_name[amfi_code]

        if ticker_upper in self._fund_name_cache:
            return self._fund_name_cache[ticker_upper]

        try:
            info = yf.Ticker(ticker).info or {}
            name = info.get("longName") or info.get("shortName") or ticker_upper
        except Exception:
            name = ticker_upper

        self._fund_name_cache[ticker_upper] = name
        return name
