# Requirements Document

## Introduction

The Mutual Fund Volatility & Trend Analyzer is a web application that enables users to analyze Indian Small-Cap Mutual Funds by providing AI-predicted volatility forecasts and historical trend visualizations. The system fetches historical NAV data, applies machine learning models to predict market risk levels, and presents insights through an interactive dashboard.

## Glossary

- **System**: The complete Mutual Fund Volatility & Trend Analyzer web application
- **Backend_API**: The Python-based REST API service built with Django REST Framework or FastAPI
- **Frontend_Dashboard**: The Next.js/React-based user interface with Tailwind CSS
- **ML_Engine**: The machine learning component using Scikit-learn with Random Forest or XGBoost
- **Data_Fetcher**: The component responsible for retrieving mutual fund data via yfinance API
- **Feature_Calculator**: The component that computes technical indicators (RSI, SMA, rolling standard deviation)
- **Prediction_Model**: The trained classifier that predicts volatility risk levels
- **NAV**: Net Asset Value - the per-unit price of a mutual fund
- **RSI**: Relative Strength Index - a momentum indicator measuring overbought/oversold conditions
- **SMA**: Simple Moving Average - the average price over a specified period
- **Ticker_Symbol**: The unique identifier for a mutual fund (e.g., "NIPPONINDIA.NS")
- **High_Risk**: A prediction indicating potential downtrend with >2% drop in next 15 days
- **Stable**: A prediction indicating stable or uptrend market conditions
- **Rolling_Volatility**: The 30-day rolling standard deviation of NAV values

## Requirements

### Requirement 1: Data Retrieval

**User Story:** As a user, I want the system to fetch historical mutual fund data, so that I can analyze past performance and trends.

#### Acceptance Criteria

1. WHEN a valid Ticker_Symbol is provided, THE Data_Fetcher SHALL retrieve 3 years of daily NAV data from yfinance API
2. WHEN the yfinance API returns data successfully, THE Data_Fetcher SHALL extract date and NAV values for each trading day
3. IF the yfinance API fails to return data, THEN THE Data_Fetcher SHALL return an error message indicating the data source is unavailable
4. IF an invalid Ticker_Symbol is provided, THEN THE Data_Fetcher SHALL return an error message indicating the ticker is not found
5. THE Data_Fetcher SHALL complete data retrieval within 10 seconds for any valid request

### Requirement 2: Technical Indicator Calculation

**User Story:** As a user, I want the system to calculate technical indicators, so that I can understand market momentum and volatility patterns.

#### Acceptance Criteria

1. WHEN NAV data is available, THE Feature_Calculator SHALL compute the 14-day RSI for all applicable data points
2. WHEN NAV data is available, THE Feature_Calculator SHALL compute the 50-day SMA for all applicable data points
3. WHEN NAV data is available, THE Feature_Calculator SHALL compute the 30-day Rolling_Volatility for all applicable data points
4. THE Feature_Calculator SHALL handle edge cases where insufficient data exists for indicator calculation by returning null values
5. FOR ALL computed indicators, THE Feature_Calculator SHALL produce values within mathematically valid ranges (RSI: 0-100, SMA: positive, Rolling_Volatility: non-negative)

### Requirement 3: Machine Learning Model Training

**User Story:** As a system administrator, I want the ML model to be trained on historical data, so that it can predict future volatility accurately.

#### Acceptance Criteria

1. THE ML_Engine SHALL train the Prediction_Model using Random Forest or XGBoost classifier algorithms
2. WHEN training data includes RSI, SMA, and Rolling_Volatility features, THE ML_Engine SHALL use these features as model inputs
3. THE ML_Engine SHALL label training samples as "1" for High_Risk (>2% drop in next 15 days) and "0" for Stable
4. THE ML_Engine SHALL achieve a minimum training accuracy of 60% on historical data
5. THE ML_Engine SHALL persist the trained Prediction_Model to disk for reuse across requests

### Requirement 4: Volatility Prediction

**User Story:** As a user, I want the system to predict future volatility, so that I can make informed investment decisions.

#### Acceptance Criteria

1. WHEN current technical indicators are calculated, THE Prediction_Model SHALL predict volatility risk for the next 15 days
2. THE Prediction_Model SHALL output either "High_Risk" or "Stable" as the prediction result
3. THE Prediction_Model SHALL complete prediction within 2 seconds after receiving input features
4. WHEN the Prediction_Model outputs "1", THE Backend_API SHALL map this to "High_Risk" in the response
5. WHEN the Prediction_Model outputs "0", THE Backend_API SHALL map this to "Stable" in the response

### Requirement 5: REST API Endpoint

**User Story:** As a frontend developer, I want a REST API endpoint for predictions, so that I can integrate ML capabilities into the user interface.

#### Acceptance Criteria

1. THE Backend_API SHALL expose an endpoint at `/api/predict-volatility/` accepting POST requests
2. WHEN a POST request includes a valid Ticker_Symbol parameter, THE Backend_API SHALL process the prediction request
3. WHEN prediction processing completes successfully, THE Backend_API SHALL return a JSON response with prediction status, historical NAV data, current RSI, and Rolling_Volatility metrics
4. IF any processing step fails, THEN THE Backend_API SHALL return an HTTP error status code with a descriptive error message
5. THE Backend_API SHALL complete the entire request-response cycle within 15 seconds

