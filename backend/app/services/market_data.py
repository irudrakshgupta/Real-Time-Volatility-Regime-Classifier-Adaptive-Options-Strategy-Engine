import yfinance as yf
from alpha_vantage.timeseries import TimeSeries
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Optional

from app.core.config import settings
from app.models.market_data import MarketData, VolatilityRegime
from app.services.volatility import calculate_realized_volatility, calculate_implied_volatility

logger = logging.getLogger(__name__)

class MarketDataService:
    def __init__(self):
        self.alpha_vantage = TimeSeries(key=settings.ALPHA_VANTAGE_API_KEY)
        
    async def fetch_market_data(self, symbol: str = settings.DEFAULT_TICKER) -> Dict:
        """Fetch real-time market data for a given symbol."""
        try:
            # Fetch data from yfinance
            ticker = yf.Ticker(symbol)
            current_data = ticker.history(period="1d", interval="1m").iloc[-1]
            
            # Fetch VIX data
            vix = yf.Ticker("^VIX")
            vix_data = vix.history(period="1d").iloc[-1]["Close"]
            
            # Calculate realized volatility
            historical_data = ticker.history(period="30d")
            realized_vol = calculate_realized_volatility(historical_data["Close"])
            
            # Get implied volatility metrics
            options_data = ticker.options[0]  # Get nearest expiration
            implied_vol = calculate_implied_volatility(ticker, options_data)
            
            market_data = {
                "timestamp": datetime.utcnow(),
                "symbol": symbol,
                "open": float(current_data["Open"]),
                "high": float(current_data["High"]),
                "low": float(current_data["Low"]),
                "close": float(current_data["Close"]),
                "volume": float(current_data["Volume"]),
                "vix": float(vix_data),
                "realized_vol": float(realized_vol),
                "implied_vol_atm": float(implied_vol["atm"]),
                "skew": float(implied_vol["skew"]),
                "vvix": float(implied_vol.get("vvix", 0))
            }
            
            return market_data
            
        except Exception as e:
            logger.error(f"Error fetching market data: {str(e)}")
            raise
    
    async def classify_regime(self, market_data: Dict) -> VolatilityRegime:
        """Classify the current volatility regime based on market data."""
        try:
            # TODO: Implement ML model prediction here
            # For now, using a simple rule-based approach
            vix = market_data["vix"]
            realized_vol = market_data["realized_vol"]
            skew = market_data["skew"]
            
            if vix < 15:
                regime = VolatilityRegime.CALM
            elif vix > 30:
                regime = VolatilityRegime.EXPLOSIVE
            elif abs(vix - realized_vol) > 5:
                regime = VolatilityRegime.TRENDING
            else:
                regime = VolatilityRegime.MEAN_REVERTING
                
            return regime
            
        except Exception as e:
            logger.error(f"Error classifying regime: {str(e)}")
            raise
    
    async def store_market_data(self, db_session, market_data: Dict, regime: VolatilityRegime):
        """Store market data and regime classification in the database."""
        try:
            db_market_data = MarketData(
                **market_data,
                regime=regime,
                regime_probability=0.8  # TODO: Implement actual probability calculation
            )
            
            db_session.add(db_market_data)
            await db_session.commit()
            await db_session.refresh(db_market_data)
            
            return db_market_data
            
        except Exception as e:
            logger.error(f"Error storing market data: {str(e)}")
            await db_session.rollback()
            raise 