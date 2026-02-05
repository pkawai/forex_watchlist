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
from portfolio import open_position, close_position, get_all_positions, calculate_pips, get_portfolio_summary

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
tab1, tab2, tab3, tab4 = st.tabs(["📊 Watchlist & Charts", "🔔 Check Alerts", "💰 Live Rates", "💼 Portfolio"])

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
        # Auto-monitor toggle
        col_monitor1, col_monitor2 = st.columns([1, 2])
        with col_monitor1:
            auto_monitor = st.toggle("Auto-Monitor", value=False, help="Automatically check alerts every 30 seconds")
        with col_monitor2:
            if auto_monitor:
                st.caption("🟢 Monitoring active - checking every 30 seconds")

        # Browser notification permission request
        if auto_monitor:
            notification_js = """
            <script>
            if ("Notification" in window && Notification.permission === "default") {
                Notification.requestPermission();
            }
            </script>
            """
            components.html(notification_js, height=0)

        # Check alerts function
        def check_all_alerts():
            triggered = []
            checked = 0

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
            return triggered, checked

        # Manual check button
        if st.button("🔔 Check All Alerts Now", type="primary"):
            with st.spinner("Checking alerts..."):
                triggered, checked = check_all_alerts()

            if triggered:
                st.success(f"🚨 {len(triggered)} alert(s) triggered!")
                for t in triggered:
                    direction = "risen above" if t['type'] == 'above' else "fallen below"
                    st.warning(f"**{t['pair']}** has {direction} {t['target']:.5f} (Current: {t['rate']:.5f})")
                    if t['note']:
                        st.caption(f"Note: {t['note']}")

                    # Send browser notification
                    notif_js = f"""
                    <script>
                    if ("Notification" in window && Notification.permission === "granted") {{
                        new Notification("Forex Alert: {t['pair']}", {{
                            body: "Price {direction} {t['target']:.5f}\\nCurrent: {t['rate']:.5f}",
                            icon: "💱",
                            requireInteraction: true
                        }});
                    }}
                    </script>
                    """
                    components.html(notif_js, height=0)
            else:
                st.info(f"No alerts triggered. Checked {checked} alert(s).")

        # Auto-refresh if monitoring is enabled
        if auto_monitor:
            import time
            from streamlit_autorefresh import st_autorefresh

            # Refresh every 30 seconds
            count = st_autorefresh(interval=30000, limit=None, key="alert_monitor")

            if count > 0:
                triggered, checked = check_all_alerts()

                if triggered:
                    st.error(f"🚨 {len(triggered)} ALERT(S) TRIGGERED!")
                    for t in triggered:
                        direction = "risen above" if t['type'] == 'above' else "fallen below"
                        st.warning(f"**{t['pair']}** has {direction} {t['target']:.5f} (Current: {t['rate']:.5f})")

                        # Browser notification
                        notif_js = f"""
                        <script>
                        if ("Notification" in window && Notification.permission === "granted") {{
                            new Notification("Forex Alert: {t['pair']}", {{
                                body: "Price {direction} {t['target']:.5f}\\nCurrent: {t['rate']:.5f}",
                                requireInteraction: true
                            }});
                        }}
                        </script>
                        """
                        components.html(notif_js, height=0)
                else:
                    st.success(f"✓ Last check: {checked} alerts OK")

        st.divider()

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

        # Desktop monitor instructions
        st.divider()
        st.subheader("Desktop Notifications")
        st.markdown("""
        For desktop notifications that work even when the browser is closed, run the monitor script:
        ```bash
        python monitor.py --interval 60
        ```
        This will check alerts every 60 seconds and send system notifications.
        """)

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

