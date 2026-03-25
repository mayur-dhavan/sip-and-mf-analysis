"""
FastAPI application initialization and configuration.
"""
import os
import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Pre-download ML model in background so the first prediction isn't slow."""
    def _warmup_model():
        try:
            from app.services.ml_engine import MLEngine
            engine = MLEngine()
            engine.load_model()
        except Exception as e:
            print(f"Background model warmup failed (will retry on first request): {e}")
    threading.Thread(target=_warmup_model, daemon=True).start()
    yield


# Initialize FastAPI app
app = FastAPI(
    title="Mutual Fund Volatility Analyzer API",
    description="API for predicting mutual fund volatility using ML",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS middleware
cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)


@app.get("/api/health/")
async def health_check():
    """
    Health check endpoint to verify API is running.
    
    Returns:
        dict: Status message indicating API health
    """
    return {"status": "healthy", "message": "API is running"}
