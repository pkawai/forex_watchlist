"""
Forex Watchlist CLI Application

A command-line tool for tracking forex currency pairs and receiving
desktop notifications when rates hit user-defined targets.

Usage:
    python main.py add EUR USD          - Add a currency pair
    python main.py remove EUR USD       - Remove a currency pair
    python main.py alert EUR USD above 1.10 "Sell signal"  - Set alert
    python main.py list                 - Show watchlist
    python main.py check                - Check alerts and notify
    python main.py rates                - Show current rates
    python main.py currencies           - List available currencies
"""

import click
from watchlist import add_pair, remove_pair, add_alert, remove_alert, list_pairs
from rates import get_rate, get_available_currencies
from alerts import check_alerts


@click.group()
def cli():
    """Forex Watchlist - Track currency pairs and get price alerts."""
    pass


@cli.command()
@click.argument('base')
@click.argument('quote')
def add(base, quote):
    """Add a currency pair to your watchlist."""
    if add_pair(base, quote):
        click.echo(f"Added {base.upper()}/{quote.upper()} to watchlist")
    else:
        click.echo(f"{base.upper()}/{quote.upper()} already in watchlist")


@cli.command()
@click.argument('base')
@click.argument('quote')
def remove(base, quote):
    """Remove a currency pair from your watchlist."""
    if remove_pair(base, quote):
        click.echo(f"Removed {base.upper()}/{quote.upper()} from watchlist")
    else:
        click.echo(f"{base.upper()}/{quote.upper()} not found in watchlist")


@cli.command()
@click.argument('base')
@click.argument('quote')
@click.argument('alert_type', type=click.Choice(['above', 'below']))
@click.argument('target', type=float)
@click.argument('note', default='')
def alert(base, quote, alert_type, target, note):
    """Set a price alert for a currency pair."""
    # First check if pair exists
    pairs = list_pairs()
    pair_exists = any(
        p['base'] == base.upper() and p['quote'] == quote.upper()
        for p in pairs
    )

    if not pair_exists:
        # Auto-add the pair
        add_pair(base, quote)
        click.echo(f"Added {base.upper()}/{quote.upper()} to watchlist")

    if add_alert(base, quote, alert_type, target, note):
        click.echo(f"Alert set: {base.upper()}/{quote.upper()} {alert_type} {target}")
        if note:
            click.echo(f"Note: {note}")
    else:
        click.echo("Failed to set alert")


@cli.command('list')
def list_cmd():
    """Show all watched currency pairs and alerts."""
    pairs = list_pairs()

    if not pairs:
        click.echo("Watchlist is empty. Add pairs with: forex add EUR USD")
        return

    click.echo("\n=== Forex Watchlist ===\n")

    for pair in pairs:
        rate_info = ""
        if pair.get('last_rate'):
            rate_info = f" (last: {pair['last_rate']:.4f})"

        click.echo(f"{pair['base']}/{pair['quote']}{rate_info}")

        if pair['alerts']:
            for i, alert in enumerate(pair['alerts']):
                note = f" - {alert['note']}" if alert.get('note') else ""
                click.echo(f"  [{i}] {alert['type']} {alert['target']:.4f}{note}")
        else:
            click.echo("  No alerts set")
        click.echo()


@cli.command()
def check():
    """Check all alerts and send notifications for triggered ones."""
    pairs = list_pairs()

    if not pairs:
        click.echo("Watchlist is empty. Add pairs with: forex add EUR USD")
        return

    click.echo("Checking alerts...")
    triggered = check_alerts(pairs)

    if triggered:
        click.echo(f"\n{len(triggered)} alert(s) triggered:")
        for t in triggered:
            click.echo(f"  - {t['pair']}: {t['alert']['type']} {t['alert']['target']:.4f}")
            click.echo(f"    Current rate: {t['current_rate']:.4f}")
    else:
        click.echo("No alerts triggered")


@cli.command()
def rates():
    """Show current rates for all watched pairs."""
    pairs = list_pairs()

    if not pairs:
        click.echo("Watchlist is empty. Add pairs with: forex add EUR USD")
        return

    click.echo("\n=== Current Rates ===\n")

    for pair in pairs:
        rate = get_rate(pair['base'], pair['quote'])
        if rate:
            click.echo(f"{pair['base']}/{pair['quote']}: {rate:.4f}")
        else:
            click.echo(f"{pair['base']}/{pair['quote']}: Error fetching rate")


@cli.command()
def currencies():
    """List all available currencies."""
    currencies = get_available_currencies()

    if currencies:
        click.echo("\n=== Available Currencies ===\n")
        for code, name in sorted(currencies.items()):
            click.echo(f"  {code}: {name}")
    else:
        click.echo("Could not fetch currency list")


@cli.command('remove-alert')
@click.argument('base')
@click.argument('quote')
@click.argument('index', type=int)
def remove_alert_cmd(base, quote, index):
    """Remove an alert by index (see 'list' for indices)."""
    if remove_alert(base, quote, index):
        click.echo(f"Removed alert [{index}] from {base.upper()}/{quote.upper()}")
    else:
        click.echo("Alert not found. Use 'list' to see alert indices.")


if __name__ == '__main__':
    cli()
