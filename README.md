# Forex Watchlist & Alerts

Track forex currency pairs and get notified when rates hit your targets. Uses real-time data from TradingView (OANDA broker).

**No API key required!**

## Features

- Real-time forex rates from TradingView (OANDA data)
- Live TradingView charts embedded in the app
- Set price alerts (above/below target)
- Desktop notifications when alerts trigger (CLI)
- Web interface with Streamlit
- 30+ forex pairs including Gold & Silver
- Technical analysis signals (Buy/Sell/Hold)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/pkawai/forex_watchlist.git
cd forex_watchlist
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Web App

Run the Streamlit web interface:

```bash
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

## CLI Usage

### Add a currency pair to your watchlist

```bash
python main.py add EUR USD
python main.py add GBP JPY
```

### Set price alerts

```bash
python main.py alert EUR USD above 1.10 "Sell signal"
python main.py alert EUR USD below 1.05 "Buy opportunity"
```

### View your watchlist

```bash
python main.py list
```

### Check current rates

```bash
python main.py rates
```

### Check alerts (and receive notifications)

```bash
python main.py check
```

### Remove a currency pair

```bash
python main.py remove EUR USD
```

## Available Pairs

Major pairs: EUR/USD, GBP/USD, USD/JPY, USD/CHF, AUD/USD, USD/CAD, NZD/USD

Cross pairs: EUR/GBP, EUR/JPY, GBP/JPY, EUR/CHF, AUD/JPY, and more...

Commodities: XAU/USD (Gold), XAG/USD (Silver)

## Project Structure

```
forex_watchlist/
├── app.py            # Streamlit web interface with TradingView charts
├── main.py           # CLI interface (Click-based)
├── rates.py          # Fetch rates from TradingView (OANDA)
├── watchlist.py      # Manage watched pairs and alerts
├── alerts.py         # Alert logic and desktop notifications
├── storage.py        # JSON file I/O
├── requirements.txt  # Python dependencies
└── data/
    └── watchlist.json  # Persistent storage
```

## Data Source

This app uses:
- **TradingView** widgets for live charts
- **tradingview-ta** library for real-time prices (via OANDA)
- No API key needed
- Updates in real-time

## Dependencies

- **streamlit** - Web interface
- **tradingview-ta** - Real-time forex data from TradingView
- **click** - CLI framework
- **requests** - HTTP client
- **plyer** - Desktop notifications

## Screenshots

The web app includes:
- Live ticker tape with major pairs
- Interactive TradingView charts
- Price alerts with notifications
- Technical analysis signals
