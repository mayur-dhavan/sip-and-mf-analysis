# Implementation Plan: Mutual Fund Volatility & Trend Analyzer

## Overview

This implementation plan breaks down the Mutual Fund Volatility & Trend Analyzer into discrete coding tasks. The system consists of a Python backend (FastAPI) with ML capabilities and a Next.js/React frontend with Tailwind CSS. Tasks are ordered to build incrementally, with early validation through testing and checkpoints.

## Tasks

- [x] 1. Backend project setup and core structure
  - Create backend directory structure with app/, services/, models/, scripts/, tests/ folders
  - Initialize Python virtual environment and create requirements.txt with FastAPI, yfinance, pandas, numpy, scikit-learn, pytest, hypothesis
  - Create main.py with FastAPI app initialization and CORS middleware configuration
  - Create basic health check endpoint at /api/health/
  - _Requirements: 5.1_

- [x] 2. Implement Data Fetcher component
  - [x] 2.1 Create DataFetcher class in services/data_fetcher.py
    - Implement fetch_nav_data() method using yfinance.Ticker().history()
    - Add 10-second timeout handling
    - Define custom exceptions: TickerNotFoundError, DataSourceUnavailableError
    - Return pandas DataFrame with Date index and Close column
    - _Requirements: 1.1, 1.2, 1.5_
  
  - [ ]* 2.2 Write property test for DataFetcher
    - **Property 1: Valid ticker data retrieval completeness**
    - **Validates: Requirements 1.1, 1.2**
    - Verify returned DataFrame has 700-800 data points for 3-year period
  
  - [ ]* 2.3 Write unit tests for DataFetcher error handling
    - Test invalid ticker returns TickerNotFoundError
    - Test API failure returns DataSourceUnavailableError
    - _Requirements: 1.3, 1.4_

- [x] 3. Implement Feature Calculator component
  - [x] 3.1 Create FeatureCalculator class in services/feature_calculator.py
    - Implement calculate_rsi() method with 14-day period
    - Implement calculate_sma() method with 50-day period
    - Implement calculate_rolling_volatility() method with 30-day window
    - Implement calculate_all_features() to compute all indicators
    - _Requirements: 2.1, 2.2, 2.3_
  
  - [ ]* 3.2 Write property tests for Feature Calculator
    - **Property 4: Technical indicator range invariants**
    - **Validates: Requirements 2.5**
    - Verify RSI values are in range [0, 100]
    - Verify SMA values are positive
    - Verify Rolling Volatility values are non-negative
  
  - [ ]* 3.3 Write unit tests for Feature Calculator edge cases
    - Test insufficient data handling (returns NaN)
    - Test calculation accuracy with known input values
    - _Requirements: 2.4_

- [x] 4. Checkpoint - Ensure data fetching and feature calculation work
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Implement ML Engine training script
  - [x] 5.1 Create train_model.py script in scripts/ directory
    - Implement prepare_training_data() function to fetch multiple tickers
    - Implement label generation logic: label=1 if 15-day return < -2%, else 0
    - Use RandomForestClassifier with n_estimators=100, max_depth=10, class_weight='balanced'
    - Split data into 80/20 train/test sets
    - Train model and evaluate accuracy
    - Save model to models/volatility_model.pkl using joblib
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_
  
  - [ ]* 5.2 Write property test for label generation
    - **Property 5: Label generation correctness**
    - **Validates: Requirements 3.3**
    - Verify label=1 when 15-day return < -2%, else label=0
  
  - [ ]* 5.3 Write property test for model persistence
    - **Property 6: Model persistence round-trip**
    - **Validates: Requirements 3.5**
    - Verify save/load produces identical predictions

- [x] 6. Implement ML Engine prediction component
  - [x] 6.1 Create MLEngine class in services/ml_engine.py
    - Implement load_model() method using joblib.load()
    - Implement predict_volatility() method accepting features dict
    - Add 2-second timeout for predictions
    - Return 0 for Stable, 1 for High_Risk
    - _Requirements: 4.1, 4.2, 4.3_
  
  - [ ]* 6.2 Write property test for prediction output validity
    - **Property 7: Prediction output validity**
    - **Validates: Requirements 4.1, 4.2**
    - Verify output is always 0 or 1 for any valid feature set
  
  - [ ]* 6.3 Write unit tests for MLEngine
    - Test model loading from disk
    - Test prediction with known feature values
    - _Requirements: 4.3_

