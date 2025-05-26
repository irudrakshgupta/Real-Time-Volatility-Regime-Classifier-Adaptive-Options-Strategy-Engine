from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from typing import Dict
import os

from app.core.config import settings
from app.api.v1.api import api_router
from app.core.logger import setup_logging

app = FastAPI(
    title="VolCortex API",
    description="Real-Time Volatility Regime Classifier & Options Strategy Engine",
    version="1.0.0",
)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup logging
setup_logging()

# Include API router
app.include_router(api_router, prefix=f"/api/{settings.API_VERSION}")

@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
    ) 