# Forex Watchlist & Alerts

Track forex currency pairs and get notified when rates hit your targets. A free alternative to TradingView's paid alert feature.

**Live Demo:** [Streamlit Cloud](https://forexwatchlist.streamlit.app) *(after deployment)*

## Features

- Track multiple currency pairs (EUR/USD, GBP/JPY, etc.)
- Set price alerts (above/below target)
- Fetch live rates from frankfurter.app API (free, no API key needed)
- Desktop notifications when alerts trigger (CLI)
- Web interface with Streamlit
- Persistent storage in JSON

## Installation

1. Clone or download this repository
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

### Remove an alert

```bash
python main.py remove-alert EUR USD 0
```

### List available currencies

```bash
python main.py currencies
```

## Project Structure

```
forex_watchlist/
├── app.py            # Streamlit web interface
├── main.py           # CLI interface (Click-based)
├── rates.py          # Fetch rates from frankfurter.app API
├── watchlist.py      # Manage watched pairs and alerts
├── alerts.py         # Alert logic and desktop notifications
├── storage.py        # JSON file I/O
├── requirements.txt  # Python dependencies
└── data/
    └── watchlist.json  # Persistent storage
```

## API

This app uses the [Frankfurter API](https://www.frankfurter.app/), which provides free foreign exchange rates from the European Central Bank. No API key required.

## Dependencies

- **streamlit** - Web interface
- **click** - CLI framework
- **requests** - HTTP client for API calls
- **plyer** - Cross-platform notifications (Windows only; macOS/Linux use native tools)

## Tips

- Run `python main.py check` periodically (e.g., via cron) to monitor your alerts
- Alerts are not automatically removed when triggered - remove them manually with `remove-alert`
- The app stores data in `data/watchlist.json`
