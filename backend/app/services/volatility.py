import numpy as np
import pandas as pd
from typing import Dict, List
import logging
from scipy.stats import norm
import py_vollib.black_scholes as bs
import py_vollib.black_scholes.implied_volatility as bs_iv

logger = logging.getLogger(__name__)

def calculate_realized_volatility(prices: pd.Series, window: int = 30) -> float:
    """Calculate realized volatility from historical prices."""
    try:
        # Calculate log returns
        returns = np.log(prices / prices.shift(1)).dropna()
        
        # Annualize volatility (sqrt of 252 trading days)
        realized_vol = returns.std() * np.sqrt(252)
        
        return realized_vol
        
    except Exception as e:
        logger.error(f"Error calculating realized volatility: {str(e)}")
        raise

def calculate_implied_volatility(ticker, expiration_date: str) -> Dict[str, float]:
    """Calculate implied volatility metrics including ATM IV and skew."""
    try:
        # Get options chain for the expiration date
        options = ticker.option_chain(expiration_date)
        
        # Get current stock price
        spot = ticker.history(period="1d")["Close"].iloc[-1]
        
        # Find ATM options (closest to current price)
        calls = options.calls
        puts = options.puts
        
        # Calculate time to expiration in years
        today = pd.Timestamp.now()
        expiry = pd.Timestamp(expiration_date)
        t = (expiry - today).days / 365
        
        # Find ATM strike
        atm_strike = calls["strike"].iloc[(calls["strike"] - spot).abs().argsort()[0]]
        
        # Calculate ATM IV
        atm_call = calls[calls["strike"] == atm_strike].iloc[0]
        atm_iv = bs_iv.implied_volatility(
            price=atm_call["lastPrice"],
            S=spot,
            K=atm_strike,
            t=t,
            r=0.02,  # Risk-free rate (approximate)
            flag='c'
        )
        
        # Calculate volatility skew
        otm_puts = puts[puts["strike"] < atm_strike]
        otm_calls = calls[calls["strike"] > atm_strike]
        
        # Calculate 25-delta skew
        put_25d = otm_puts.iloc[len(otm_puts)//4]
        call_25d = otm_calls.iloc[len(otm_calls)//4]
        
        put_25d_iv = bs_iv.implied_volatility(
            price=put_25d["lastPrice"],
            S=spot,
            K=put_25d["strike"],
            t=t,
            r=0.02,
            flag='p'
        )
        
        call_25d_iv = bs_iv.implied_volatility(
            price=call_25d["lastPrice"],
            S=spot,
            K=call_25d["strike"],
            t=t,
            r=0.02,
            flag='c'
        )
        
        # Calculate skew as difference between 25-delta put and call IV
        skew = put_25d_iv - call_25d_iv
        
        return {
            "atm": atm_iv,
            "skew": skew,
            "put_25d": put_25d_iv,
            "call_25d": call_25d_iv
        }
        
    except Exception as e:
        logger.error(f"Error calculating implied volatility: {str(e)}")
        raise

def calculate_forward_volatility(historical_vol: float, implied_vol: float, vix: float) -> float:
    """Calculate forward-looking volatility estimate."""
    try:
        # Combine historical and implied vol with VIX
        # Using a simple weighted average for demonstration
        weights = [0.3, 0.4, 0.3]  # Historical, Implied, VIX
        forward_vol = (
            weights[0] * historical_vol +
            weights[1] * implied_vol +
            weights[2] * vix/100  # VIX is quoted in percentage points
        )
        
        return forward_vol
        
    except Exception as e:
        logger.error(f"Error calculating forward volatility: {str(e)}")
        raise 