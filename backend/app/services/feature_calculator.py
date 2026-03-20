"""
Feature Calculator Service

This module provides technical indicator calculations for mutual fund NAV data.
Implements RSI, SMA, EMA, MACD, Bollinger Bands, and Rolling Volatility calculations.
"""

import pandas as pd
import numpy as np


class FeatureCalculator:
    """
    Calculate technical indicators from NAV data.
    
    Provides methods for computing:
    - RSI (Relative Strength Index)
    - SMA (Simple Moving Average)
    - EMA (Exponential Moving Average)
    - MACD (Moving Average Convergence Divergence)
    - Bollinger Bands
    - Rolling Volatility (Standard Deviation)
    - Daily Returns & Log Returns
    - Rate of Change (ROC)
    """
    
    @staticmethod
    def calculate_rsi(nav_series: pd.Series, period: int = 14) -> pd.Series:
        """
        Calculate 14-day Relative Strength Index.
        
        RSI measures momentum by comparing the magnitude of recent gains
        to recent losses. Values range from 0 to 100.
        
        Args:
            nav_series: Series of NAV values
            period: Number of periods for RSI calculation (default: 14)
            
        Returns:
            Series with RSI values (0-100 range), NaN for initial period
            
        Notes:
            - RSI = 100 - (100 / (1 + RS))
            - RS = Average Gain / Average Loss over period
            - First 'period' values will be NaN
        """
        if len(nav_series) < period + 1:
            return pd.Series([np.nan] * len(nav_series), index=nav_series.index)
        
        # Calculate price changes
        delta = nav_series.diff()
        
        # Separate gains and losses
        gain = delta.where(delta > 0, 0.0)
        loss = -delta.where(delta < 0, 0.0)
        
        # Calculate average gain and loss using exponential moving average
        avg_gain = gain.ewm(com=period - 1, min_periods=period, adjust=False).mean()
        avg_loss = loss.ewm(com=period - 1, min_periods=period, adjust=False).mean()
        
        # Calculate RS and RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        # Handle division by zero (when avg_loss is 0)
        rsi = rsi.fillna(100)
        
        return rsi
    
    @staticmethod
    def calculate_sma(nav_series: pd.Series, period: int = 50) -> pd.Series:
        """
        Calculate 50-day Simple Moving Average.
        
        SMA smooths price data by calculating the average over a rolling window.
        
        Args:
            nav_series: Series of NAV values
            period: Number of periods for SMA calculation (default: 50)
            
        Returns:
            Series with SMA values, NaN for initial period
            
        Notes:
            - First 'period-1' values will be NaN
            - SMA values must be positive for valid NAV data
        """
        if len(nav_series) < period:
            return pd.Series([np.nan] * len(nav_series), index=nav_series.index)
        
        sma = nav_series.rolling(window=period, min_periods=period).mean()
        
        return sma
    
    @staticmethod
    def calculate_rolling_volatility(nav_series: pd.Series, period: int = 30) -> pd.Series:
        """
        Calculate 30-day rolling standard deviation (volatility).
        
        Rolling volatility measures price fluctuation over a moving window.
        Higher values indicate greater price instability.
        
        Args:
            nav_series: Series of NAV values
            period: Number of periods for volatility calculation (default: 30)
            
        Returns:
            Series with rolling volatility values (non-negative), NaN for initial period
            
        Notes:
            - First 'period-1' values will be NaN
            - Volatility is always non-negative (standard deviation)
        """
        if len(nav_series) < period:
            return pd.Series([np.nan] * len(nav_series), index=nav_series.index)
        
        volatility = nav_series.rolling(window=period, min_periods=period).std()
        
        return volatility

    @staticmethod
    def calculate_ema(nav_series: pd.Series, period: int = 20) -> pd.Series:
        """Calculate Exponential Moving Average."""
        if len(nav_series) < period:
            return pd.Series([np.nan] * len(nav_series), index=nav_series.index)
        return nav_series.ewm(span=period, min_periods=period, adjust=False).mean()

    @staticmethod
    def calculate_macd(nav_series: pd.Series) -> tuple:
        """
        Calculate MACD (12-26-9).
        Returns (macd_line, signal_line, histogram).
        """
        if len(nav_series) < 26:
            nan_series = pd.Series([np.nan] * len(nav_series), index=nav_series.index)
            return nan_series, nan_series, nan_series
        
        ema_12 = nav_series.ewm(span=12, min_periods=12, adjust=False).mean()
        ema_26 = nav_series.ewm(span=26, min_periods=26, adjust=False).mean()
        macd_line = ema_12 - ema_26
        signal_line = macd_line.ewm(span=9, min_periods=9, adjust=False).mean()
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram

    @staticmethod
    def calculate_bollinger_bands(nav_series: pd.Series, period: int = 20, num_std: float = 2.0) -> tuple:
        """
        Calculate Bollinger Bands.
        Returns (upper_band, middle_band, lower_band, band_width).
        """
        if len(nav_series) < period:
            nan_series = pd.Series([np.nan] * len(nav_series), index=nav_series.index)
            return nan_series, nan_series, nan_series, nan_series
        
        middle = nav_series.rolling(window=period, min_periods=period).mean()
        std = nav_series.rolling(window=period, min_periods=period).std()
        upper = middle + (std * num_std)
        lower = middle - (std * num_std)
        band_width = (upper - lower) / middle
        return upper, middle, lower, band_width

    @staticmethod
    def calculate_daily_returns(nav_series: pd.Series) -> pd.Series:
        """Calculate daily percentage returns."""
        return nav_series.pct_change()

    @staticmethod
    def calculate_roc(nav_series: pd.Series, period: int = 10) -> pd.Series:
        """Calculate Rate of Change over a period."""
        if len(nav_series) < period:
            return pd.Series([np.nan] * len(nav_series), index=nav_series.index)
        return (nav_series - nav_series.shift(period)) / nav_series.shift(period) * 100
    
    def calculate_all_features(self, nav_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate all technical indicators.
        
        Computes RSI, SMA, and Rolling Volatility for the provided NAV data
        and adds them as new columns to the DataFrame.
        
        Args:
            nav_df: DataFrame with NAV values in 'Close' column and Date index
            
        Returns:
            DataFrame with additional columns:
            - RSI: 14-day Relative Strength Index (0-100)
            - SMA_50: 50-day Simple Moving Average
            - Rolling_Volatility_30: 30-day rolling standard deviation
            
        Notes:
            - Returns NaN for periods with insufficient data
            - RSI range: 0-100
            - SMA and volatility must be non-negative
            - Original DataFrame is not modified (returns a copy)
            
        Requirements: 2.1, 2.2, 2.3
        """
        # Create a copy to avoid modifying the original
        result_df = nav_df.copy()
        
        # Extract NAV series (Close column)
        if 'Close' not in result_df.columns:
            raise ValueError("DataFrame must contain 'Close' column with NAV values")
        
        nav_series = result_df['Close']
        
        # Calculate all indicators
        result_df['RSI'] = self.calculate_rsi(nav_series, period=14)
        result_df['SMA_50'] = self.calculate_sma(nav_series, period=50)
        result_df['SMA_20'] = self.calculate_sma(nav_series, period=20)
        result_df['EMA_20'] = self.calculate_ema(nav_series, period=20)
        result_df['Rolling_Volatility_30'] = self.calculate_rolling_volatility(nav_series, period=30)
        result_df['Rolling_Volatility_10'] = self.calculate_rolling_volatility(nav_series, period=10)
        result_df['Daily_Return'] = self.calculate_daily_returns(nav_series)
        result_df['ROC_10'] = self.calculate_roc(nav_series, period=10)
        
        # MACD
        macd_line, signal_line, histogram = self.calculate_macd(nav_series)
        result_df['MACD'] = macd_line
        result_df['MACD_Signal'] = signal_line
        result_df['MACD_Hist'] = histogram
        
        # Bollinger Bands
        upper, middle, lower, band_width = self.calculate_bollinger_bands(nav_series)
        result_df['BB_Upper'] = upper
        result_df['BB_Lower'] = lower
        result_df['BB_Width'] = band_width
        
        # Derived features
        result_df['NAV_to_SMA50_Ratio'] = nav_series / result_df['SMA_50']
        result_df['Volatility_Ratio'] = result_df['Rolling_Volatility_10'] / result_df['Rolling_Volatility_30']
        
        return result_df
