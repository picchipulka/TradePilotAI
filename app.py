from collections import Counter

from database.supabase import WatchlistEntry, get_watchlist
from market.market_data import get_current_price
from scanner.scanner import get_distance_to_range, get_range_status


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

    return {
        "entry": entry,
        "current_price": current_price,
        "status": status,
        "distance": distance,
    }


def main() -> None:
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

    print(f"Found {len(entries)} watchlist entries\n")

    for item in sorted_entries:
        print(_format_entry(item["entry"], item["current_price"]))

    print("\nSummary")
    print("-------")
    print(f"IN RANGE: {status_counts.get('IN RANGE', 0)}")
    print(f"BELOW: {status_counts.get('BELOW', 0)}")
    print(f"ABOVE: {status_counts.get('ABOVE', 0)}")
    print(f"UNKNOWN: {status_counts.get('UNKNOWN', 0)}")


if __name__ == "__main__":
    main()