### Requirement 6: JSON Response Format

**User Story:** As a frontend developer, I want a standardized JSON response format, so that I can reliably parse and display data.

#### Acceptance Criteria

1. THE Backend_API SHALL include a "prediction" field with value "Stable" or "High_Risk" in the JSON response
2. THE Backend_API SHALL include a "historical_nav" field containing an array of date-NAV pairs for the last 6 months
3. THE Backend_API SHALL include a "current_rsi" field with the most recent RSI value
4. THE Backend_API SHALL include a "current_volatility" field with the most recent Rolling_Volatility value
5. THE Backend_API SHALL include a "current_nav" field with the most recent NAV value

### Requirement 7: Frontend Dashboard Layout

**User Story:** As a user, I want a clean professional dashboard, so that I can easily view and understand mutual fund analytics.

#### Acceptance Criteria

1. THE Frontend_Dashboard SHALL display a search component for entering Ticker_Symbol values
2. THE Frontend_Dashboard SHALL display metric cards showing Current NAV, Current RSI, and AI Risk Status
3. WHEN the prediction is "Stable", THE Frontend_Dashboard SHALL display the AI Risk Status card with green styling
4. WHEN the prediction is "High_Risk", THE Frontend_Dashboard SHALL display the AI Risk Status card with red styling
5. THE Frontend_Dashboard SHALL use Tailwind CSS for styling all components

### Requirement 8: Interactive Chart Visualization

**User Story:** As a user, I want to see historical NAV trends in a chart, so that I can visually analyze fund performance.

#### Acceptance Criteria

1. THE Frontend_Dashboard SHALL display an interactive line chart showing NAV values for the last 6 months
2. THE Frontend_Dashboard SHALL overlay the 50-day SMA on the NAV line chart
3. THE Frontend_Dashboard SHALL use Recharts or Chart.js library for chart rendering
4. WHEN a user hovers over the chart, THE Frontend_Dashboard SHALL display tooltip information for that data point
5. THE Frontend_Dashboard SHALL render the chart within 3 seconds after receiving data from the Backend_API

### Requirement 9: Loading States and User Feedback

**User Story:** As a user, I want visual feedback during data processing, so that I know the system is working on my request.

#### Acceptance Criteria

1. WHEN a prediction request is submitted, THE Frontend_Dashboard SHALL display a loading spinner or skeleton screen
2. WHILE the Backend_API processes the request, THE Frontend_Dashboard SHALL disable the search submit button
3. WHEN the Backend_API response is received, THE Frontend_Dashboard SHALL hide the loading indicator and display results
4. THE Frontend_Dashboard SHALL display loading states for a minimum of 500ms to ensure visibility
5. THE Frontend_Dashboard SHALL provide smooth transitions between loading and loaded states

### Requirement 10: Error Handling and User Notifications

**User Story:** As a user, I want clear error messages when something goes wrong, so that I can understand and resolve issues.

#### Acceptance Criteria

1. IF the Backend_API returns an error response, THEN THE Frontend_Dashboard SHALL display a user-friendly error message
2. IF the yfinance API is unavailable, THEN THE Frontend_Dashboard SHALL display a message indicating the data source is temporarily unavailable
3. IF an invalid Ticker_Symbol is entered, THEN THE Frontend_Dashboard SHALL display a message prompting the user to verify the ticker
4. IF network connectivity fails, THEN THE Frontend_Dashboard SHALL display a message indicating connection issues
5. THE Frontend_Dashboard SHALL provide a retry mechanism for failed requests

### Requirement 11: Mutual Fund Search and Selection

**User Story:** As a user, I want to search and select mutual funds easily, so that I can quickly analyze different funds.

#### Acceptance Criteria

1. THE Frontend_Dashboard SHALL provide an input field for entering Ticker_Symbol values
2. THE Frontend_Dashboard SHALL provide a submit button to trigger the prediction request
3. WHEN the submit button is clicked with an empty Ticker_Symbol, THE Frontend_Dashboard SHALL display a validation message
4. THE Frontend_Dashboard SHALL accept Ticker_Symbol values in the format used by yfinance (e.g., "NIPPONINDIA.NS")
5. THE Frontend_Dashboard SHALL trim whitespace from Ticker_Symbol input before submission

### Requirement 12: API Service Integration

**User Story:** As a frontend developer, I want reusable API service functions, so that I can maintain clean separation of concerns.

#### Acceptance Criteria

1. THE Frontend_Dashboard SHALL implement an API service module for Backend_API communication
2. THE API service module SHALL provide a function for calling the `/api/predict-volatility/` endpoint
3. THE API service module SHALL handle HTTP request configuration including headers and request body formatting
4. THE API service module SHALL parse JSON responses and return typed data structures
5. THE API service module SHALL propagate errors to calling components for appropriate handling
