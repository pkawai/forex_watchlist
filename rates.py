"""
Rates module for Forex Watchlist application.
Handles fetching live forex rates from ExchangeRate-API.
Updates every few minutes with 1500 free requests/month.
"""

import os
import requests
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

# Get API key from environment variable or .env file
API_KEY = os.environ.get("EXCHANGERATE_API_KEY", "")
BASE_URL = "https://v6.exchangerate-api.com/v6"


def get_rate(base, quote):
    """
    Fetch exchange rate for a single currency pair.

    Args:
        base (str): Base currency code (e.g., 'EUR')
        quote (str): Quote currency code (e.g., 'USD')

    Returns:
        float: Exchange rate, or None if failed
    """
    if not API_KEY:
        print("Error: EXCHANGERATE_API_KEY not set")
        return None

    try:
        url = f"{BASE_URL}/{API_KEY}/pair/{base.upper()}/{quote.upper()}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get('result') == 'success':
            return data.get('conversion_rate')
        else:
            print(f"API Error: {data.get('error-type', 'Unknown error')}")
            return None
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
    if not API_KEY:
        print("Error: EXCHANGERATE_API_KEY not set")
        return None

    try:
        url = f"{BASE_URL}/{API_KEY}/latest/{base.upper()}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get('result') == 'success':
            return data.get('conversion_rates')
        else:
            print(f"API Error: {data.get('error-type', 'Unknown error')}")
            return None
    except requests.RequestException as e:
        print(f"Error fetching rates: {e}")
        return None


def get_available_currencies():
    """
    Get list of available currencies from the API.

    Returns:
        dict: Dictionary of currency codes to names, or None if failed
    """
    if not API_KEY:
        print("Error: EXCHANGERATE_API_KEY not set")
        return None

    try:
        url = f"{BASE_URL}/{API_KEY}/codes"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get('result') == 'success':
            # Convert list of [code, name] to dict
            return {code: name for code, name in data.get('supported_codes', [])}
        else:
            print(f"API Error: {data.get('error-type', 'Unknown error')}")
            return None
    except requests.RequestException as e:
        print(f"Error fetching currencies: {e}")
        return None
