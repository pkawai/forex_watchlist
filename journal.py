"""
Trade Journal module for Forex Watchlist.
Handles logging, storing, and analyzing past trades.
"""

import json
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
JOURNAL_FILE = os.path.join(DATA_DIR, 'journal.json')


def load_journal():
    """Load trade journal from JSON file."""
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(JOURNAL_FILE):
        default = {"trades": []}
        save_journal(default)
        return default

    try:
        with open(JOURNAL_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {"trades": []}


def save_journal(journal):
    """Save trade journal to JSON file."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(JOURNAL_FILE, 'w') as f:
        json.dump(journal, f, indent=2)


def add_trade(pair, direction, entry_price, exit_price, lot_size, notes=""):
    """
    Log a completed trade to the journal.

    Args:
        pair: Currency pair (e.g. "EUR/USD")
        direction: "BUY" or "SELL"
        entry_price: Price at entry
        exit_price: Price at exit
        lot_size: Position size in lots
        notes: Optional trade notes

    Returns:
        dict: The created trade entry
    """
    journal = load_journal()

    # Calculate P/L in pips
    if direction == "BUY":
        pips = (exit_price - entry_price) * 10000
    else:
        pips = (entry_price - exit_price) * 10000

    # Handle JPY pairs (2 decimal places instead of 4)
    if "JPY" in pair:
        if direction == "BUY":
            pips = (exit_price - entry_price) * 100
        else:
            pips = (entry_price - exit_price) * 100

    trade = {
        "id": int(datetime.now().timestamp() * 1000),
        "pair": pair,
        "direction": direction,
        "entry_price": entry_price,
        "exit_price": exit_price,
        "lot_size": lot_size,
        "pips": round(pips, 1),
        "notes": notes,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    journal["trades"].append(trade)
    save_journal(journal)
    return trade


def delete_trade(trade_id):
    """Delete a trade from the journal by ID."""
    journal = load_journal()
    journal["trades"] = [t for t in journal["trades"] if t["id"] != trade_id]
    save_journal(journal)


def get_all_trades():
    """Get all trades sorted by date (newest first)."""
    journal = load_journal()
    return sorted(journal["trades"], key=lambda t: t["id"], reverse=True)


def get_journal_stats():
    """
    Calculate overall trading statistics.

    Returns:
        dict: Stats including total trades, win rate, total pips, etc.
    """
    trades = get_all_trades()

    if not trades:
        return {
            "total_trades": 0,
            "wins": 0,
            "losses": 0,
            "win_rate": 0,
            "total_pips": 0,
            "avg_pips": 0,
            "best_trade": 0,
            "worst_trade": 0,
            "most_traded_pair": "-"
        }

    wins = [t for t in trades if t["pips"] > 0]
    losses = [t for t in trades if t["pips"] <= 0]
    total_pips = sum(t["pips"] for t in trades)
    pips_list = [t["pips"] for t in trades]

    # Most traded pair
    pair_counts = {}
    for t in trades:
        pair_counts[t["pair"]] = pair_counts.get(t["pair"], 0) + 1
    most_traded = max(pair_counts, key=pair_counts.get)

    return {
        "total_trades": len(trades),
        "wins": len(wins),
        "losses": len(losses),
        "win_rate": round(len(wins) / len(trades) * 100, 1),
        "total_pips": round(total_pips, 1),
        "avg_pips": round(total_pips / len(trades), 1),
        "best_trade": round(max(pips_list), 1),
        "worst_trade": round(min(pips_list), 1),
        "most_traded_pair": most_traded
    }
