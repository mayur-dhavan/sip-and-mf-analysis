# SIP and Mutual Fund (MF) Volatility Analyzer

A full-stack application that uses machine learning to predict mutual fund volatility risk for Indian markets. Enter any NSE/BSE mutual fund ticker, and the app analyzes 5 years of NAV data across 19 technical indicators to classify the fund as **Stable** or **High Risk**.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
  - [Backend Setup](#1-backend-setup)
  - [Frontend Setup](#2-frontend-setup)
- [Environment Variables](#environment-variables)
- [ML Model](#ml-model)
  - [Features (Technical Indicators)](#features-technical-indicators)
  - [Model Architecture](#model-architecture)
  - [Model Registry & Versioning](#model-registry--versioning)
- [Retraining the Model](#retraining-the-model)
  - [Manual Retrain](#manual-retrain)
  - [Automated Retrain](#automated-retrain)
  - [Daily Retrain & Upload](#daily-retrain--upload)
- [Running the Full Application](#running-the-full-application)
- [API Reference](#api-reference)
- [Frontend Features](#frontend-features)
- [Hugging Face Deployment](#hugging-face-deployment)
- [Running Tests](#running-tests)
- [Troubleshooting](#troubleshooting)

---

## Project Overview

This project provides:

- **ML-powered volatility prediction** — A stacked ensemble classifier trained on 5 years of Indian mutual fund & benchmark NAV data
- **19 technical indicators** — RSI, MACD, Bollinger Bands, Sharpe Ratio, Drawdown, SMA/EMA, Z-Score and more
- **Champion/Challenger model registry** — Automatic version tracking and promotion of better-performing models
- **Interactive web UI** — Next.js dashboard to search funds, view NAV charts, metrics, and run SIP calculations
- **Hugging Face integration** — Model served and deployed as a Gradio space

---

## Architecture

```
+------------------------------------------------------------------+
|                        User Browser                              |
|                  Next.js Frontend  :3000                         |
+------------------------+-----------------------------------------+
                         | HTTP (REST)
                         v
+------------------------------------------------------------------+
|               FastAPI Backend  :8000                             |
|  +--------------+  +------------------+  +------------------+   |
|  | DataFetcher  |  |FeatureCalculator |  |    MLEngine      |   |
|  |  yfinance +  |->|  19 Technical    |->|  Stacked         |   |
|  |  AMFI Master |  |  Indicators      |  |  Ensemble Model  |   |
|  +--------------+  +------------------+  +------------------+   |
|                                               |                  |
|                                      +------------------+        |
|                                      |  ModelRegistry   |        |
|                                      |  champion/vers.  |        |
|                                      +------------------+        |
+------------------------------------------------------------------+
                         | fallback download
                         v
             Hugging Face Space (Gradio)
         mayur6901/sip-mf-volatility-predictor
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Next.js 16.2, React 19, TypeScript, TailwindCSS 4, Recharts |
| **Backend** | FastAPI, Uvicorn, Pydantic v2, Python 3.9+ |
| **Data** | yfinance, AMFI Master Fund List, pandas, numpy |
| **ML** | scikit-learn, XGBoost, joblib |
| **Model Hosting** | Hugging Face Hub (`huggingface_hub`) |
| **Testing** | pytest, pytest-asyncio, httpx, hypothesis |

---

## Project Structure

```
SIP and MF Analysis/
+-- README.md                              <- You are here
¦
+-- backend/
¦   +-- app/
¦   ¦   +-- main.py                        <- FastAPI app, CORS, lifespan warmup
¦   ¦   +-- api/
¦   ¦   ¦   +-- routes.py                  <- API endpoints (predict, search, health)
¦   ¦   +-- data/
¦   ¦   ¦   +-- amfi_master.py             <- AMFI Indian fund ticker database
¦   ¦   +-- models/
¦   ¦   ¦   +-- schemas.py                 <- Pydantic request/response schemas
¦   ¦   +-- services/
¦   ¦   ¦   +-- data_fetcher.py            <- NAV data from yfinance + AMFI
¦   ¦   ¦   +-- feature_calculator.py      <- 19 technical indicator calculations
¦   ¦   ¦   +-- feature_config.py          <- Shared feature column definitions
¦   ¦   ¦   +-- ml_engine.py               <- Model loading, HF download, prediction
¦   ¦   ¦   +-- model_registry.py          <- Champion/challenger versioning
¦   ¦   +-- utils/
¦   ¦       +-- exceptions.py              <- Custom exceptions
¦   +-- models/
¦   ¦   +-- volatility_model.pkl           <- Active serving model
¦   ¦   +-- challengers/                   <- Newly trained challengers
¦   ¦   +-- registry/
¦   ¦       +-- manifest.json              <- Version history + champion tracking
¦   ¦       +-- versions/                  <- All versioned model artifacts
¦   +-- scripts/
¦   ¦   +-- train_model.py                 <- Full training pipeline
¦   ¦   +-- automated_retrain.py           <- Champion/challenger retrain loop
¦   ¦   +-- daily_retrain_and_upload.py    <- Scheduled retrain + HF upload
¦   ¦   +-- create_mock_model.py           <- Mock model for testing
¦   +-- tests/
¦   ¦   +-- test_health.py
¦   ¦   +-- test_api_routes.py
¦   ¦   +-- test_data_fetcher.py
¦   ¦   +-- test_feature_calculator.py
¦   ¦   +-- test_model_registry.py
¦   ¦   +-- test_integration.py
¦   +-- requirements.txt
¦   +-- setup.bat                          <- Windows automated setup
¦   +-- setup.sh                           <- Unix automated setup
¦
+-- frontend/
¦   +-- app/
¦   ¦   +-- layout.tsx                     <- Root layout
¦   ¦   +-- page.tsx                       <- Main app page
¦   +-- components/
¦   ¦   +-- SearchComponent.tsx            <- Fund ticker search
¦   ¦   +-- MetricsDashboard.tsx           <- Full metrics panel
¦   ¦   +-- MetricCard.tsx                 <- Individual metric tile
¦   ¦   +-- ChartComponent.tsx             <- NAV + SMA chart (Recharts)
¦   ¦   +-- SipCalculator.tsx              <- SIP return calculator
¦   ¦   +-- LoadingSpinner.tsx
¦   ¦   +-- ErrorMessage.tsx
¦   +-- services/
¦   ¦   +-- api.ts                         <- Backend API client
¦   +-- types/
¦   ¦   +-- index.ts                       <- TypeScript interfaces
¦   +-- package.json
¦
+-- huggingface_space/
¦   +-- app.py                             <- Gradio app for HF Space
¦   +-- requirements.txt
¦
+-- scripts/
    +-- deploy_hf_space.py                 <- Deploy to Hugging Face
```

---

## Quick Start

### 1. Backend Setup

**Prerequisites:** Python 3.9 or higher, pip

#### Option A — Automated (Recommended)

```bash
cd backend

# Windows
setup.bat

# Linux/macOS
chmod +x setup.sh && ./setup.sh
```

#### Option B — Manual

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/macOS)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Start the Backend Server

```bash
cd backend
python -m uvicorn app.main:app --reload
```

The API runs at **http://localhost:8000**

> On first startup, the backend automatically downloads the pre-trained model from
> Hugging Face (`mayur6901/sip-mf-volatility-predictor`) if no local model exists.

---

### 2. Frontend Setup

**Prerequisites:** Node.js 18+

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The app runs at **http://localhost:3000**

#### Other frontend commands

```bash
npm run build    # Production build
npm run start    # Start production server
npm run lint     # Run ESLint
```

---

## Environment Variables

### Backend — `backend/.env`

| Variable | Default | Description |
|---|---|---|
| `CORS_ORIGINS` | `*` | Comma-separated list of allowed CORS origins |
| `MODEL_DECISION_THRESHOLD_OVERRIDE` | *(from model artifact)* | Override the model's decision threshold (0–1) |

### Frontend — `frontend/.env.local`

| Variable | Default | Description |
|---|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | `http://localhost:8000` | Backend API base URL |

---

## ML Model

### Features (Technical Indicators)

The model uses **19 technical indicators** computed from 5 years of daily NAV data:

| Feature | Description |
|---|---|
| `RSI` | 14-day Relative Strength Index (0–100) |
| `SMA_20` | 20-day Simple Moving Average |
| `SMA_50` | 50-day Simple Moving Average |
| `EMA_20` | 20-day Exponential Moving Average |
| `Rolling_Volatility_10` | 10-day rolling standard deviation |
| `Rolling_Volatility_30` | 30-day rolling standard deviation |
| `Daily_Return` | Single-day percentage return |
| `ROC_10` | 10-day Rate of Change |
| `MACD` | MACD line (EMA12 - EMA26) |
| `MACD_Signal` | 9-day EMA of MACD |
| `MACD_Hist` | MACD - Signal histogram |
| `BB_Width` | Bollinger Band width (normalised) |
| `NAV_to_SMA50_Ratio` | NAV / SMA50 |
| `Volatility_Ratio` | Short-term / Long-term volatility |
| `Return_5` | 5-day cumulative return |
| `Return_20` | 20-day cumulative return |
| `Sharpe_30` | 30-day rolling Sharpe Ratio (annualised) |
| `ZScore_20` | Z-score vs 20-day rolling mean |
| `Drawdown_60` | 60-day rolling drawdown from peak |

### Model Architecture

The training pipeline builds a **stacked ensemble classifier**:

```
Base Estimators (Level 0):
  +-- RandomForestClassifier
  +-- GradientBoostingClassifier
  +-- ExtraTreesClassifier
  +-- XGBClassifier  (falls back to GradientBoosting if XGBoost not installed)

Meta Estimator (Level 1):
  +-- LogisticRegression
```

**Label Generation:** A fund is labelled `High_Risk` if its NAV drops more than 2% in
the next 15 trading days. An adaptive quantile fallback is applied if the positive class
is under-represented (<12%) or over-represented (>42%) in training data.

**Current champion model — `v20260325T060101Z`:**

| Metric | Score |
|---|---|
| Accuracy | 90.5% |
| Weighted F1 | 90.8% |
| ROC-AUC | 0.941 |
| CV F1 Mean (5-fold) | 0.861 |
| High-Risk Precision | 68.3% |
| High-Risk Recall | 80.5% |
| Decision Threshold | 0.68 |

### Model Registry & Versioning

Every training run creates a **challenger** artifact. The registry compares it against
the current **champion**. If the challenger's score exceeds the champion by at least
`0.003`, it is automatically promoted to become the new serving model.

```
backend/models/
+-- volatility_model.pkl           <- Current serving champion (symlinked/copied)
+-- challengers/                   <- Newly trained, pending evaluation
+-- registry/
    +-- manifest.json              <- Champion + all version metadata
    +-- versions/
        +-- v20260325T060101Z_volatility_model.pkl   <- Current champion
        +-- ...                                       <- Older versions
```

---

## Retraining the Model

### Manual Retrain

Run a single full training cycle from scratch using 5 years of data:

```bash
cd backend
python scripts/train_model.py
```

What this does:
1. Fetches NAV data for up to **150 AMFI schemes** + NSE/BSE benchmarks (`^NSEI`, `^NSMIDCP`, `^NSEBANK`, `^BSESN`, `^CNXIT`)
2. Computes all 19 technical features per ticker
3. Trains the stacked ensemble with 5-fold stratified cross-validation
4. Optimises the decision threshold for High-Risk recall
5. Saves the model to `models/volatility_model.pkl`
6. Registers it as a challenger in the model registry
7. Promotes it to champion if it beats the current best score

---

### Automated Retrain

Runs a champion/challenger cycle on a schedule with configurable flags:

```bash
cd backend

# Run one retraining cycle then exit
python scripts/automated_retrain.py --once

# Run every 24 hours continuously (default)
python scripts/automated_retrain.py --interval-hours 24

# Custom interval + stricter promotion threshold
python scripts/automated_retrain.py --interval-hours 12 --min-score-improvement 0.01

# Require higher minimum accuracy before a challenger can be promoted
python scripts/automated_retrain.py --once --minimum-accuracy 0.70
```

**All flags:**

| Flag | Default | Description |
|---|---|---|
| `--once` | — | Run one cycle and exit |
| `--interval-hours` | `24` | Hours between retraining cycles |
| `--min-score-improvement` | `0.003` | Minimum score gain to promote a challenger |
| `--minimum-accuracy` | `0.55` | Reject challengers below this accuracy |

---

### Daily Retrain & Upload

Retrains the model and uploads the new artifact to Hugging Face:

```bash
cd backend
python scripts/daily_retrain_and_upload.py
```

---

### Create Mock Model (for Testing)

Generates a lightweight placeholder model without fetching live data:

```bash
cd backend
python scripts/create_mock_model.py
```

---

## Running the Full Application

Open **two terminals** simultaneously:

**Terminal 1 — Backend:**
```bash
cd backend
venv\Scripts\activate           # Windows
# source venv/bin/activate      # Linux/macOS
python -m uvicorn app.main:app --reload
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```

Then open **http://localhost:3000** in your browser.

---

## API Reference

Base URL: `http://localhost:8000`

---

### `GET /api/health/`

Health check — confirms the API is running.

**Response:**
```json
{ "status": "healthy", "message": "API is running" }
```

---

### `POST /api/predict-volatility/`

Predicts volatility risk for a given mutual fund ticker. Fetches 5 years of NAV,
computes all 19 features, and returns the ML prediction with full metrics.

**Request body:**
```json
{ "ticker": "NIPPONINDIA.NS" }
```

**Response:**
```json
{
  "prediction": "Stable",
  "ticker": "NIPPONINDIA.NS",
  "fund_name": "Nippon India Large Cap Fund",
  "current_nav": 42.35,
  "current_rsi": 58.2,
  "current_volatility": 0.012,
  "risk_probability": 0.23,
  "model_confidence": 0.77,
  "analysis_summary": "Fund shows stable momentum ...",
  "current_macd": 0.14,
  "current_macd_signal": 0.10,
  "bb_width": 0.032,
  "sharpe_30": 1.45,
  "drawdown_60": -0.03,
  "sma_20": 41.8,
  "sma_50": 40.5,
  "return_5": 0.012,
  "return_20": 0.034,
  "zscore_20": 0.85,
  "volatility_ratio": 0.92,
  "nav_to_sma50_ratio": 1.04,
  "daily_return": 0.003,
  "historical_nav": [
    { "date": "2025-11-15", "nav": 40.1 },
    { "date": "2025-11-18", "nav": 40.5 }
  ]
}
```

**Error codes:**

| HTTP Status | Code | Reason |
|---|---|---|
| 404 | `TICKER_NOT_FOUND` | Unknown or unsupported ticker symbol |
| 503 | `DATA_SOURCE_UNAVAILABLE` | yfinance or AMFI data source unreachable |
| 504 | `TIMEOUT` | Request exceeded the 40-second processing limit |
| 500 | `PREDICTION_ERROR` | Internal model or data processing error |

---

### `GET /api/search-funds/?q={query}`

Search for supported mutual fund tickers by name or keyword.

**Example:** `GET /api/search-funds/?q=nippon`

**Response:**
```json
{
  "query": "nippon",
  "results": [
    {
      "ticker": "NIPPONINDIA.NS",
      "name": "Nippon India Large Cap Fund",
      "fund_house": "Nippon India",
      "category": "Large Cap",
      "is_supported": true
    }
  ]
}
```

---

## Frontend Features

| Component | Description |
|---|---|
| **SearchComponent** | Type-ahead fund name/ticker search with live suggestions |
| **MetricsDashboard** | Full metrics panel showing all 19 indicators and the prediction |
| **MetricCard** | Individual metric tile with formatted value and label |
| **ChartComponent** | Interactive NAV line chart with 50-day SMA overlay (powered by Recharts) |
| **SipCalculator** | Compute SIP returns given monthly investment, duration, and expected rate |
| **LoadingSpinner** | Shown while API request is in progress |
| **ErrorMessage** | User-friendly error display with retry button |

---

## Hugging Face Deployment

The model and a standalone Gradio prediction interface are hosted on Hugging Face.

**Space:** `mayur6901/sip-mf-volatility-predictor`

The Gradio app (`huggingface_space/app.py`) replicates the full prediction pipeline —
data fetching, feature calculation, and model inference — independently of the FastAPI backend.

**Deploy or update the HF Space:**
```bash
python scripts/deploy_hf_space.py
```

The FastAPI backend will automatically download the model from this Space during startup
if `backend/models/volatility_model.pkl` does not exist locally.

---

## Running Tests

```bash
cd backend

# Run all tests
pytest tests/

# Verbose output
pytest tests/ -v

# Specific test files
pytest tests/test_api_routes.py -v
pytest tests/test_feature_calculator.py -v
pytest tests/test_model_registry.py -v
pytest tests/test_data_fetcher.py -v
pytest tests/test_integration.py -v
pytest tests/test_health.py -v
```

---

## Troubleshooting

**Model not found on startup?**
The app auto-downloads from Hugging Face on first run. Ensure you have internet access and
`huggingface_hub` is installed. Or train a local model: `python scripts/train_model.py`

**`TickerNotFoundError` when searching?**
Use a valid NSE (`.NS`) or BSE (`.BO`) ticker from yfinance, e.g.:
- `HDFCBANK.NS` — HDFC Bank (NSE)
- `0P0000XV5N.BO` — AMFI fund on BSE
- `^NSEI` — Nifty 50 benchmark

**Frontend not connecting to backend?**
Verify the backend is running on port 8000. Set `NEXT_PUBLIC_API_BASE_URL` in
`frontend/.env.local` if using a non-default URL or a deployed backend.

**CORS errors in browser?**
Set `CORS_ORIGINS=http://localhost:3000` in `backend/.env` (or your frontend URL in production).

**Training takes too long?**
Reduce `MAX_AMFI_TRAINING_SCHEMES` in `scripts/train_model.py` (default: 150).

**XGBoost not found?**
Install it: `pip install xgboost`. The training script falls back to `GradientBoostingClassifier`
if XGBoost is unavailable, but XGBoost is recommended for best performance.
