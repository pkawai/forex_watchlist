"""
Portfolio module for Forex Watchlist.
Tracks open positions and calculates overall profit/loss.
"""

import json
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
PORTFOLIO_FILE = os.path.join(DATA_DIR, 'portfolio.json')


def load_portfolio():
    """Load portfolio from JSON file."""
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(PORTFOLIO_FILE):
        default = {"positions": []}
        save_portfolio(default)
        return default

    try:
        with open(PORTFOLIO_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {"positions": []}


def save_portfolio(portfolio):
    """Save portfolio to JSON file."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(PORTFOLIO_FILE, 'w') as f:
        json.dump(portfolio, f, indent=2)


def open_position(pair, direction, entry_price, lot_size, stop_loss=None, take_profit=None, notes=""):
    """
    Open a new position in the portfolio.

    Args:
        pair: Currency pair (e.g. "EUR/USD")
        direction: "BUY" or "SELL"
        entry_price: Entry price
        lot_size: Position size in lots
        stop_loss: Optional stop loss price
        take_profit: Optional take profit price
        notes: Optional notes

    Returns:
        dict: The created position
    """
    portfolio = load_portfolio()

    position = {
        "id": int(datetime.now().timestamp() * 1000),
        "pair": pair,
        "direction": direction,
        "entry_price": entry_price,
        "lot_size": lot_size,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "notes": notes,
        "opened_at": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    portfolio["positions"].append(position)
    save_portfolio(portfolio)
    return position


def close_position(position_id):
    """Remove a position from the portfolio."""
    portfolio = load_portfolio()
    portfolio["positions"] = [p for p in portfolio["positions"] if p["id"] != position_id]
    save_portfolio(portfolio)


def get_all_positions():
    """Get all open positions sorted by date (newest first)."""
    portfolio = load_portfolio()
    return sorted(portfolio["positions"], key=lambda p: p["id"], reverse=True)


def calculate_pips(pair, direction, entry_price, current_price):
    """
    Calculate unrealized P/L in pips for a position.

    Args:
        pair: Currency pair
        direction: "BUY" or "SELL"
        entry_price: Entry price
        current_price: Current market price

    Returns:
        float: P/L in pips
    """
    if direction == "BUY":
        pips = (current_price - entry_price)
    else:
        pips = (entry_price - current_price)

    # JPY pairs use 2 decimal pip calculation
    if "JPY" in pair:
        pips *= 100
    else:
        pips *= 10000

    return round(pips, 1)


def get_portfolio_summary(positions_with_pips):
    """
    Calculate portfolio-level stats from positions with their current pips.

    Args:
        positions_with_pips: List of (position, pips) tuples

    Returns:
        dict: Summary stats
    """
    if not positions_with_pips:
        return {
            "total_positions": 0,
            "total_pips": 0,
            "winning": 0,
            "losing": 0,
            "total_lots": 0
        }

    total_pips = sum(pips for _, pips in positions_with_pips)
    winning = sum(1 for _, pips in positions_with_pips if pips > 0)
    losing = sum(1 for _, pips in positions_with_pips if pips <= 0)
    total_lots = sum(p["lot_size"] for p, _ in positions_with_pips)

    return {
        "total_positions": len(positions_with_pips),
        "total_pips": round(total_pips, 1),
        "winning": winning,
        "losing": losing,
        "total_lots": round(total_lots, 2)
    }