- [x] 7. Implement Pydantic schemas for API
  - [x] 7.1 Create schemas.py in models/ directory
    - Define PredictionRequest model with ticker field
    - Define PredictionResponse model with prediction, historical_nav, current_rsi, current_volatility, current_nav fields
    - Define ErrorResponse model with code, message, details fields
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 8. Implement Backend API endpoint
  - [x] 8.1 Create routes.py in api/ directory
    - Implement POST /api/predict-volatility/ endpoint
    - Orchestrate: fetch data → calculate features → extract latest values → predict → format response
    - Filter historical_nav to last 6 months
    - Add 15-second total timeout
    - Map prediction 0→"Stable", 1→"High_Risk"
    - _Requirements: 5.1, 5.2, 5.3, 5.5, 4.4, 4.5_
  
  - [x] 8.2 Implement error handling in API endpoint
    - Handle TickerNotFoundError → 404 with error response
    - Handle DataSourceUnavailableError → 503 with error response
    - Handle timeout → 504 with error response
    - Handle general exceptions → 500 with error response
    - _Requirements: 5.4, 10.2, 10.3, 10.4_
  
  - [ ]* 8.3 Write property test for API response structure
    - **Property 8: API response structure completeness**
    - **Validates: Requirements 5.3, 6.1, 6.2, 6.3, 6.4, 6.5**
    - Verify all required fields present for any valid ticker
  
  - [ ]* 8.4 Write property test for API error responses
    - **Property 9: API error response consistency**
    - **Validates: Requirements 5.4**
    - Verify error responses have 4xx/5xx status codes, not 200
  
  - [ ]* 8.5 Write integration tests for API endpoint
    - Test full request-response cycle with valid ticker
    - Test error scenarios (invalid ticker, API failure)
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 9. Checkpoint - Ensure backend API is fully functional
  - Ensure all tests pass, ask the user if questions arise.

- [x] 10. Frontend project setup
  - [x] 10.1 Initialize Next.js project with TypeScript and Tailwind CSS
    - Create frontend directory with Next.js 14+ App Router
    - Configure Tailwind CSS in tailwind.config.js
    - Set up TypeScript with strict mode in tsconfig.json
    - Install dependencies: recharts, axios
    - _Requirements: 7.5_
  
  - [x] 10.2 Create TypeScript type definitions
    - Create types/index.ts with interfaces: HistoricalNavPoint, PredictionData, ApiError
    - _Requirements: 12.4_

- [x] 11. Implement API service module
  - [x] 11.1 Create api.ts in services/ directory
    - Implement predictVolatility() function using fetch or axios
    - Configure POST request to /api/predict-volatility/
    - Parse JSON response into PredictionData type
    - Handle network errors and HTTP errors
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_
  
  - [ ]* 11.2 Write property test for API service response parsing
    - **Property 12: API service response parsing**
    - **Validates: Requirements 12.4**
    - Verify successful parsing for any valid JSON response
  
  - [ ]* 11.3 Write property test for API service error propagation
    - **Property 13: API service error propagation**
    - **Validates: Requirements 12.5**
    - Verify errors are propagated in structured format
  
  - [ ]* 11.4 Write unit tests for API service
    - Test request formatting
    - Test error handling for network failures
    - _Requirements: 12.3, 12.5_

- [x] 12. Implement Search Component
  - [x] 12.1 Create SearchComponent.tsx in components/ directory
    - Create input field for ticker symbol
    - Create submit button with loading state
    - Implement client-side validation (non-empty, trimmed)
    - Disable submit button when loading
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_
  
  - [ ]* 12.2 Write property test for input trimming
    - **Property 11: Input sanitization**
    - **Validates: Requirements 11.5**
    - Verify whitespace is trimmed before submission
  
  - [ ]* 12.3 Write unit tests for SearchComponent
    - Test rendering and user interaction
    - Test validation messages
    - _Requirements: 11.3_

