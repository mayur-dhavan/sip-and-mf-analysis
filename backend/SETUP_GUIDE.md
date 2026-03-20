# Backend Setup Guide

## Overview

This guide walks you through setting up the Mutual Fund Volatility Analyzer backend.

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Git (optional, for version control)

## Directory Structure

The backend follows this structure:

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app initialization with CORS
│   ├── api/
│   │   └── __init__.py         # API routes (to be implemented)
│   ├── services/
│   │   └── __init__.py         # Business logic components
│   ├── models/
│   │   └── __init__.py         # Pydantic schemas
│   └── utils/
│       └── __init__.py         # Utility functions
├── models/
│   └── .gitkeep                # Trained ML models storage
├── scripts/
│   └── .gitkeep                # Training and utility scripts
├── tests/
│   ├── __init__.py
│   └── test_health.py          # Health check endpoint tests
├── requirements.txt            # Python dependencies
├── setup.py                    # Setup verification script
├── setup.bat                   # Windows setup script
├── setup.sh                    # Unix/Linux/macOS setup script
├── .gitignore                  # Git ignore patterns
└── README.md                   # Main documentation
```

## Setup Steps

### Option 1: Automated Setup (Recommended)

**Windows:**
```bash
cd backend
setup.bat
```

**macOS/Linux:**
```bash
cd backend
chmod +x setup.sh
./setup.sh
```

### Option 2: Manual Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment:**
   
   **Windows:**
   ```bash
   venv\Scripts\activate
   ```
   
   **macOS/Linux:**
   ```bash
   source venv/bin/activate
   ```

4. **Upgrade pip:**
   ```bash
   python -m pip install --upgrade pip
   ```

5. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

6. **Verify installation:**
   ```bash
   python setup.py
   ```

## Running the Application

1. **Activate virtual environment** (if not already activated):
   
   **Windows:**
   ```bash
   venv\Scripts\activate
   ```
   
   **macOS/Linux:**
   ```bash
   source venv/bin/activate
   ```

2. **Start the FastAPI server:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Access the application:**
   - API: http://localhost:8000
   - Health Check: http://localhost:8000/api/health/
   - Interactive API Docs: http://localhost:8000/docs
   - Alternative API Docs: http://localhost:8000/redoc

## Testing

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest tests/test_health.py
```

### Run Tests with Verbose Output

```bash
pytest -v
```

### Run Tests with Coverage

```bash
pytest --cov=app tests/
```

## Dependencies

The following packages are installed via `requirements.txt`:

### Web Framework
- **fastapi** (0.104.1): Modern web framework for building APIs
- **uvicorn** (0.24.0): ASGI server for running FastAPI
- **pydantic** (2.5.0): Data validation using Python type hints

### Data Fetching
- **yfinance** (0.2.32): Yahoo Finance API for fetching mutual fund data

### Data Processing
- **pandas** (2.1.3): Data manipulation and analysis
- **numpy** (1.26.2): Numerical computing

### Machine Learning
- **scikit-learn** (1.3.2): ML algorithms and tools
- **joblib** (1.3.2): Model persistence

### Testing
- **pytest** (7.4.3): Testing framework
- **pytest-asyncio** (0.21.1): Async test support
- **hypothesis** (6.92.1): Property-based testing
- **httpx** (0.25.2): HTTP client for testing FastAPI

## Current Features

### Health Check Endpoint

The backend includes a basic health check endpoint:

**Endpoint:** `GET /api/health/`

**Response:**
```json
{
  "status": "healthy",
  "message": "API is running"
}
```

**Test it:**
```bash
curl http://localhost:8000/api/health/
```

### CORS Configuration

CORS middleware is configured to allow:
- All origins (configure for production)
- All methods (GET, POST, etc.)
- All headers
- Credentials

## Next Steps

After completing this setup, the following components need to be implemented:

1. **Data Fetcher** - Fetch mutual fund data from yfinance
2. **Feature Calculator** - Calculate RSI, SMA, and volatility indicators
3. **ML Engine** - Train and load ML models for predictions
4. **API Endpoints** - Implement `/api/predict-volatility/` endpoint
5. **Pydantic Schemas** - Define request/response models
6. **Error Handling** - Custom exceptions and error responses

## Troubleshooting

### Virtual Environment Not Activating

**Windows:**
- Try: `venv\Scripts\Activate.ps1` (PowerShell)
- Or: `venv\Scripts\activate.bat` (Command Prompt)

**macOS/Linux:**
- Ensure script has execute permissions: `chmod +x setup.sh`
- Try: `source venv/bin/activate`

### Module Not Found Errors

Ensure virtual environment is activated and dependencies are installed:
```bash
pip install -r requirements.txt
```

### Port Already in Use

If port 8000 is busy, use a different port:
```bash
uvicorn app.main:app --reload --port 8001
```

### Python Version Issues

Check your Python version:
```bash
python --version
```

Ensure it's 3.9 or higher. If not, install a newer version.

## Development Tips

1. **Keep virtual environment activated** while developing
2. **Use `--reload` flag** during development for auto-restart
3. **Check API docs** at `/docs` for interactive testing
4. **Run tests frequently** to catch issues early
5. **Use type hints** for better IDE support and error detection

## Support

For issues or questions:
1. Check the main README.md
2. Review the design.md and requirements.md in `.kiro/specs/mutual-fund-volatility-analyzer/`
3. Run `python setup.py` to verify installation
