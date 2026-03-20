"""
Unit tests for API routes.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from datetime import datetime, timedelta

from app.main import app
from app.utils.exceptions import TickerNotFoundError, DataSourceUnavailableError
from app.services.ml_engine import ModelNotFoundError, PredictionError


client = TestClient(app)


@pytest.fixture
def mock_nav_data():
    """Create mock NAV data for testing."""
    dates = pd.date_range(end=datetime.now(), periods=750, freq='D')
    nav_values = [100 + i * 0.1 for i in range(750)]
    df = pd.DataFrame({'Close': nav_values}, index=dates)
    df.index.name = 'Date'
    return df


@pytest.fixture
def mock_features_data(mock_nav_data):
    """Create mock features data for testing."""
    df = mock_nav_data.copy()
    df['RSI'] = 55.0
    df['SMA_50'] = 105.0
    df['Rolling_Volatility_30'] = 2.5
    return df


class TestPredictVolatilityEndpoint:
    """Test suite for /api/predict-volatility/ endpoint."""
    
    @patch('app.api.routes.data_fetcher')
    def test_endpoint_exists(self, mock_df):
        """Test that the endpoint exists and accepts POST requests."""
        # Setup mock to avoid hitting real API
        mock_df.fetch_nav_data.side_effect = TickerNotFoundError("Test error")
        
        response = client.post("/api/predict-volatility/", json={"ticker": "TEST.NS"})
        # Should not return 405 (method not allowed) - endpoint exists
        assert response.status_code != 405
        # Will return 404 due to mocked error, which is fine - endpoint exists
        assert response.status_code in [404, 500, 503]  # Valid error codes
    
    @patch('app.api.routes.data_fetcher')
    @patch('app.api.routes.feature_calculator')
    @patch('app.api.routes.ml_engine')
    def test_successful_prediction_stable(self, mock_ml, mock_fc, mock_df, mock_nav_data, mock_features_data):
        """Test successful prediction with Stable result."""
        # Setup mocks
        mock_df.fetch_nav_data.return_value = mock_nav_data
        mock_fc.calculate_all_features.return_value = mock_features_data
        mock_ml.predict_with_confidence.return_value = (0, 0.35, 0.65)  # Stable
        
        # Make request
        response = client.post("/api/predict-volatility/", json={"ticker": "NIPPONINDIA.NS"})
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data['prediction'] == 'Stable'
        assert 'historical_nav' in data
        assert 'current_rsi' in data
        assert 'current_volatility' in data
        assert 'current_nav' in data
        assert isinstance(data['historical_nav'], list)
        assert len(data['historical_nav']) > 0
    
    @patch('app.api.routes.data_fetcher')
    @patch('app.api.routes.feature_calculator')
    @patch('app.api.routes.ml_engine')
    def test_successful_prediction_high_risk(self, mock_ml, mock_fc, mock_df, mock_nav_data, mock_features_data):
        """Test successful prediction with High_Risk result."""
        # Setup mocks
        mock_df.fetch_nav_data.return_value = mock_nav_data
        mock_fc.calculate_all_features.return_value = mock_features_data
        mock_ml.predict_with_confidence.return_value = (1, 0.82, 0.82)  # High_Risk
        
        # Make request
        response = client.post("/api/predict-volatility/", json={"ticker": "NIPPONINDIA.NS"})
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data['prediction'] == 'High_Risk'
    
    @patch('app.api.routes.data_fetcher')
    def test_ticker_not_found_error(self, mock_df):
        """Test handling of TickerNotFoundError → 404."""
        # Setup mock to raise TickerNotFoundError
        mock_df.fetch_nav_data.side_effect = TickerNotFoundError("Ticker 'INVALID.NS' not found")
        
        # Make request
        response = client.post("/api/predict-volatility/", json={"ticker": "INVALID.NS"})
        
        # Verify response
        assert response.status_code == 404
        data = response.json()
        assert 'detail' in data
        assert data['detail']['code'] == 'TICKER_NOT_FOUND'
    
    @patch('app.api.routes.data_fetcher')
    def test_data_source_unavailable_error(self, mock_df):
        """Test handling of DataSourceUnavailableError → 503."""
        # Setup mock to raise DataSourceUnavailableError
        mock_df.fetch_nav_data.side_effect = DataSourceUnavailableError("yfinance API unavailable")
        
        # Make request
        response = client.post("/api/predict-volatility/", json={"ticker": "TEST.NS"})
        
        # Verify response
        assert response.status_code == 503
        data = response.json()
        assert 'detail' in data
        assert data['detail']['code'] == 'DATA_SOURCE_UNAVAILABLE'
    
    @patch('app.api.routes.data_fetcher')
    @patch('app.api.routes.feature_calculator')
    @patch('app.api.routes.ml_engine')
    def test_model_not_found_error(self, mock_ml, mock_fc, mock_df, mock_nav_data, mock_features_data):
        """Test handling of ModelNotFoundError → 500."""
        # Setup mocks
        mock_df.fetch_nav_data.return_value = mock_nav_data
        mock_fc.calculate_all_features.return_value = mock_features_data
        mock_ml.predict_with_confidence.side_effect = ModelNotFoundError("Model file not found")
        
        # Make request
        response = client.post("/api/predict-volatility/", json={"ticker": "TEST.NS"})
        
        # Verify response
        assert response.status_code == 500
        data = response.json()
        assert 'detail' in data
        assert data['detail']['code'] == 'MODEL_ERROR'
    
    @patch('app.api.routes.data_fetcher')
    @patch('app.api.routes.feature_calculator')
    @patch('app.api.routes.ml_engine')
    def test_prediction_error(self, mock_ml, mock_fc, mock_df, mock_nav_data, mock_features_data):
        """Test handling of PredictionError → 500."""
        # Setup mocks
        mock_df.fetch_nav_data.return_value = mock_nav_data
        mock_fc.calculate_all_features.return_value = mock_features_data
        mock_ml.predict_with_confidence.side_effect = PredictionError("Prediction failed")
        
        # Make request
        response = client.post("/api/predict-volatility/", json={"ticker": "TEST.NS"})
        
        # Verify response
        assert response.status_code == 500
        data = response.json()
        assert 'detail' in data
        assert data['detail']['code'] == 'MODEL_ERROR'
    
    @patch('app.api.routes.data_fetcher')
    def test_general_exception_handling(self, mock_df):
        """Test handling of general exceptions → 500."""
        # Setup mock to raise unexpected exception
        mock_df.fetch_nav_data.side_effect = ValueError("Unexpected error")
        
        # Make request
        response = client.post("/api/predict-volatility/", json={"ticker": "TEST.NS"})
        
        # Verify response
        assert response.status_code == 500
        data = response.json()
        assert 'detail' in data
        assert data['detail']['code'] == 'INTERNAL_ERROR'
    
    @patch('app.api.routes.data_fetcher')
    @patch('app.api.routes.feature_calculator')
    @patch('app.api.routes.ml_engine')
    def test_historical_nav_filtered_to_6_months(self, mock_ml, mock_fc, mock_df, mock_nav_data, mock_features_data):
        """Test that historical_nav is filtered to last 6 months."""
        # Setup mocks
        mock_df.fetch_nav_data.return_value = mock_nav_data
        mock_fc.calculate_all_features.return_value = mock_features_data
        mock_ml.predict_with_confidence.return_value = (0, 0.40, 0.60)
        
        # Make request
        response = client.post("/api/predict-volatility/", json={"ticker": "TEST.NS"})
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Check that historical_nav contains approximately 6 months of data
        # (approximately 180 days, but may vary due to weekends/holidays)
        assert len(data['historical_nav']) <= 200  # Max ~6.5 months
        assert len(data['historical_nav']) >= 120  # Min ~4 months (accounting for weekends)
        
        # Verify date format
        first_date = datetime.strptime(data['historical_nav'][0]['date'], '%Y-%m-%d')
        last_date = datetime.strptime(data['historical_nav'][-1]['date'], '%Y-%m-%d')
        assert (last_date - first_date).days <= 200
    
    @patch('app.api.routes.data_fetcher')
    @patch('app.api.routes.feature_calculator')
    @patch('app.api.routes.ml_engine')
    def test_response_structure(self, mock_ml, mock_fc, mock_df, mock_nav_data, mock_features_data):
        """Test that response contains all required fields."""
        # Setup mocks
        mock_df.fetch_nav_data.return_value = mock_nav_data
        mock_fc.calculate_all_features.return_value = mock_features_data
        mock_ml.predict_with_confidence.return_value = (0, 0.40, 0.60)
        
        # Make request
        response = client.post("/api/predict-volatility/", json={"ticker": "TEST.NS"})
        
        # Verify response structure
        assert response.status_code == 200
        data = response.json()
        
        # Check all required fields exist
        assert 'prediction' in data
        assert 'historical_nav' in data
        assert 'current_rsi' in data
        assert 'current_volatility' in data
        assert 'current_nav' in data
        
        # Check field types
        assert isinstance(data['prediction'], str)
        assert isinstance(data['historical_nav'], list)
        assert isinstance(data['current_rsi'], (int, float))
        assert isinstance(data['current_volatility'], (int, float))
        assert isinstance(data['current_nav'], (int, float))
        
        # Check historical_nav structure
        if len(data['historical_nav']) > 0:
            nav_point = data['historical_nav'][0]
            assert 'date' in nav_point
            assert 'nav' in nav_point
            assert isinstance(nav_point['date'], str)
            assert isinstance(nav_point['nav'], (int, float))
