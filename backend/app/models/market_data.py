from sqlalchemy import Column, Integer, Float, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.base_class import Base

class VolatilityRegime(str, enum.Enum):
    CALM = "calm"
    TRENDING = "trending"
    MEAN_REVERTING = "mean_reverting"
    EXPLOSIVE = "explosive"

class MarketData(Base):
    __tablename__ = "market_data"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    symbol = Column(String, nullable=False, index=True)
    
    # Price data
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    
    # Volatility metrics
    vix = Column(Float)
    realized_vol = Column(Float)
    implied_vol_atm = Column(Float)
    vvix = Column(Float)
    skew = Column(Float)
    
    # Regime classification
    regime = Column(Enum(VolatilityRegime))
    regime_probability = Column(Float)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<MarketData(symbol={self.symbol}, timestamp={self.timestamp}, regime={self.regime})>"

class StrategyRecommendation(Base):
    __tablename__ = "strategy_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    market_data_id = Column(Integer, ForeignKey("market_data.id"))
    
    # Strategy details
    strategy_name = Column(String, nullable=False)
    strategy_type = Column(String, nullable=False)
    entry_price = Column(Float)
    target_price = Column(Float)
    stop_loss = Column(Float)
    
    # Greeks
    delta = Column(Float)
    gamma = Column(Float)
    vega = Column(Float)
    theta = Column(Float)
    
    # Risk metrics
    max_loss = Column(Float)
    max_profit = Column(Float)
    probability_of_profit = Column(Float)
    sharpe_ratio = Column(Float)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    market_data = relationship("MarketData", backref="strategy_recommendations")

    def __repr__(self):
        return f"<StrategyRecommendation(strategy={self.strategy_name}, timestamp={self.timestamp})>" 