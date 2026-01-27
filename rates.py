"""
Rates module for Forex Watchlist application.
Fetches real-time forex rates from TradingView (OANDA data).
No API key required.
"""

from tradingview_ta import TA_Handler, Interval

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


def get_rate(base, quote):
    """
    Fetch real-time exchange rate from TradingView (OANDA).

    Args:
        base (str): Base currency code (e.g., 'EUR')
        quote (str): Quote currency code (e.g., 'USD')

    Returns:
        float: Exchange rate, or None if failed
    """
    symbol = get_symbol(base, quote)
    if not symbol:
        print(f"Pair {base}/{quote} not available")
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
        print(f"Error fetching rate for {base}/{quote}: {e}")
        return None


def get_rate_with_details(base, quote):
    """
    Fetch rate with additional details (open, high, low, change).

    Returns:
        dict: Rate details or None if failed
    """
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
        indicators = analysis.indicators

        return {
            "close": indicators.get("close"),
            "open": indicators.get("open"),
            "high": indicators.get("high"),
            "low": indicators.get("low"),
            "change": indicators.get("change"),
            "change_pct": indicators.get("change") / indicators.get("open") * 100 if indicators.get("open") else 0,
            "recommendation": analysis.summary.get("RECOMMENDATION", "NEUTRAL")
        }
    except Exception as e:
        print(f"Error: {e}")
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
