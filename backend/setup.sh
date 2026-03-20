#!/bin/bash
# Setup script for Unix/Linux/macOS

echo "Setting up Mutual Fund Volatility Analyzer Backend..."
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Verify setup
echo ""
echo "Verifying setup..."
python setup.py

echo ""
echo "Setup complete!"
echo "To activate the virtual environment, run: source venv/bin/activate"
echo "To start the server, run: uvicorn app.main:app --reload"
