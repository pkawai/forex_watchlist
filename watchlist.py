"""
Watchlist module for Forex Watchlist application.
Manages watched currency pairs and alert configurations.
"""

from datetime import datetime
from storage import load_watchlist, save_watchlist


def find_pair(watchlist, base, quote):
    """
    Find a currency pair in the watchlist.

    Args:
        watchlist (dict): Watchlist data
        base (str): Base currency code
        quote (str): Quote currency code

    Returns:
        tuple: (index, pair_dict) or (None, None) if not found
    """
    base = base.upper()
    quote = quote.upper()
    for i, pair in enumerate(watchlist['pairs']):
        if pair['base'] == base and pair['quote'] == quote:
            return i, pair
    return None, None


def add_pair(base, quote):
    """
    Add a currency pair to the watchlist.

    Args:
        base (str): Base currency code
        quote (str): Quote currency code

    Returns:
        bool: True if added, False if already exists
    """
    watchlist = load_watchlist()
    base = base.upper()
    quote = quote.upper()

    # Check if pair already exists
    _, existing = find_pair(watchlist, base, quote)
    if existing:
        return False

    # Add new pair
    new_pair = {
        "base": base,
        "quote": quote,
        "alerts": [],
        "last_rate": None,
        "last_updated": None
    }
    watchlist['pairs'].append(new_pair)
    save_watchlist(watchlist)
    return True


def remove_pair(base, quote):
    """
    Remove a currency pair from the watchlist.

    Args:
        base (str): Base currency code
        quote (str): Quote currency code

    Returns:
        bool: True if removed, False if not found
    """
    watchlist = load_watchlist()
    idx, _ = find_pair(watchlist, base, quote)

    if idx is None:
        return False

    watchlist['pairs'].pop(idx)
    save_watchlist(watchlist)
    return True


def add_alert(base, quote, alert_type, target, note=""):
    """
    Add an alert to a currency pair.

    Args:
        base (str): Base currency code
        quote (str): Quote currency code
        alert_type (str): 'above' or 'below'
        target (float): Target price
        note (str): Optional note for the alert

    Returns:
        bool: True if added, False if pair not found
    """
    watchlist = load_watchlist()
    idx, pair = find_pair(watchlist, base, quote)

    if pair is None:
        return False

    alert = {
        "type": alert_type.lower(),
        "target": float(target),
        "note": note
    }
    watchlist['pairs'][idx]['alerts'].append(alert)
    save_watchlist(watchlist)
    return True


def remove_alert(base, quote, alert_index):
    """
    Remove an alert from a currency pair by index.

    Args:
        base (str): Base currency code
        quote (str): Quote currency code
        alert_index (int): Index of alert to remove

    Returns:
        bool: True if removed, False if not found
    """
    watchlist = load_watchlist()
    idx, pair = find_pair(watchlist, base, quote)

    if pair is None:
        return False

    if alert_index < 0 or alert_index >= len(pair['alerts']):
        return False

    watchlist['pairs'][idx]['alerts'].pop(alert_index)
    save_watchlist(watchlist)
    return True


def list_pairs():
    """
    Get all watched currency pairs.

    Returns:
        list: List of pair dictionaries
    """
    watchlist = load_watchlist()
    return watchlist['pairs']


def update_rate(base, quote, rate):
    """
    Update the last known rate for a currency pair.

    Args:
        base (str): Base currency code
        quote (str): Quote currency code
        rate (float): Current rate
    """
    watchlist = load_watchlist()
    idx, pair = find_pair(watchlist, base, quote)

    if pair is not None:
        watchlist['pairs'][idx]['last_rate'] = rate
        watchlist['pairs'][idx]['last_updated'] = datetime.now().isoformat()
        save_watchlist(watchlist)