with tab4:
    st.header("Portfolio")

    # Open a new position
    st.subheader("Open Position")
    with st.form("position_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            pos_pair = st.selectbox("Pair", available_pairs, key="portfolio_pair")
            pos_direction = st.radio("Direction", ["BUY", "SELL"], horizontal=True, key="pos_dir")
        with col2:
            pos_entry = st.number_input("Entry Price", min_value=0.00001, value=1.00000, step=0.00001, format="%.5f", key="pos_entry")
            pos_lots = st.number_input("Lot Size", min_value=0.01, value=0.1, step=0.01, format="%.2f", key="pos_lots")
        with col3:
            pos_sl = st.number_input("Stop Loss (optional)", min_value=0.0, value=0.0, step=0.00001, format="%.5f", key="pos_sl")
            pos_tp = st.number_input("Take Profit (optional)", min_value=0.0, value=0.0, step=0.00001, format="%.5f", key="pos_tp")

        pos_notes = st.text_input("Notes (optional)", key="pos_notes")
        pos_submitted = st.form_submit_button("Open Position", type="primary", use_container_width=True)

        if pos_submitted:
            sl = pos_sl if pos_sl > 0 else None
            tp = pos_tp if pos_tp > 0 else None
            open_position(pos_pair, pos_direction, pos_entry, pos_lots, sl, tp, pos_notes)
            st.success(f"Opened {pos_direction} {pos_pair} at {pos_entry:.5f}")
            st.rerun()

    # Get positions and calculate live P/L
    positions = get_all_positions()

    if positions:
        st.divider()

        # Calculate pips for each position using live rates
        positions_with_pips = []
        for pos in positions:
            base, quote = pos["pair"].split("/")
            current_rate = get_rate(base, quote)
            if current_rate:
                pips = calculate_pips(pos["pair"], pos["direction"], pos["entry_price"], current_rate)
                positions_with_pips.append((pos, pips, current_rate))
            else:
                positions_with_pips.append((pos, 0, None))

        # Portfolio summary
        summary = get_portfolio_summary([(p, pips) for p, pips, _ in positions_with_pips])

        st.subheader("Portfolio Summary")
        s1, s2, s3, s4, s5 = st.columns(5)
        with s1:
            st.metric("Open Positions", summary["total_positions"])
        with s2:
            st.metric("Total P/L", f"{summary['total_pips']:+.1f} pips")
        with s3:
            st.metric("Winning", summary["winning"])
        with s4:
            st.metric("Losing", summary["losing"])
        with s5:
            st.metric("Total Lots", f"{summary['total_lots']:.2f}")

        # Open positions list
        st.divider()
        st.subheader("Open Positions")

        for pos, pips, current_rate in positions_with_pips:
            color = "green" if pips > 0 else "red" if pips < 0 else "gray"
            direction_label = "Long" if pos["direction"] == "BUY" else "Short"

            with st.container():
                c1, c2, c3, c4 = st.columns([2, 2, 1, 1])
                with c1:
                    st.markdown(f"**{pos['pair']}** - {direction_label}")
                    st.caption(f"Opened: {pos['opened_at']} | {pos['lot_size']} lots")
                with c2:
                    current_display = f"{current_rate:.5f}" if current_rate else "N/A"
                    st.caption(f"Entry: {pos['entry_price']:.5f} | Current: {current_display}")
                    sl_text = f"SL: {pos['stop_loss']:.5f}" if pos.get("stop_loss") else "SL: -"
                    tp_text = f"TP: {pos['take_profit']:.5f}" if pos.get("take_profit") else "TP: -"
                    st.caption(f"{sl_text} | {tp_text}")
                    if pos.get("notes"):
                        st.caption(f"Notes: {pos['notes']}")
                with c3:
                    st.markdown(f":{color}[**{pips:+.1f} pips**]")
                with c4:
                    if st.button("Close", key=f"close_pos_{pos['id']}"):
                        close_position(pos["id"])
                        st.rerun()
                st.divider()

        if st.button("Refresh Prices"):
            st.rerun()
    else:
        st.info("No open positions. Use the form above to track a position.")

# Footer
st.divider()
col1, col2 = st.columns(2)
with col1:
    st.caption("Real-time data from [TradingView](https://tradingview.com) via OANDA")
with col2:
    st.caption("No API key required")
