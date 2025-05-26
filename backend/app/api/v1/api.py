from fastapi import APIRouter

from app.api.v1.endpoints import market_data, strategy

api_router = APIRouter()

api_router.include_router(
    market_data.router,
    prefix="/market-data",
    tags=["market-data"]
)

api_router.include_router(
    strategy.router,
    prefix="/strategy",
    tags=["strategy"]
) 