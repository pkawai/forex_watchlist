"""
Storage module for Forex Watchlist application.
Handles loading and saving watchlist data to JSON files.
"""

import json
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
WATCHLIST_FILE = os.path.join(DATA_DIR, 'watchlist.json')


def get_default_watchlist():
    """Return empty watchlist structure."""
    return {"pairs": []}


def load_watchlist():
    """
    Load watchlist from JSON file.
    Creates default file if it doesn't exist.

    Returns:
        dict: Watchlist data structure
    """
    # Ensure data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(WATCHLIST_FILE):
        # Create default watchlist
        default = get_default_watchlist()
        save_watchlist(default)
        return default

    try:
        with open(WATCHLIST_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        # If file is corrupted, return default
        return get_default_watchlist()


def save_watchlist(watchlist):
    """
    Save watchlist to JSON file.

    Args:
        watchlist (dict): Watchlist data to save
    """
    # Ensure data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)

    with open(WATCHLIST_FILE, 'w') as f:
        json.dump(watchlist, f, indent=2)
