# SIP and Mutual Fund (MF) Analysis

A comprehensive application for Mutual Fund Volatility Analysis, featuring a FastAPI Python backend and a Next.js React frontend.

## Project Structure

- ackend/: FastAPI application for data fetching, ML engines, API routes, and model registry.
- rontend/: Next.js web application for metrics dashboards, charts, and SIP calculators.
- huggingface_space/: Resources for deploying the model/app to Hugging Face Spaces.

## Getting Started

### 1. Backend Setup & Run

The backend handles the core logic, machine learning models, and API endpoints.

**Prerequisites:** Python 3.9+

**Dependencies Setup:**
``bash
cd backend
pip install -r requirements.txt
# Alternatively, use the provided setup scripts: .\setup.bat (Windows) or ./setup.sh (Unix)
``

**Run the Backend Server:**
``bash
cd backend
python -m uvicorn app.main:app --reload
``
*(The backend API usually runs on http://localhost:8000)*

### 2. Retraining the ML Model

To manually retrain the machine learning model using the latest data:

``bash
cd backend
python scripts/train_model.py
``

*Additional Training Scripts:*
- python scripts/automated_retrain.py: Automated retraining workflow.
- python scripts/daily_retrain_and_upload.py: Retrains and handles daily upload tasks.

### 3. Frontend Setup & Run

The frontend is a Next.js application providing the user interface.

**Prerequisites:** Node.js (v18+)

**Dependencies Setup:**
``bash
cd frontend
npm install
``

**Run the Frontend Development Server:**
``bash
cd frontend
npm run dev
``
*(The frontend usually runs on http://localhost:3000)*

## Key Features

- **SIP Calculator:** Evaluate returns based on SIP investments.
- **Volatility Analysis:** ML-driven analysis of mutual fund metrics.
- **Model Registry:** Automatic versioning of ML models inside the backend registry.

## Deployment

You can deploy the app or interactive portions to Hugging Face utilizing the scripts in huggingface_space/ or via python scripts/deploy_hf_space.py.
