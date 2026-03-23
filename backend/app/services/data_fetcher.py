"""Data fetcher component for retrieving mutual fund NAV data."""

import pandas as pd
import yfinance as yf
from typing import Dict, List, Optional
import threading
from contextlib import contextmanager
import re
import requests
from datetime import datetime, timedelta
from pathlib import Path
import joblib
import time

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

    MAX_DYNAMIC_SCHEMES = 2500
    AMFI_UNAVAILABLE_COOLDOWN_MINUTES = 30
    AMFI_FETCH_TIMEOUT_SECONDS = 4
    AMFI_FETCH_MAX_ATTEMPTS = 2
    _LIVE_INDEX_CACHE: Optional[List[Dict[str, str]]] = None
    _LIVE_INDEX_LOADED: bool = False

    def __init__(self):
        self._fund_name_cache: Dict[str, str] = {}
        self._fund_registry = []
        self._amfi_to_name: Dict[str, str] = {}
        self._yahoo_to_amfi: Dict[str, str] = {}
        self._amfi_to_yahoo: Dict[str, str] = {}
        self._verified_supported = self._load_verified_supported_tickers()
        self._runtime_unavailable_amfi: set[str] = set()
        self._runtime_unavailable_until: Dict[str, datetime] = {}

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
                "is_supported": self._is_entry_supported(yahoo_ticker, amfi_code, source="static"),
                "source": "static",
            }
            self._fund_registry.append(record)
            if amfi_supported:
                self._amfi_to_name[amfi_code] = fund["name"]
            if yahoo_ticker:
                self._fund_name_cache[yahoo_ticker.upper()] = fund["name"]
                if amfi_supported:
                    self._yahoo_to_amfi[yahoo_ticker.upper()] = amfi_code
                    self._amfi_to_yahoo[amfi_code] = yahoo_ticker

        self._extend_registry_with_live_amfi_index(limit=self.MAX_DYNAMIC_SCHEMES)

    def _mark_amfi_temporarily_unavailable(self, amfi_code: str) -> None:
        """Mark a scheme as temporarily unavailable to avoid repeated user-facing failures."""
        code = str(amfi_code).strip()
        if not code:
            return
        self._runtime_unavailable_amfi.add(code)
        self._runtime_unavailable_until[code] = datetime.now() + timedelta(
            minutes=self.AMFI_UNAVAILABLE_COOLDOWN_MINUTES
        )

    def _is_amfi_temporarily_unavailable(self, amfi_code: str) -> bool:
        """Return whether a scheme is currently in cooldown for search/prediction support labels."""
        code = str(amfi_code).strip()
        if not code:
            return False

        until = self._runtime_unavailable_until.get(code)
        if until is None:
            return code in self._runtime_unavailable_amfi

        if datetime.now() >= until:
            self._runtime_unavailable_until.pop(code, None)
            self._runtime_unavailable_amfi.discard(code)
            return False

        return True

    def _load_verified_supported_tickers(self) -> set[str]:
        """Load successful training tickers from latest artifact for support labeling."""
        try:
            model_path = Path(__file__).resolve().parents[2] / "models" / "volatility_model.pkl"
            if not model_path.exists():
                return set()
            artifact = joblib.load(model_path)
            successful = artifact.get("successful_tickers", []) if isinstance(artifact, dict) else []
            return {str(item).strip().upper() for item in successful if str(item).strip()}
        except Exception:
            return set()

    def _is_entry_supported(self, yahoo_ticker: Optional[str], amfi_code: str, source: str = "static") -> bool:
        """Decide whether search entry should be flagged analyzable."""
        if amfi_code.isdigit():
            # Any valid AMFI code is potentially analyzable unless runtime checks mark it unavailable.
            return True

        if source == "mfapi_index" and amfi_code.isdigit():
            # Entries from mfapi index are actual known scheme codes.
            return True

        if not self._verified_supported:
            # If artifact is absent, fall back to broad support behavior.
            return bool(yahoo_ticker) or amfi_code.isdigit()

        if yahoo_ticker and str(yahoo_ticker).strip().upper() in self._verified_supported:
            return True
        if amfi_code.isdigit() and f"AMFI:{amfi_code}" in self._verified_supported:
            return True
        return False

    def _extend_registry_with_live_amfi_index(self, limit: int) -> None:
        """Augment registry with live AMFI scheme index from mfapi for broad search coverage."""
        try:
            payload = self._get_live_amfi_index_payload()
            if not payload:
                return

            existing_amfi = {str(item["amfi_code"]).strip() for item in self._fund_registry}
            added = 0

            for row in payload:
                if added >= limit:
                    break

                code = str(row.get("schemeCode", "")).strip()
                name = str(row.get("schemeName", "")).strip()
                if not code.isdigit() or not name or code in existing_amfi:
                    continue

                fund_house = self._guess_fund_house(name)
                category = "Open Ended"

                self._fund_registry.append(
                    {
                        "ticker": f"AMFI:{code}",
                        "name": name,
                        "amfi_code": code,
                        "fund_house": fund_house,
                        "category": category,
                        "yahoo_ticker": None,
                        "is_supported": self._is_entry_supported(None, code, source="mfapi_index"),
                        "source": "mfapi_index",
                    }
                )
                self._amfi_to_name[code] = name
                existing_amfi.add(code)
                added += 1
        except Exception:
            # Non-fatal fallback: keep static registry only.
            return

    @classmethod
    def _get_live_amfi_index_payload(cls) -> List[Dict[str, str]]:
        """Fetch live AMFI scheme index once per process and reuse cache."""
        if cls._LIVE_INDEX_LOADED:
            return cls._LIVE_INDEX_CACHE or []

        try:
            response = requests.get("https://www.amfiindia.com/spages/NAVAll.txt", timeout=20)
            if response.status_code != 200:
                cls._LIVE_INDEX_CACHE = []
            else:
                parsed: List[Dict[str, str]] = []
                for line in response.text.splitlines():
                    parts = [segment.strip() for segment in line.split(";")]
                    if len(parts) < 5:
                        continue
                    scheme_code = parts[0]
                    scheme_name = parts[3]
                    nav_val = parts[4]
                    if not scheme_code.isdigit() or not scheme_name:
                        continue
                    # Keep only entries that currently have a valid NAV value.
                    try:
                        float(nav_val)
                    except Exception:
                        continue

                    parsed.append({
                        "schemeCode": scheme_code,
                        "schemeName": scheme_name,
                    })

                cls._LIVE_INDEX_CACHE = parsed
        except Exception:
            cls._LIVE_INDEX_CACHE = []
        finally:
            cls._LIVE_INDEX_LOADED = True

        return cls._LIVE_INDEX_CACHE or []

    @staticmethod
    def _guess_fund_house(scheme_name: str) -> str:
        """Infer a fund house label from scheme name for search grouping."""
        cleaned = scheme_name.replace("Mutual Fund", "").strip()
        tokens = cleaned.split()
        if not tokens:
            return "Unknown AMC"
        return " ".join(tokens[:2]).strip()
    
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
            if self._is_amfi_temporarily_unavailable(amfi_code):
                raise DataSourceUnavailableError(
                    f"AMFI data temporarily unavailable for scheme code '{amfi_code}'. "
                    "Please retry after some time or select another analyzable fund."
                )
            try:
                return self._fetch_amfi_nav_data(amfi_code, period)
            except (TickerNotFoundError, DataSourceUnavailableError) as amfi_error:
                self._mark_amfi_temporarily_unavailable(amfi_code)

                fallback_yahoo = self._amfi_to_yahoo.get(amfi_code)
                if fallback_yahoo:
                    try:
                        return self.fetch_nav_data(fallback_yahoo, period)
                    except Exception:
                        pass

                raise amfi_error

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
                try:
                    return self._fetch_amfi_nav_data(mapped_amfi, period)
                except TickerNotFoundError:
                    self._mark_amfi_temporarily_unavailable(mapped_amfi)
                    raise
            raise
        except Exception as e:
            # Handle network errors, API failures, etc.
            raise DataSourceUnavailableError(
                f"Failed to fetch data from yfinance: {str(e)}"
            )

    def _fetch_amfi_nav_data(self, amfi_code: str, period: str = "5y") -> pd.DataFrame:
        """Fetch historical NAV data from AMFI-compatible public endpoint by scheme code."""
        max_attempts = self.AMFI_FETCH_MAX_ATTEMPTS
        for attempt in range(1, max_attempts + 1):
            try:
                response = requests.get(
                    f"https://api.mfapi.in/mf/{amfi_code}",
                    timeout=self.AMFI_FETCH_TIMEOUT_SECONDS,
                    headers={"User-Agent": "SIP-MF-Analyzer/1.0"},
                )

                if response.status_code == 404:
                    raise TickerNotFoundError(
                        f"No AMFI data found for scheme code '{amfi_code}'."
                    )

                if response.status_code >= 500:
                    if attempt < max_attempts:
                        time.sleep(0.6 * attempt)
                        continue
                    raise DataSourceUnavailableError(
                        f"AMFI API returned status {response.status_code} for scheme code '{amfi_code}'."
                    )

                if response.status_code != 200:
                    raise DataSourceUnavailableError(
                        f"AMFI API returned status {response.status_code} for scheme code '{amfi_code}'."
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

                nav_df_full = pd.DataFrame(rows, columns=["Date", "Close"]).set_index("Date")
                nav_df_full = nav_df_full.sort_index()
                nav_df = nav_df_full

                cutoff = self._period_to_cutoff(period)
                if cutoff is not None:
                    nav_df = nav_df[nav_df.index >= cutoff]
                    if nav_df.empty and not nav_df_full.empty:
                        # Newer funds may not have full 5y history; use all available data.
                        nav_df = nav_df_full

                if nav_df.empty:
                    raise TickerNotFoundError(
                        f"No AMFI NAV data in requested period '{period}' for scheme code '{amfi_code}'."
                    )

                nav_df.index.name = "Date"
                return nav_df[["Close"]]

            except TickerNotFoundError:
                raise
            except requests.RequestException as e:
                if attempt < max_attempts:
                    time.sleep(0.6 * attempt)
                    continue
                raise DataSourceUnavailableError(f"AMFI data source unavailable: {str(e)}")
            except DataSourceUnavailableError:
                raise
            except Exception as e:
                if attempt < max_attempts:
                    time.sleep(0.6 * attempt)
                    continue
                raise DataSourceUnavailableError(f"Failed to fetch data from AMFI source: {str(e)}")

        raise DataSourceUnavailableError(
            f"Failed to fetch data from AMFI source for scheme code '{amfi_code}'."
        )

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

        normalized_code = normalized
        if normalized.startswith("amfi:"):
            normalized_code = normalized.split(":", 1)[1].strip()

        scored = []
        for item in self._fund_registry:
            name = str(item["name"]).lower()
            ticker = str(item["ticker"]).lower()
            amfi_code = str(item["amfi_code"]).lower()
            fund_house = str(item["fund_house"]).lower()
            category = str(item["category"]).lower()
            amfi_alias = f"amfi:{amfi_code}" if amfi_code else ""

            search_blob = " ".join([name, ticker, amfi_code, amfi_alias, fund_house, category])
            if normalized not in search_blob and normalized_code not in search_blob:
                continue

            score = 0
            if ticker.startswith(normalized):
                score += 6
            if amfi_alias.startswith(normalized):
                score += 6
            if name.startswith(normalized):
                score += 5
            if fund_house.startswith(normalized):
                score += 3
            if amfi_code.startswith(normalized) or amfi_code.startswith(normalized_code):
                score += 4
            if normalized in category:
                score += 2
            item_supported = bool(item["is_supported"]) and not self._is_amfi_temporarily_unavailable(item["amfi_code"])
            if item_supported:
                score += 2

            scored.append((score, item))

        scored.sort(key=lambda pair: (-pair[0], pair[1]["name"]))
        final_results = []
        for _, entry in scored[:limit]:
            item = dict(entry)
            item["is_supported"] = bool(item["is_supported"]) and not self._is_amfi_temporarily_unavailable(item["amfi_code"])
            final_results.append(item)
        return final_results

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
