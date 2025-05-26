from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime
import logging
from dataclasses import dataclass

from app.models.market_data import VolatilityRegime
from app.services.volatility import calculate_forward_volatility

logger = logging.getLogger(__name__)

@dataclass
class StrategyConfig:
    name: str
    type: str
    description: str
    min_volatility: float
    max_volatility: float
    preferred_regime: List[VolatilityRegime]
    risk_profile: str
    typical_duration: str

STRATEGY_CONFIGS = [
    StrategyConfig(
        name="Long Calendar Spread",
        type="calendar_spread",
        description="Buy longer-dated option, sell shorter-dated option at same strike",
        min_volatility=10,
        max_volatility=20,
        preferred_regime=[VolatilityRegime.CALM],
        risk_profile="limited_risk",
        typical_duration="30-60 days"
    ),
    StrategyConfig(
        name="Iron Butterfly",
        type="butterfly",
        description="Combination of bull and bear spreads with same middle strike",
        min_volatility=8,
        max_volatility=15,
        preferred_regime=[VolatilityRegime.CALM, VolatilityRegime.MEAN_REVERTING],
        risk_profile="limited_risk",
        typical_duration="30-45 days"
    ),
    StrategyConfig(
        name="Long Straddle",
        type="straddle",
        description="Buy ATM call and put with same expiration",
        min_volatility=25,
        max_volatility=100,
        preferred_regime=[VolatilityRegime.EXPLOSIVE],
        risk_profile="unlimited_risk",
        typical_duration="30-45 days"
    ),
    StrategyConfig(
        name="Iron Condor",
        type="iron_condor",
        description="Sell OTM put spread and OTM call spread",
        min_volatility=15,
        max_volatility=30,
        preferred_regime=[VolatilityRegime.MEAN_REVERTING],
        risk_profile="limited_risk",
        typical_duration="30-45 days"
    ),
    StrategyConfig(
        name="Ratio Back Spread",
        type="backspread",
        description="Buy OTM options and sell fewer ATM options",
        min_volatility=20,
        max_volatility=40,
        preferred_regime=[VolatilityRegime.TRENDING, VolatilityRegime.EXPLOSIVE],
        risk_profile="unlimited_risk",
        typical_duration="15-30 days"
    )
]

class StrategyService:
    def __init__(self):
        self.strategies = {s.name: s for s in STRATEGY_CONFIGS}
    
    def recommend_strategy(
        self,
        regime: VolatilityRegime,
        market_data: Dict,
        risk_tolerance: str = "moderate"
    ) -> List[Dict]:
        """Recommend options strategies based on current market regime and conditions."""
        try:
            # Calculate forward volatility estimate
            forward_vol = calculate_forward_volatility(
                market_data["realized_vol"],
                market_data["implied_vol_atm"],
                market_data["vix"]
            )
            
            # Filter strategies based on regime and volatility levels
            suitable_strategies = []
            
            for strategy in STRATEGY_CONFIGS:
                if (regime in strategy.preferred_regime and
                    strategy.min_volatility <= forward_vol * 100 <= strategy.max_volatility):
                    
                    # Calculate strategy score based on current conditions
                    score = self._calculate_strategy_score(
                        strategy,
                        regime,
                        forward_vol,
                        market_data["skew"],
                        risk_tolerance
                    )
                    
                    suitable_strategies.append({
                        "name": strategy.name,
                        "type": strategy.type,
                        "description": strategy.description,
                        "score": score,
                        "risk_profile": strategy.risk_profile,
                        "duration": strategy.typical_duration
                    })
            
            # Sort by score
            suitable_strategies.sort(key=lambda x: x["score"], reverse=True)
            
            return suitable_strategies[:3]  # Return top 3 recommendations
            
        except Exception as e:
            logger.error(f"Error recommending strategy: {str(e)}")
            raise
    
    def _calculate_strategy_score(
        self,
        strategy: StrategyConfig,
        regime: VolatilityRegime,
        forward_vol: float,
        skew: float,
        risk_tolerance: str
    ) -> float:
        """Calculate a score for how suitable a strategy is given current conditions."""
        try:
            score = 0.0
            
            # Regime alignment
            if regime in strategy.preferred_regime:
                score += 0.4
            
            # Volatility alignment
            vol_range = strategy.max_volatility - strategy.min_volatility
            vol_mid = (strategy.max_volatility + strategy.min_volatility) / 2
            vol_score = 1 - abs(forward_vol * 100 - vol_mid) / vol_range
            score += 0.3 * max(0, vol_score)
            
            # Risk tolerance alignment
            risk_scores = {
                "conservative": {"limited_risk": 1.0, "unlimited_risk": 0.2},
                "moderate": {"limited_risk": 0.8, "unlimited_risk": 0.6},
                "aggressive": {"limited_risk": 0.6, "unlimited_risk": 1.0}
            }
            score += 0.3 * risk_scores[risk_tolerance][strategy.risk_profile]
            
            return score
            
        except Exception as e:
            logger.error(f"Error calculating strategy score: {str(e)}")
            raise
    
    def calculate_strategy_metrics(
        self,
        strategy_type: str,
        market_data: Dict,
        params: Dict
    ) -> Dict:
        """Calculate risk metrics and expected performance for a strategy."""
        try:
            # TODO: Implement full options pricing and risk calculation
            # For now, returning placeholder metrics
            return {
                "expected_profit": 1000.0,
                "max_loss": -500.0,
                "probability_of_profit": 0.65,
                "break_even_points": [350.0, 370.0],
                "greeks": {
                    "delta": 0.1,
                    "gamma": 0.02,
                    "theta": -0.5,
                    "vega": 0.3
                },
                "risk_metrics": {
                    "sharpe_ratio": 1.5,
                    "sortino_ratio": 2.0,
                    "max_drawdown": 0.15
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating strategy metrics: {str(e)}")
            raise 