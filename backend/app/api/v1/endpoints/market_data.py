from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict
from datetime import datetime, timedelta

from app.db.session import get_db
from app.services.market_data import MarketDataService
from app.models.market_data import MarketData, VolatilityRegime

router = APIRouter()
market_data_service = MarketDataService()

@router.get("/current")
async def get_current_market_data(
    symbol: str = "SPX",
    db: Session = Depends(get_db)
) -> Dict:
    """Get current market data and volatility regime."""
    try:
        # Fetch real-time market data
        market_data = await market_data_service.fetch_market_data(symbol)
        
        # Classify regime
        regime = await market_data_service.classify_regime(market_data)
        
        # Store in database
        db_entry = await market_data_service.store_market_data(db, market_data, regime)
        
        return {
            "market_data": market_data,
            "regime": regime,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/historical")
async def get_historical_data(
    symbol: str = "SPX",
    days: int = 30,
    db: Session = Depends(get_db)
) -> List[Dict]:
    """Get historical market data and regime classifications."""
    try:
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Query database
        historical_data = db.query(MarketData).filter(
            MarketData.symbol == symbol,
            MarketData.timestamp >= start_date,
            MarketData.timestamp <= end_date
        ).order_by(MarketData.timestamp.asc()).all()
        
        return [
            {
                "timestamp": data.timestamp.isoformat(),
                "close": data.close,
                "vix": data.vix,
                "realized_vol": data.realized_vol,
                "implied_vol_atm": data.implied_vol_atm,
                "regime": data.regime,
                "regime_probability": data.regime_probability
            }
            for data in historical_data
        ]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/regimes/summary")
async def get_regime_summary(
    symbol: str = "SPX",
    days: int = 30,
    db: Session = Depends(get_db)
) -> Dict:
    """Get summary statistics of regime classifications."""
    try:
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Query database
        data = db.query(MarketData).filter(
            MarketData.symbol == symbol,
            MarketData.timestamp >= start_date,
            MarketData.timestamp <= end_date
        ).all()
        
        # Calculate regime frequencies
        total_count = len(data)
        regime_counts = {}
        
        for regime in VolatilityRegime:
            count = sum(1 for d in data if d.regime == regime)
            regime_counts[regime] = {
                "count": count,
                "percentage": count / total_count if total_count > 0 else 0
            }
        
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "total_observations": total_count,
            "regime_distribution": regime_counts,
            "current_regime": data[-1].regime if data else None
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 