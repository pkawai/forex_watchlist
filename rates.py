"""
Rates module for Forex Watchlist application.
Fetches real-time forex rates from TradingView (OANDA data).
Falls back to Frankfurter API if TradingView is rate limited.
No API key required.
"""

import time
import requests
from tradingview_ta import TA_Handler, Interval

# Cache for rate limiting (stores last fetch time and result)
_rate_cache = {}
CACHE_DURATION = 30  # seconds

# Track if TradingView is rate limited
_tradingview_blocked_until = 0
BLOCK_DURATION = 300  # 5 minutes cooldown when rate limited

# Common forex pairs available on OANDA via TradingView
FOREX_PAIRS = {
    "EUR/USD": ("EURUSD", "Euro / US Dollar"),
    "GBP/USD": ("GBPUSD", "British Pound / US Dollar"),
    "USD/JPY": ("USDJPY", "US Dollar / Japanese Yen"),
    "USD/CHF": ("USDCHF", "US Dollar / Swiss Franc"),
    "AUD/USD": ("AUDUSD", "Australian Dollar / US Dollar"),
    "USD/CAD": ("USDCAD", "US Dollar / Canadian Dollar"),
    "NZD/USD": ("NZDUSD", "New Zealand Dollar / US Dollar"),
    "EUR/GBP": ("EURGBP", "Euro / British Pound"),
    "EUR/JPY": ("EURJPY", "Euro / Japanese Yen"),
    "GBP/JPY": ("GBPJPY", "British Pound / Japanese Yen"),
    "EUR/CHF": ("EURCHF", "Euro / Swiss Franc"),
    "AUD/JPY": ("AUDJPY", "Australian Dollar / Japanese Yen"),
    "EUR/AUD": ("EURAUD", "Euro / Australian Dollar"),
    "GBP/AUD": ("GBPAUD", "British Pound / Australian Dollar"),
    "GBP/CAD": ("GBPCAD", "British Pound / Canadian Dollar"),
    "EUR/CAD": ("EURCAD", "Euro / Canadian Dollar"),
    "AUD/CAD": ("AUDCAD", "Australian Dollar / Canadian Dollar"),
    "AUD/NZD": ("AUDNZD", "Australian Dollar / New Zealand Dollar"),
    "NZD/JPY": ("NZDJPY", "New Zealand Dollar / Japanese Yen"),
    "CHF/JPY": ("CHFJPY", "Swiss Franc / Japanese Yen"),
    "CAD/JPY": ("CADJPY", "Canadian Dollar / Japanese Yen"),
    "CAD/CHF": ("CADCHF", "Canadian Dollar / Swiss Franc"),
    "EUR/NZD": ("EURNZD", "Euro / New Zealand Dollar"),
    "GBP/CHF": ("GBPCHF", "British Pound / Swiss Franc"),
    "GBP/NZD": ("GBPNZD", "British Pound / New Zealand Dollar"),
    "USD/SGD": ("USDSGD", "US Dollar / Singapore Dollar"),
    "USD/HKD": ("USDHKD", "US Dollar / Hong Kong Dollar"),
    "USD/MXN": ("USDMXN", "US Dollar / Mexican Peso"),
    "USD/ZAR": ("USDZAR", "US Dollar / South African Rand"),
    "XAU/USD": ("XAUUSD", "Gold / US Dollar"),
    "XAG/USD": ("XAGUSD", "Silver / US Dollar"),
}


def get_symbol(base, quote):
    """Convert base/quote to TradingView symbol."""
    pair_key = f"{base.upper()}/{quote.upper()}"
    if pair_key in FOREX_PAIRS:
        return FOREX_PAIRS[pair_key][0]
    # Try reverse
    reverse_key = f"{quote.upper()}/{base.upper()}"
    if reverse_key in FOREX_PAIRS:
        return FOREX_PAIRS[reverse_key][0]
    return None


def _get_rate_frankfurter(base, quote):
    """Fallback: fetch rate from Frankfurter API (ECB data)."""
    try:
        url = f"https://api.frankfurter.app/latest?from={base.upper()}&to={quote.upper()}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data['rates'].get(quote.upper())
    except Exception as e:
        print(f"Frankfurter fallback error: {e}")
        return None


