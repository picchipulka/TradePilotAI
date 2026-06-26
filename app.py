import time
from collections import Counter
from datetime import datetime

from alerts.alert_state import (
    get_last_zone,
    mark_below_alert_sent,
    mark_buy_alert_sent,
    mark_recovery_alert_sent,
    mark_stop_alert_sent,
    reset_below_alert,
    reset_buy_alert,
    reset_recovery_alert,
    reset_stop_alert,
    set_last_zone,
    was_below_alert_sent,
    was_buy_alert_sent,
    was_recovery_alert_sent,
    was_stop_alert_sent,
)
from alerts.notifier import send_notification
from database.supabase import WatchlistEntry, get_watchlist
from market.market_data import get_current_price
from scanner.scanner import get_distance_to_range, get_range_status, get_zone


SCAN_INTERVAL_SECONDS = 60


def market_monitoring_hours() -> bool:
    now = datetime.now()

    # Monday=0 ... Sunday=6
    if now.weekday() >= 5:
        return False

    return 4 <= now.hour < 20


def _format_price(value: float | None) -> str:
    if value is None:
        return "N/A"

    rounded = round(value, 2)

    if rounded == int(rounded):
        return str(int(rounded))

    return str(rounded)


def _format_entry(entry: WatchlistEntry, current_price: float | None) -> str:
    buy_low = _format_price(entry.Buy_Range_low)
    buy_high = _format_price(entry.Buy_Range_high)

    status = get_range_status(
        current_price,
        entry.Buy_Range_low,
        entry.Buy_Range_high,
    )

    distance = get_distance_to_range(
        current_price,
        entry.Buy_Range_low,
        entry.Buy_Range_high,
    )

    return (
        f"{entry.Ticker} | Current: {_format_price(current_price)}"
        f" | Buy Zone: {buy_low}-{buy_high}"
        f" | Status: {status}"
        f" | Distance: {_format_price(distance)}"
    )


def _scan_entry(entry: WatchlistEntry) -> dict:
    current_price = get_current_price(entry.Ticker)

    status = get_range_status(
        current_price,
        entry.Buy_Range_low,
        entry.Buy_Range_high,
    )

    distance = get_distance_to_range(
        current_price,
        entry.Buy_Range_low,
        entry.Buy_Range_high,
    )

    zone = get_zone(
        current_price,
        entry.Buy_Range_low,
        entry.Buy_Range_high,
        entry.Stop_loss,
    )

    return {
        "entry": entry,
        "current_price": current_price,
        "status": status,
        "distance": distance,
        "zone": zone,
    }


def _print_console_alert(title: str, item: dict, message: str) -> None:
    entry = item["entry"]

    print("\n===================================")
    print(title)
    print(f"Ticker     : {entry.Ticker}")
    print(f"Current    : {_format_price(item['current_price'])}")
    print(
        f"Buy Zone   : "
        f"{_format_price(entry.Buy_Range_low)} - "
        f"{_format_price(entry.Buy_Range_high)}"
    )
    print(f"Stop Loss  : {_format_price(entry.Stop_loss)}")
    print(f"Message    : {message}")
    print("===================================\n")


def _send_alert(title: str, item: dict, message: str) -> None:
    _print_console_alert(title, item, message)

    entry = item["entry"]

    send_notification(
        ticker=entry.Ticker,
        current_price=item["current_price"],
        buy_low=entry.Buy_Range_low,
        buy_high=entry.Buy_Range_high,
    )


def _process_alert(item: dict) -> None:
    entry = item["entry"]
    ticker = entry.Ticker
    current_zone = item["zone"]
    last_zone = get_last_zone(ticker)

    if current_zone == "UNKNOWN":
        set_last_zone(ticker, current_zone)
        return

    if current_zone == "IN_BUY_ZONE":
        reset_below_alert(ticker)
        reset_stop_alert(ticker)
        reset_recovery_alert(ticker)

        if not was_buy_alert_sent(ticker):
            _send_alert(
                "🚨 BUY ALERT 🚨",
                item,
                "Price entered buy zone.",
            )
            mark_buy_alert_sent(ticker)

    elif current_zone == "ABOVE_BUY_ZONE":
        reset_below_alert(ticker)
        reset_stop_alert(ticker)
        reset_recovery_alert(ticker)

    elif current_zone == "BELOW_BUY_ZONE":
        reset_buy_alert(ticker)
        reset_stop_alert(ticker)
        reset_recovery_alert(ticker)

        if last_zone == "IN_BUY_ZONE" and not was_below_alert_sent(ticker):
            _send_alert(
                "🚨 NOTIFICATION ALERT 🚨",
                item,
                "Price exited below buy zone and is heading toward stop.",
            )
            mark_below_alert_sent(ticker)

    elif current_zone == "STOP_ZONE":
        reset_buy_alert(ticker)
        reset_below_alert(ticker)

        if last_zone == "BELOW_BUY_ZONE" and not was_stop_alert_sent(ticker):
            _send_alert(
                "🚨 DECISION ALERT 🚨",
                item,
                "Price entered stop zone.",
            )
            mark_stop_alert_sent(ticker)

    if last_zone == "STOP_ZONE" and current_zone == "BELOW_BUY_ZONE":
        if not was_recovery_alert_sent(ticker):
            _send_alert(
                "🚨 NOTIFICATION ALERT 🚨",
                item,
                "Price is heading back toward buy range low.",
            )
            mark_recovery_alert_sent(ticker)

    set_last_zone(ticker, current_zone)


def run_scan_once() -> None:
    entries = get_watchlist()

    if not entries:
        print("No watchlist entries found.")
        return

    scanned_entries = [_scan_entry(entry) for entry in entries]

    sorted_entries = sorted(
        scanned_entries,
        key=lambda item: float("inf") if item["distance"] is None else item["distance"],
    )

    status_counts = Counter(item["status"] for item in scanned_entries)

    print("\n" + "=" * 60)
    print(f"Scan Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Found {len(entries)} watchlist entries")
    print("=" * 60 + "\n")

    for item in sorted_entries:
        print(_format_entry(item["entry"], item["current_price"]))
        _process_alert(item)

    print("\nSummary")
    print("-------")
    print(f"IN RANGE: {status_counts.get('IN RANGE', 0)}")
    print(f"BELOW: {status_counts.get('BELOW', 0)}")
    print(f"ABOVE: {status_counts.get('ABOVE', 0)}")
    print(f"UNKNOWN: {status_counts.get('UNKNOWN', 0)}")


def main() -> None:
    print("TradePilotAI continuous scanner started.")
    print(f"Scanning every {SCAN_INTERVAL_SECONDS} seconds.")
    print("Active window: Monday-Friday, 4:00 AM-8:00 PM.")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            if market_monitoring_hours():
                run_scan_once()
            else:
                print(
                    f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} "
                    "Outside monitoring hours. Sleeping..."
                )

            time.sleep(SCAN_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\nTradePilotAI scanner stopped.")


if __name__ == "__main__":
    main()