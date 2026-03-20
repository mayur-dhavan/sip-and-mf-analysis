"""
FastAPI application initialization and configuration.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router

# Initialize FastAPI app
app = FastAPI(
    title="Mutual Fund Volatility Analyzer API",
    description="API for predicting mutual fund volatility using ML",
    version="1.0.0"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
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
