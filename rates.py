"""
Rates module for Forex Watchlist application.
Handles fetching live forex rates from frankfurter.app API.
"""

import requests

BASE_URL = "https://api.frankfurter.app"


def get_rate(base, quote):
    """
    Fetch exchange rate for a single currency pair.

    Args:
        base (str): Base currency code (e.g., 'EUR')
        quote (str): Quote currency code (e.g., 'USD')

    Returns:
        float: Exchange rate, or None if failed
    """
    try:
        url = f"{BASE_URL}/latest?from={base.upper()}&to={quote.upper()}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data['rates'].get(quote.upper())
    except requests.RequestException as e:
        print(f"Error fetching rate: {e}")
        return None


def get_all_rates(base):
    """
    Fetch all exchange rates for a base currency.

    Args:
        base (str): Base currency code (e.g., 'EUR')

    Returns:
        dict: Dictionary of currency codes to rates, or None if failed
    """
    try:
        url = f"{BASE_URL}/latest?from={base.upper()}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data['rates']
    except requests.RequestException as e:
        print(f"Error fetching rates: {e}")
        return None


def get_available_currencies():
    """
    Get list of available currencies from the API.

    Returns:
        dict: Dictionary of currency codes to names, or None if failed
    """
    try:
        url = f"{BASE_URL}/currencies"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching currencies: {e}")
        return None
