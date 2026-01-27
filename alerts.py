"""
Alerts module for Forex Watchlist application.
Handles alert checking and desktop notifications.
"""

import platform
import subprocess
from rates import get_rate
from watchlist import update_rate


def send_notification(title, message):
    """
    Send a desktop notification.

    Args:
        title (str): Notification title
        message (str): Notification body text
    """
    system = platform.system()

    try:
        if system == "Darwin":
            # macOS - use osascript for reliable notifications
            script = f'display notification "{message}" with title "{title}"'
            subprocess.run(["osascript", "-e", script], check=True)
        elif system == "Linux":
            # Linux - use notify-send if available
            subprocess.run(["notify-send", title, message], check=True)
        elif system == "Windows":
            # Windows - try plyer
            from plyer import notification
            notification.notify(
                title=title,
                message=message,
                app_name="Forex Watchlist",
                timeout=10
            )
        else:
            # Fallback to console
            print(f"[ALERT] {title}: {message}")
    except Exception:
        # Fallback to console if notification fails
        print(f"[ALERT] {title}: {message}")


def format_alert_message(pair, alert, current_rate):
    """
    Format an alert message for display.

    Args:
        pair (dict): Currency pair data
        alert (dict): Alert configuration
        current_rate (float): Current exchange rate

    Returns:
        str: Formatted message
    """
    direction = "risen above" if alert['type'] == 'above' else "fallen below"
    message = f"{pair['base']}/{pair['quote']} has {direction} {alert['target']:.4f}\n"
    message += f"Current rate: {current_rate:.4f}"
    if alert.get('note'):
        message += f"\nNote: {alert['note']}"
    return message


def check_alert_triggered(alert, current_rate):
    """
    Check if an alert condition is met.

    Args:
        alert (dict): Alert configuration
        current_rate (float): Current exchange rate

    Returns:
        bool: True if alert triggered
    """
    if alert['type'] == 'above':
        return current_rate >= alert['target']
    elif alert['type'] == 'below':
        return current_rate <= alert['target']
    return False


def check_alerts(pairs):
    """
    Check all alerts against current rates and send notifications.

    Args:
        pairs (list): List of currency pair configurations

    Returns:
        list: List of triggered alerts with details
    """
    triggered = []

    for pair in pairs:
        if not pair['alerts']:
            continue

        # Fetch current rate
        current_rate = get_rate(pair['base'], pair['quote'])
        if current_rate is None:
            print(f"Could not fetch rate for {pair['base']}/{pair['quote']}")
            continue

        # Update stored rate
        update_rate(pair['base'], pair['quote'], current_rate)

        # Check each alert
        for alert in pair['alerts']:
            if check_alert_triggered(alert, current_rate):
                message = format_alert_message(pair, alert, current_rate)
                title = f"Forex Alert: {pair['base']}/{pair['quote']}"

                # Send notification
                send_notification(title, message)

                triggered.append({
                    'pair': f"{pair['base']}/{pair['quote']}",
                    'alert': alert,
                    'current_rate': current_rate,
                    'message': message
                })

    return triggered
