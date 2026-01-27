"""
Forex Watchlist - Streamlit Web App

A web application for tracking forex currency pairs and monitoring
price alerts. Uses TradingView data from OANDA broker.
No API key required.
"""

import streamlit as st
import streamlit.components.v1 as components
from storage import load_watchlist, save_watchlist
from rates import get_rate, get_rate_with_details, get_available_currencies, get_tradingview_symbol, FOREX_PAIRS
from watchlist import add_pair, remove_pair, add_alert, remove_alert, list_pairs
from alerts import check_alert_triggered

# Page config
st.set_page_config(
    page_title="Forex Watchlist",
    page_icon="💱",
    layout="wide"
)

st.title("💱 Forex Watchlist & Alerts")
st.caption("Real-time forex data from TradingView (OANDA) - No API key required")


def tradingview_widget(symbol, height=400):
    """Embed TradingView mini chart widget."""
    widget_html = f'''
    <!-- TradingView Widget BEGIN -->
    <div class="tradingview-widget-container">
      <div class="tradingview-widget-container__widget"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-mini-symbol-overview.js" async>
      {{
        "symbol": "{symbol}",
        "width": "100%",
        "height": "{height}",
        "locale": "en",
        "dateRange": "1D",
        "colorTheme": "light",
        "isTransparent": false,
        "autosize": true,
        "largeChartUrl": ""
      }}
      </script>
    </div>
    <!-- TradingView Widget END -->
    '''
    components.html(widget_html, height=height + 20)


def tradingview_ticker():
    """Embed TradingView ticker tape widget."""
    widget_html = '''
    <!-- TradingView Widget BEGIN -->
    <div class="tradingview-widget-container">
      <div class="tradingview-widget-container__widget"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
      {
        "symbols": [
          {"proName": "OANDA:EURUSD", "title": "EUR/USD"},
          {"proName": "OANDA:GBPUSD", "title": "GBP/USD"},
          {"proName": "OANDA:USDJPY", "title": "USD/JPY"},
          {"proName": "OANDA:XAUUSD", "title": "Gold"},
          {"proName": "OANDA:GBPJPY", "title": "GBP/JPY"},
          {"proName": "OANDA:AUDUSD", "title": "AUD/USD"}
        ],
        "showSymbolLogo": true,
        "isTransparent": false,
        "displayMode": "adaptive",
        "colorTheme": "light",
        "locale": "en"
      }
      </script>
    </div>
    <!-- TradingView Widget END -->
    '''
    components.html(widget_html, height=80)


# Show ticker tape at top
tradingview_ticker()

# Sidebar - Add new pair
st.sidebar.header("Add Currency Pair")

# Get available pairs
available_pairs = list(FOREX_PAIRS.keys())
selected_pair_to_add = st.sidebar.selectbox(
    "Select Pair",
    available_pairs,
    format_func=lambda x: f"{x} - {FOREX_PAIRS[x][1]}"
)

if st.sidebar.button("Add to Watchlist", type="primary", use_container_width=True):
    base, quote = selected_pair_to_add.split("/")
    if add_pair(base, quote):
        st.sidebar.success(f"Added {selected_pair_to_add}")
        st.rerun()
    else:
        st.sidebar.warning(f"{selected_pair_to_add} already in watchlist")

# Sidebar - Set alert
st.sidebar.divider()
st.sidebar.header("Set Alert")

pairs = list_pairs()
if pairs:
    pair_options = [f"{p['base']}/{p['quote']}" for p in pairs]
    selected_pair = st.sidebar.selectbox("Currency Pair", pair_options)

    if selected_pair:
        base_alert, quote_alert = selected_pair.split("/")

        # Get current rate for reference
        current = get_rate(base_alert, quote_alert)
        if current:
            st.sidebar.caption(f"Current rate: {current:.5f}")

        alert_type = st.sidebar.radio("Alert Type", ["above", "below"], horizontal=True)
        target = st.sidebar.number_input(
            "Target Price",
            min_value=0.00001,
            value=current if current else 1.0,
            step=0.00001,
            format="%.5f"
        )
        note = st.sidebar.text_input("Note (optional)")

        if st.sidebar.button("Set Alert", use_container_width=True):
            if add_alert(base_alert, quote_alert, alert_type, target, note):
                st.sidebar.success(f"Alert set: {selected_pair} {alert_type} {target:.5f}")
                st.rerun()
else:
    st.sidebar.info("Add a currency pair first")

# Main content
tab1, tab2, tab3 = st.tabs(["📊 Watchlist & Charts", "🔔 Check Alerts", "💰 Live Rates"])

