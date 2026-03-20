"""
Setup script for the Mutual Fund Volatility Analyzer backend.
This script helps verify the installation and setup.
"""
import sys


def check_python_version():
    """Check if Python version is 3.9 or higher."""
    if sys.version_info < (3, 9):
        print(f"Error: Python 3.9+ required. Current version: {sys.version}")
        return False
    print(f"✓ Python version: {sys.version.split()[0]}")
    return True


def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        'fastapi',
        'uvicorn',
        'pydantic',
        'yfinance',
        'pandas',
        'numpy',
        'sklearn',
        'pytest',
        'hypothesis',
        'httpx'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} installed")
        except ImportError:
            missing.append(package)
            print(f"✗ {package} not found")
    
    if missing:
        print(f"\nMissing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True


if __name__ == "__main__":
    print("Checking backend setup...\n")
    
    python_ok = check_python_version()
    print()
    
    if python_ok:
        deps_ok = check_dependencies()
        print()
        
        if deps_ok:
            print("✓ All checks passed! Backend is ready.")
            sys.exit(0)
        else:
            print("✗ Some dependencies are missing.")
            sys.exit(1)
    else:
        print("✗ Python version check failed.")
        sys.exit(1)
