#!/usr/bin/env python3
"""
Forex Alert Monitor - Background Service

Runs continuously and sends desktop notifications when alerts trigger.
Usage: python monitor.py [--interval 60]
"""

import argparse
import time
import platform
import subprocess
from datetime import datetime

from watchlist import list_pairs
from rates import get_rate
from alerts import check_alert_triggered
from storage import load_watchlist, save_watchlist


def send_desktop_notification(title, message):
    """Send a desktop notification based on OS."""
    system = platform.system()

    try:
        if system == "Darwin":  # macOS
            # Use osascript for macOS notifications
            script = f'display notification "{message}" with title "{title}" sound name "Glass"'
            subprocess.run(["osascript", "-e", script], check=True)
        elif system == "Linux":
            subprocess.run(["notify-send", "-u", "critical", title, message], check=True)
        elif system == "Windows":
            # Use PowerShell for Windows notifications
            ps_script = f'''
            [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
            $template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
            $textNodes = $template.GetElementsByTagName("text")
            $textNodes.Item(0).AppendChild($template.CreateTextNode("{title}")) | Out-Null
            $textNodes.Item(1).AppendChild($template.CreateTextNode("{message}")) | Out-Null
            $toast = [Windows.UI.Notifications.ToastNotification]::new($template)
            [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Forex Watchlist").Show($toast)
            '''
            subprocess.run(["powershell", "-Command", ps_script], check=True)

        print(f"[NOTIFICATION] {title}: {message}")
        return True
    except Exception as e:
        print(f"[ERROR] Could not send notification: {e}")
        print(f"[ALERT] {title}: {message}")
        return False


def check_and_notify(triggered_cache):
    """Check all alerts and send notifications for newly triggered ones."""
    pairs = list_pairs()
    newly_triggered = []

    for pair in pairs:
        if not pair['alerts']:
            continue

        pair_key = f"{pair['base']}/{pair['quote']}"
        rate = get_rate(pair['base'], pair['quote'])

        if rate is None:
            continue

        for i, alert in enumerate(pair['alerts']):
            alert_key = f"{pair_key}_{alert['type']}_{alert['target']}"

            if check_alert_triggered(alert, rate):
                # Only notify if not already triggered recently
                if alert_key not in triggered_cache:
                    triggered_cache[alert_key] = datetime.now()

                    direction = "above" if alert['type'] == 'above' else "below"
                    title = f"Forex Alert: {pair_key}"
                    message = f"Price is now {direction} {alert['target']:.5f}\nCurrent: {rate:.5f}"
                    if alert.get('note'):
                        message += f"\n{alert['note']}"

                    send_desktop_notification(title, message)
                    newly_triggered.append({
                        'pair': pair_key,
                        'type': alert['type'],
                        'target': alert['target'],
                        'rate': rate
                    })
            else:
                # Remove from cache if alert is no longer triggered (price moved back)
                if alert_key in triggered_cache:
                    del triggered_cache[alert_key]

    return newly_triggered


def main():
    parser = argparse.ArgumentParser(description="Monitor forex alerts and send notifications")
    parser.add_argument("--interval", "-i", type=int, default=60,
                        help="Check interval in seconds (default: 60)")
    args = parser.parse_args()

    print("=" * 50)
    print("Forex Alert Monitor")
    print("=" * 50)
    print(f"Check interval: {args.interval} seconds")
    print("Press Ctrl+C to stop")
    print("=" * 50)

    # Cache to track already-triggered alerts (prevent spam)
    triggered_cache = {}

    # Initial check
    pairs = list_pairs()
    alert_count = sum(len(p['alerts']) for p in pairs)
    print(f"\nMonitoring {len(pairs)} pair(s) with {alert_count} alert(s)")

    if alert_count == 0:
        print("\nNo alerts set! Add alerts first:")
        print("  python main.py alert EUR USD above 1.10")
        print("  or use the web app: streamlit run app.py")
        return

    print("\nStarting monitor...\n")

    try:
        while True:
            timestamp = datetime.now().strftime("%H:%M:%S")

            # Reload pairs in case they were updated
            pairs = list_pairs()
            alert_count = sum(len(p['alerts']) for p in pairs)

            print(f"[{timestamp}] Checking {alert_count} alerts...", end=" ")

            triggered = check_and_notify(triggered_cache)

            if triggered:
                print(f"{len(triggered)} TRIGGERED!")
                for t in triggered:
                    print(f"  -> {t['pair']}: {t['type']} {t['target']:.5f} (now: {t['rate']:.5f})")
            else:
                print("OK")

            time.sleep(args.interval)

    except KeyboardInterrupt:
        print("\n\nMonitor stopped.")


if __name__ == "__main__":
    main()