with tab1:
    st.header("Your Watchlist")

    if not pairs:
        st.info("Your watchlist is empty. Add currency pairs using the sidebar.")

        # Show example chart
        st.subheader("Example: EUR/USD")
        tradingview_widget("OANDA:EURUSD", 350)
    else:
        for pair in pairs:
            pair_name = f"{pair['base']}/{pair['quote']}"
            tv_symbol = get_tradingview_symbol(pair['base'], pair['quote'])

            with st.expander(f"**{pair_name}**", expanded=True):
                col1, col2 = st.columns([2, 1])

                with col1:
                    # Show TradingView chart
                    if tv_symbol:
                        tradingview_widget(tv_symbol, 300)
                    else:
                        st.warning("Chart not available for this pair")

                with col2:
                    # Show rate details
                    details = get_rate_with_details(pair['base'], pair['quote'])
                    if details:
                        st.metric(
                            "Current Price",
                            f"{details['close']:.5f}",
                            delta=f"{details['change_pct']:.2f}%" if details.get('change_pct') else None
                        )
                        st.caption(f"High: {details['high']:.5f} | Low: {details['low']:.5f}")
                        st.caption(f"Signal: {details['recommendation']}")
                    else:
                        st.warning("Could not fetch rate")

                    # Show alerts
                    if pair['alerts']:
                        st.subheader("Alerts")
                        for i, alert in enumerate(pair['alerts']):
                            icon = "📈" if alert['type'] == 'above' else "📉"
                            note_text = f" - {alert['note']}" if alert.get('note') else ""
                            col_a, col_b = st.columns([3, 1])
                            with col_a:
                                st.write(f"{icon} {alert['type']} **{alert['target']:.5f}**{note_text}")
                            with col_b:
                                if st.button("🗑️", key=f"del_alert_{pair_name}_{i}"):
                                    remove_alert(pair['base'], pair['quote'], i)
                                    st.rerun()
                    else:
                        st.caption("No alerts set")

                    st.divider()
                    if st.button("Remove Pair", key=f"del_{pair_name}", type="secondary"):
                        remove_pair(pair['base'], pair['quote'])
                        st.rerun()

with tab2:
    st.header("Check Alerts")

    if not pairs:
        st.info("Add currency pairs and set alerts first.")
    else:
        if st.button("🔔 Check All Alerts", type="primary"):
            triggered = []
            checked = 0

            with st.spinner("Checking alerts..."):
                for pair in pairs:
                    if not pair['alerts']:
                        continue

                    rate = get_rate(pair['base'], pair['quote'])
                    if rate is None:
                        continue

                    checked += len(pair['alerts'])

                    for alert in pair['alerts']:
                        if check_alert_triggered(alert, rate):
                            triggered.append({
                                'pair': f"{pair['base']}/{pair['quote']}",
                                'type': alert['type'],
                                'target': alert['target'],
                                'rate': rate,
                                'note': alert.get('note', '')
                            })

            if triggered:
                st.success(f"🚨 {len(triggered)} alert(s) triggered!")
                for t in triggered:
                    direction = "risen above" if t['type'] == 'above' else "fallen below"
                    st.warning(f"**{t['pair']}** has {direction} {t['target']:.5f} (Current: {t['rate']:.5f})")
                    if t['note']:
                        st.caption(f"Note: {t['note']}")
            else:
                st.info(f"No alerts triggered. Checked {checked} alert(s).")

        # Show alert summary
        st.subheader("Alert Summary")
        alert_count = sum(len(p['alerts']) for p in pairs)
        st.write(f"Total alerts set: **{alert_count}**")

        for pair in pairs:
            if pair['alerts']:
                st.write(f"**{pair['base']}/{pair['quote']}**: {len(pair['alerts'])} alert(s)")
                for alert in pair['alerts']:
                    icon = "📈" if alert['type'] == 'above' else "📉"
                    st.caption(f"  {icon} {alert['type']} {alert['target']:.5f}")

with tab3:
    st.header("Live Exchange Rates")

    if not pairs:
        st.info("Add currency pairs to see their rates.")
    else:
        # Create grid of rate cards
        cols = st.columns(min(len(pairs), 3))

        for i, pair in enumerate(pairs):
            with cols[i % 3]:
                details = get_rate_with_details(pair['base'], pair['quote'])
                if details:
                    delta_color = "normal"
                    st.metric(
                        label=f"{pair['base']}/{pair['quote']}",
                        value=f"{details['close']:.5f}",
                        delta=f"{details['change_pct']:.3f}%" if details.get('change_pct') else None
                    )
                    st.caption(f"H: {details['high']:.5f} | L: {details['low']:.5f}")
                else:
                    st.error(f"{pair['base']}/{pair['quote']}: Error")

        if st.button("🔄 Refresh Rates"):
            st.rerun()

# Footer
st.divider()
col1, col2 = st.columns(2)
with col1:
    st.caption("Real-time data from [TradingView](https://tradingview.com) via OANDA")
with col2:
    st.caption("No API key required")