def _get_rate_tradingview(base, quote):
    """Fetch rate from TradingView."""
    global _tradingview_blocked_until

    # Check if we're in cooldown
    if time.time() < _tradingview_blocked_until:
        return None

    symbol = get_symbol(base, quote)
    if not symbol:
        return None

    try:
        handler = TA_Handler(
            symbol=symbol,
            screener="forex",
            exchange="OANDA",
            interval=Interval.INTERVAL_1_MINUTE
        )
        analysis = handler.get_analysis()
        return analysis.indicators.get("close")
    except Exception as e:
        if "429" in str(e):
            # Rate limited - set cooldown
            _tradingview_blocked_until = time.time() + BLOCK_DURATION
            print(f"TradingView rate limited. Using fallback for {BLOCK_DURATION}s")
        return None


def get_rate(base, quote):
    """
    Fetch exchange rate - tries TradingView first, falls back to Frankfurter.
    Results are cached for 30 seconds to avoid rate limiting.

    Args:
        base (str): Base currency code (e.g., 'EUR')
        quote (str): Quote currency code (e.g., 'USD')

    Returns:
        float: Exchange rate, or None if failed
    """
    cache_key = f"{base}/{quote}"
    now = time.time()

    # Check cache first
    if cache_key in _rate_cache:
        cached_time, cached_rate = _rate_cache[cache_key]
        if now - cached_time < CACHE_DURATION:
            return cached_rate

    # Try TradingView first
    rate = _get_rate_tradingview(base, quote)

    # Fallback to Frankfurter if TradingView failed
    if rate is None:
        rate = _get_rate_frankfurter(base, quote)

    # Update cache if we got a rate
    if rate is not None:
        _rate_cache[cache_key] = (now, rate)
        return rate

    # Return stale cache if available
    if cache_key in _rate_cache:
        return _rate_cache[cache_key][1]

    return None


def get_rate_with_details(base, quote):
    """
    Fetch rate with additional details (open, high, low, change).
    Falls back to basic rate if TradingView is unavailable.

    Returns:
        dict: Rate details or None if failed
    """
    global _tradingview_blocked_until

    cache_key = f"{base}/{quote}_details"
    now = time.time()

    # Check cache
    if cache_key in _rate_cache:
        cached_time, cached_data = _rate_cache[cache_key]
        if now - cached_time < CACHE_DURATION:
            return cached_data

    symbol = get_symbol(base, quote)

    # Try TradingView if not rate limited
    if symbol and time.time() >= _tradingview_blocked_until:
        try:
            handler = TA_Handler(
                symbol=symbol,
                screener="forex",
                exchange="OANDA",
                interval=Interval.INTERVAL_1_MINUTE
            )
            analysis = handler.get_analysis()
            indicators = analysis.indicators

            result = {
                "close": indicators.get("close"),
                "open": indicators.get("open"),
                "high": indicators.get("high"),
                "low": indicators.get("low"),
                "change": indicators.get("change"),
                "change_pct": indicators.get("change") / indicators.get("open") * 100 if indicators.get("open") else 0,
                "recommendation": analysis.summary.get("RECOMMENDATION", "NEUTRAL")
            }

            _rate_cache[cache_key] = (now, result)
            return result
        except Exception as e:
            if "429" in str(e):
                _tradingview_blocked_until = time.time() + BLOCK_DURATION

    # Fallback: just get the rate from Frankfurter
    rate = _get_rate_frankfurter(base, quote)
    if rate:
        result = {
            "close": rate,
            "open": rate,
            "high": rate,
            "low": rate,
            "change": 0,
            "change_pct": 0,
            "recommendation": "N/A"
        }
        _rate_cache[cache_key] = (now, result)
        return result

    # Return stale cache if available
    if cache_key in _rate_cache:
        return _rate_cache[cache_key][1]

    return None


def get_available_currencies():
    """
    Get available forex pairs.

    Returns:
        dict: Available pairs with descriptions
    """
    return FOREX_PAIRS


def get_tradingview_symbol(base, quote):
    """Get the full TradingView symbol for embedding widgets."""
    symbol = get_symbol(base, quote)
    if symbol:
        return f"OANDA:{symbol}"
    return None
