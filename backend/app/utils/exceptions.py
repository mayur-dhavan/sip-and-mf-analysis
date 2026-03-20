"""Custom exceptions for the Mutual Fund Volatility Analyzer."""


class TickerNotFoundError(Exception):
    """Raised when a ticker symbol is not found or invalid."""
    pass


class DataSourceUnavailableError(Exception):
    """Raised when the data source (yfinance API) is unavailable."""
    pass