- [x] 13. Implement Metrics Dashboard components
  - [x] 13.1 Create MetricCard.tsx component
    - Accept title, value, variant props
    - Style with Tailwind CSS
    - Support 'default', 'success', 'danger' variants
    - _Requirements: 7.2, 7.5_
  
  - [x] 13.2 Create MetricsDashboard.tsx component
    - Display three MetricCard components for Current NAV, Current RSI, AI Risk Status
    - Apply green styling for "Stable" prediction
    - Apply red styling for "High_Risk" prediction
    - _Requirements: 7.2, 7.3, 7.4_
  
  - [ ]* 13.3 Write unit tests for Metrics Dashboard
    - Test correct styling for Stable vs High_Risk
    - Test metric values display correctly
    - _Requirements: 7.3, 7.4_

- [x] 14. Implement Chart Component
  - [x] 14.1 Create ChartComponent.tsx in components/ directory
    - Use Recharts LineChart with two lines (NAV and SMA)
    - Configure tooltip to show date, NAV, and SMA on hover
    - Make chart responsive with ResponsiveContainer
    - Style with Tailwind CSS
    - _Requirements: 8.1, 8.2, 8.3, 8.4_
  
  - [ ]* 14.2 Write unit tests for ChartComponent
    - Test chart renders with data
    - Test tooltip functionality
    - _Requirements: 8.4_

- [x] 15. Implement Loading and Error components
  - [x] 15.1 Create LoadingSpinner.tsx component
    - Display animated spinner with Tailwind CSS
    - _Requirements: 9.1_
  
  - [x] 15.2 Create ErrorMessage.tsx component
    - Display user-friendly error messages
    - Include retry button
    - Style with Tailwind CSS
    - _Requirements: 10.1, 10.5_
  
  - [ ]* 15.3 Write property test for error display
    - **Property 10: Frontend error display**
    - **Validates: Requirements 10.1**
    - Verify user-friendly messages for any error response
  
  - [ ]* 15.4 Write unit tests for Loading and Error components
    - Test LoadingSpinner renders
    - Test ErrorMessage displays correct text
    - Test retry button functionality
    - _Requirements: 9.1, 10.5_

- [x] 16. Implement Main Page component
  - [x] 16.1 Create page.tsx in app/ directory
    - Manage state: data, loading, error
    - Implement handleSearch function to call API service
    - Render SearchComponent with onSearch callback
    - Conditionally render LoadingSpinner, ErrorMessage, or results
    - Render MetricsDashboard and ChartComponent when data is available
    - _Requirements: 7.1, 9.1, 9.2, 9.3, 10.1_
  
  - [x] 16.2 Add loading state transitions
    - Display loading for minimum 500ms
    - Disable submit button while loading
    - Smooth transitions between states
    - _Requirements: 9.2, 9.4, 9.5_
  
  - [ ]* 16.3 Write integration tests for Main Page
    - Test full user flow: search → loading → results
    - Test error flow: search → error → retry
    - _Requirements: 9.1, 9.2, 9.3, 10.5_

- [x] 17. Configure API base URL and environment variables
  - [x] 17.1 Create .env.local file for frontend
    - Set NEXT_PUBLIC_API_BASE_URL environment variable
    - Update api.ts to use environment variable
  
  - [x] 17.2 Create .env file for backend
    - Set any required environment variables (if needed)

- [x] 18. Add global styling and layout
  - [x] 18.1 Update globals.css with Tailwind directives
    - Add custom styles for consistent spacing and typography
  
  - [x] 18.2 Create layout.tsx with app metadata
    - Set page title and description
    - Configure responsive viewport
    - _Requirements: 7.1_

- [ ] 19. Final checkpoint - End-to-end testing
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 20. Create documentation
  - [ ] 20.1 Create backend README.md
    - Document API endpoints
    - Document setup instructions
    - Document model training process
  
  - [ ] 20.2 Create frontend README.md
    - Document component structure
    - Document setup and development instructions
    - Document environment variables

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at key milestones
- Property tests validate universal correctness properties across all inputs
- Unit tests validate specific examples, edge cases, and integration points
- Backend uses Python with FastAPI, frontend uses Next.js with TypeScript
- All property tests must run minimum 100 iterations
