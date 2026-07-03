import time
from collections import Counter
from datetime import datetime

from alerts.alert_state import (
    ABOVE_BUY_ZONE,
    BELOW_BUY_ZONE,
    IN_BUY_ZONE,
    RECOVERING_TO_BUY_ZONE,
    STOP_ZONE,
    get_state,
    set_state,
)
from ai.agent import get_macro_context, review_thesis
from alerts.notifier import send_notification
from database.supabase import WatchlistEntry, get_watchlist
from market.market_data import get_current_price
from scanner.scanner import get_distance_to_range, get_range_status, get_zone

# Alert titles significant enough in the trade thesis lifecycle to warrant an
# independent AI review (entering the opportunity zone / entering the
# decision zone), per docs/trade_thesis_specification.md.
AI_REVIEW_ALERT_TITLES = {"🚨 BUY ALERT 🚨", "🚨 DECISION ALERT 🚨"}


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


def _format_ai_review(
    entry: WatchlistEntry,
    current_price: float | None,
    macro_context_cache: dict,
) -> str | None:
    if macro_context_cache.get("context") is None:
        macro_context_cache["context"] = get_macro_context()

    review = review_thesis(entry, current_price, macro_context_cache["context"])
    if review is None:
        return None

    return (
        f"\nAI Conviction : {review.ai_conviction}/10 ({review.thesis_status})\n"
        f"AI Thesis     : {review.ai_thesis}\n"
        f"Supporting    : {'; '.join(review.supporting_evidence) or 'None noted'}\n"
        f"Contradicting : {'; '.join(review.contradicting_evidence) or 'None noted'}\n"
        f"Risks         : {'; '.join(review.risks) or 'None noted'}"
    )


def _send_alert(
    title: str, item: dict, message: str, macro_context_cache: dict
) -> None:
    if title in AI_REVIEW_ALERT_TITLES:
        ai_summary = _format_ai_review(
            item["entry"], item["current_price"], macro_context_cache
        )
        if ai_summary:
            message = f"{message}\n{ai_summary}"

    _print_console_alert(title, item, message)

    entry = item["entry"]

    send_notification(
        ticker=entry.Ticker,
        current_price=item["current_price"],
        buy_low=entry.Buy_Range_low,
        buy_high=entry.Buy_Range_high,
        title=title,
        message=message,
    )


def _process_alert(item: dict, macro_context_cache: dict) -> None:
    """Edge-triggered state machine matching docs/Trade_alert_state_diagram.png.

    Zones 4 (BELOW_BUY_ZONE, falling from the buy zone) and 6 (recovering
    up out of the stop zone) share the same scanner zone but are distinct
    states here, since the diagram alerts differently on each: state 4 gets
    a "heading toward stop" notification, while re-entering the buy zone
    from state 6 (Rule 6) must NOT re-fire the buy alert.
    """
    entry = item["entry"]
    ticker = entry.Ticker
    zone = item["zone"]
    previous_state = get_state(ticker)

    if zone == "UNKNOWN":
        return

    new_state = zone
    alert = None

    if zone == IN_BUY_ZONE:
        if previous_state == RECOVERING_TO_BUY_ZONE:
            pass  # Rule 6: recovering into the buy zone fires no alert.
        elif previous_state != IN_BUY_ZONE:
            alert = ("🚨 BUY ALERT 🚨", "Price entered buy zone.")

    elif zone == ABOVE_BUY_ZONE:
        pass

    elif zone == BELOW_BUY_ZONE:
        if previous_state == STOP_ZONE:
            new_state = RECOVERING_TO_BUY_ZONE
            alert = (
                "🚨 NOTIFICATION ALERT 🚨",
                "Price is heading back toward buy range low.",
            )
        elif previous_state == RECOVERING_TO_BUY_ZONE:
            new_state = RECOVERING_TO_BUY_ZONE
        elif previous_state != BELOW_BUY_ZONE:
            alert = (
                "🚨 NOTIFICATION ALERT 🚨",
                "Price exited below buy zone and is heading toward stop.",
            )

    elif zone == STOP_ZONE:
        if previous_state != STOP_ZONE:
            alert = ("🚨 DECISION ALERT 🚨", "Price entered stop zone.")

    if alert is not None:
        _send_alert(alert[0], item, alert[1], macro_context_cache)

    set_state(ticker, new_state)


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

    # Fetched lazily on the first AI-review alert this scan and reused for
    # the rest, so macro news/indicators are only fetched once per scan
    # instead of once per ticker (Alpha Vantage rate limit).
    macro_context_cache: dict = {"context": None}

    for item in sorted_entries:
        print(_format_entry(item["entry"], item["current_price"]))
        _process_alert(item, macro_context_cache)

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