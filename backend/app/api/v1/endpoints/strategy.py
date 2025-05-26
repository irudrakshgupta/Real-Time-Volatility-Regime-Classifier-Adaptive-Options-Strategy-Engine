from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from datetime import datetime

from app.db.session import get_db
from app.services.strategy import StrategyService
from app.services.market_data import MarketDataService
from app.models.market_data import MarketData

router = APIRouter()
strategy_service = StrategyService()
market_data_service = MarketDataService()

@router.get("/recommend")
async def get_strategy_recommendations(
    symbol: str = "SPX",
    risk_tolerance: str = "moderate",
    db: Session = Depends(get_db)
) -> Dict:
    """Get strategy recommendations based on current market conditions."""
    try:
        # Get current market data
        market_data = await market_data_service.fetch_market_data(symbol)
        
        # Get current regime
        regime = await market_data_service.classify_regime(market_data)
        
        # Get strategy recommendations
        recommendations = strategy_service.recommend_strategy(
            regime=regime,
            market_data=market_data,
            risk_tolerance=risk_tolerance
        )
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "market_conditions": {
                "regime": regime,
                "vix": market_data["vix"],
                "realized_vol": market_data["realized_vol"],
                "implied_vol": market_data["implied_vol_atm"],
                "skew": market_data["skew"]
            },
            "recommendations": recommendations
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze")
async def analyze_strategy(
    strategy_type: str,
    params: Dict,
    symbol: str = "SPX",
    db: Session = Depends(get_db)
) -> Dict:
    """Analyze a specific options strategy with given parameters."""
    try:
        # Get current market data
        market_data = await market_data_service.fetch_market_data(symbol)
        
        # Calculate strategy metrics
        metrics = strategy_service.calculate_strategy_metrics(
            strategy_type=strategy_type,
            market_data=market_data,
            params=params
        )
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "strategy_type": strategy_type,
            "parameters": params,
            "metrics": metrics
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/backtest")
async def backtest_strategy(
    strategy_type: str,
    params: Dict,
    symbol: str = "SPX",
    days: int = 30,
    db: Session = Depends(get_db)
) -> Dict:
    """Backtest a strategy over historical data."""
    try:
        # Get historical data
        historical_data = db.query(MarketData).filter(
            MarketData.symbol == symbol
        ).order_by(
            MarketData.timestamp.desc()
        ).limit(days).all()
        
        # Initialize results containers
        pnl_series = []
        metrics_series = []
        
        # Simulate strategy performance
        for data in historical_data:
            # Calculate strategy metrics for each historical point
            daily_metrics = strategy_service.calculate_strategy_metrics(
                strategy_type=strategy_type,
                market_data={
                    "close": data.close,
                    "vix": data.vix,
                    "realized_vol": data.realized_vol,
                    "implied_vol_atm": data.implied_vol_atm,
                    "skew": data.skew
                },
                params=params
            )
            
            pnl_series.append({
                "timestamp": data.timestamp.isoformat(),
                "pnl": daily_metrics["expected_profit"]
            })
            
            metrics_series.append({
                "timestamp": data.timestamp.isoformat(),
                "metrics": daily_metrics
            })
        
        return {
            "strategy_type": strategy_type,
            "parameters": params,
            "backtest_period": {
                "start": historical_data[-1].timestamp.isoformat(),
                "end": historical_data[0].timestamp.isoformat()
            },
            "pnl_series": pnl_series,
            "metrics_series": metrics_series,
            "summary_statistics": {
                "total_return": sum(p["pnl"] for p in pnl_series),
                "win_rate": len([p for p in pnl_series if p["pnl"] > 0]) / len(pnl_series),
                "max_drawdown": min(p["pnl"] for p in pnl_series),
                "sharpe_ratio": metrics_series[0]["metrics"]["risk_metrics"]["sharpe_ratio"]
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 