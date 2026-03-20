# Mutual Fund Volatility Analyzer - Backend

Python backend API for predicting mutual fund volatility using machine learning.

## Quick Setup

### Automated Setup (Recommended)

**Windows:**
```bash
setup.bat
```

**macOS/Linux:**
```bash
chmod +x setup.sh
./setup.sh
```

### Manual Setup

#### 1. Create Virtual Environment

```bash
python -m venv venv
```

#### 2. Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Verify Setup

```bash
python setup.py
```

## Running the Application

Start the FastAPI development server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Health Check: http://localhost:8000/api/health/
- API Documentation: http://localhost:8000/docs

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app initialization
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py           # API endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── data_fetcher.py     # Data fetching logic
│   │   ├── feature_calculator.py  # Technical indicators
│   │   └── ml_engine.py        # ML prediction logic
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Pydantic models
│   └── utils/
│       ├── __init__.py
│       └── exceptions.py       # Custom exceptions
├── models/
│   └── volatility_model.pkl    # Trained ML model
├── scripts/
│   └── train_model.py          # Model training script
├── tests/
│   └── ...                     # Test files
├── requirements.txt
└── README.md
```

## Testing

Run all tests:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=app tests/
```

## API Endpoints

### Health Check
- **GET** `/api/health/`
- Returns API health status

### Predict Volatility (Coming Soon)
- **POST** `/api/predict-volatility/`
- Predicts mutual fund volatility risk

## Automated Retraining and Model Versioning

The backend supports periodic retraining with champion/challenger promotion.

### One-Off Automated Cycle

```bash
python scripts/automated_retrain.py --once
```

### Periodic Retraining Loop (e.g., every 24 hours)

```bash
python scripts/automated_retrain.py --interval-hours 24
```

### Optional Promotion Strictness

```bash
python scripts/automated_retrain.py --interval-hours 24 --min-score-improvement 0.005
```

How it works:
- Trains a challenger model and saves it under `models/challengers/`.
- Registers the challenger in `models/registry/manifest.json`.
- Compares challenger score vs current champion score.
- Promotes the challenger only if it beats champion by the configured margin.
- Writes serving champion artifact to `models/volatility_model.pkl`.
