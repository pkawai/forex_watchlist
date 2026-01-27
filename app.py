"""
Forex Watchlist - Streamlit Web App

A web application for tracking forex currency pairs and monitoring
price alerts. Free alternative to TradingView's paid alert feature.
"""

import os
import streamlit as st
from dotenv import load_dotenv
from storage import load_watchlist, save_watchlist
from rates import get_rate, get_available_currencies, API_KEY
from watchlist import add_pair, remove_pair, add_alert, remove_alert, list_pairs, find_pair
from alerts import check_alert_triggered

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="Forex Watchlist",
    page_icon="💱",
    layout="wide"
)

st.title("💱 Forex Watchlist & Alerts")
st.caption("Track currency pairs and get notified when rates hit your targets")

# Check for API key
if not API_KEY:
    st.error("⚠️ API Key Required")
    st.markdown("""
    1. Get a free API key at [exchangerate-api.com](https://www.exchangerate-api.com/)
    2. Create a `.env` file in the project folder with:
    ```
    EXCHANGERATE_API_KEY=your_api_key_here
    ```
    3. Restart the app
    """)
    st.stop()

# Sidebar - Add new pair
st.sidebar.header("Add Currency Pair")

currencies = get_available_currencies()
if currencies:
    currency_list = sorted(currencies.keys())

    col1, col2 = st.sidebar.columns(2)
    with col1:
        base = st.selectbox("Base", currency_list, index=currency_list.index("EUR") if "EUR" in currency_list else 0)
    with col2:
        quote = st.selectbox("Quote", currency_list, index=currency_list.index("USD") if "USD" in currency_list else 0)

    if st.sidebar.button("Add Pair", type="primary", use_container_width=True):
        if base == quote:
            st.sidebar.error("Base and quote must be different")
        elif add_pair(base, quote):
            st.sidebar.success(f"Added {base}/{quote}")
            st.rerun()
        else:
            st.sidebar.warning(f"{base}/{quote} already in watchlist")

# Sidebar - Set alert
st.sidebar.divider()
st.sidebar.header("Set Alert")

pairs = list_pairs()
if pairs:
    pair_options = [f"{p['base']}/{p['quote']}" for p in pairs]
    selected_pair = st.sidebar.selectbox("Currency Pair", pair_options)

    if selected_pair:
        base_alert, quote_alert = selected_pair.split("/")

        alert_type = st.sidebar.radio("Alert Type", ["above", "below"], horizontal=True)
        target = st.sidebar.number_input("Target Price", min_value=0.0001, value=1.0, step=0.0001, format="%.4f")
        note = st.sidebar.text_input("Note (optional)")

        if st.sidebar.button("Set Alert", use_container_width=True):
            if add_alert(base_alert, quote_alert, alert_type, target, note):
                st.sidebar.success(f"Alert set: {selected_pair} {alert_type} {target}")
                st.rerun()
else:
    st.sidebar.info("Add a currency pair first")

# Main content
tab1, tab2, tab3 = st.tabs(["📊 Watchlist", "🔔 Check Alerts", "💰 Live Rates"])

with tab1:
    st.header("Your Watchlist")

    if not pairs:
        st.info("Your watchlist is empty. Add currency pairs using the sidebar.")
    else:
        for pair in pairs:
            pair_name = f"{pair['base']}/{pair['quote']}"

            with st.expander(f"**{pair_name}**", expanded=True):
                col1, col2 = st.columns([3, 1])

                with col1:
                    # Show current rate
                    rate = get_rate(pair['base'], pair['quote'])
                    if rate:
                        st.metric("Current Rate", f"{rate:.4f}")
                    else:
                        st.warning("Could not fetch rate")

                    # Show alerts
                    if pair['alerts']:
                        st.subheader("Alerts")
                        for i, alert in enumerate(pair['alerts']):
                            alert_col1, alert_col2 = st.columns([4, 1])
                            with alert_col1:
                                icon = "📈" if alert['type'] == 'above' else "📉"
                                note_text = f" - {alert['note']}" if alert.get('note') else ""
                                st.write(f"{icon} {alert['type'].capitalize()} **{alert['target']:.4f}**{note_text}")
                            with alert_col2:
                                if st.button("🗑️", key=f"del_alert_{pair_name}_{i}"):
                                    remove_alert(pair['base'], pair['quote'], i)
                                    st.rerun()
                    else:
                        st.caption("No alerts set")

                with col2:
                    if st.button("Remove Pair", key=f"del_{pair_name}"):
                        remove_pair(pair['base'], pair['quote'])
                        st.rerun()

with tab2:
    st.header("Check Alerts")

    if not pairs:
        st.info("Add currency pairs and set alerts first.")
    else:
        if st.button("🔔 Check All Alerts", type="primary"):
            triggered = []

            for pair in pairs:
                if not pair['alerts']:
                    continue

                rate = get_rate(pair['base'], pair['quote'])
                if rate is None:
                    continue

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
                    st.warning(f"**{t['pair']}** has {direction} {t['target']:.4f} (Current: {t['rate']:.4f})")
                    if t['note']:
                        st.caption(f"Note: {t['note']}")
            else:
                st.info("No alerts triggered. All rates are within your thresholds.")

        # Show alert summary
        st.subheader("Alert Summary")
        alert_count = sum(len(p['alerts']) for p in pairs)
        st.write(f"Total alerts set: **{alert_count}**")

        for pair in pairs:
            if pair['alerts']:
                st.write(f"**{pair['base']}/{pair['quote']}**: {len(pair['alerts'])} alert(s)")

with tab3:
    st.header("Live Exchange Rates")

    if not pairs:
        st.info("Add currency pairs to see their rates.")
    else:
        cols = st.columns(min(len(pairs), 4))

        for i, pair in enumerate(pairs):
            with cols[i % 4]:
                rate = get_rate(pair['base'], pair['quote'])
                if rate:
                    # Calculate change indicator (placeholder - would need historical data)
                    st.metric(
                        label=f"{pair['base']}/{pair['quote']}",
                        value=f"{rate:.4f}"
                    )
                else:
                    st.error(f"{pair['base']}/{pair['quote']}: Error")

        if st.button("🔄 Refresh Rates"):
            st.rerun()

# Footer
st.divider()
st.caption("Data from [ExchangeRate-API](https://www.exchangerate-api.com/) - Updates every few minutes")
