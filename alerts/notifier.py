try:
    from winotify import Notification
except Exception as exc:
    Notification = None
    IMPORT_ERROR = exc
else:
    IMPORT_ERROR = None


def send_notification(
    ticker: str,
    current_price: float | None,
    buy_low: float | None,
    buy_high: float | None,
) -> None:
    if Notification is None:
        print(f"Notification skipped: winotify import failed: {IMPORT_ERROR}")
        return

    if current_price is None or buy_low is None or buy_high is None:
        print(f"Notification skipped: missing price data for {ticker}.")
        return

    toast = Notification(
        app_id="TradePilotAI",
        title="TradePilotAI Buy Alert",
        msg=(
            f"{ticker} entered buy zone\n"
            f"Current: {current_price:.2f}\n"
            f"Buy Zone: {buy_low:.2f} - {buy_high:.2f}"
        ),
        duration="short",
    )

    toast.show()