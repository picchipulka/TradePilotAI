last_zone_by_ticker: dict[str, str] = {}
buy_alert_sent: set[str] = set()
below_alert_sent: set[str] = set()
stop_alert_sent: set[str] = set()
recovery_alert_sent: set[str] = set()


def get_last_zone(ticker: str) -> str | None:
    return last_zone_by_ticker.get(ticker)


def set_last_zone(ticker: str, zone: str) -> None:
    last_zone_by_ticker[ticker] = zone


def was_buy_alert_sent(ticker: str) -> bool:
    return ticker in buy_alert_sent


def mark_buy_alert_sent(ticker: str) -> None:
    buy_alert_sent.add(ticker)


def reset_buy_alert(ticker: str) -> None:
    buy_alert_sent.discard(ticker)


def was_below_alert_sent(ticker: str) -> bool:
    return ticker in below_alert_sent


def mark_below_alert_sent(ticker: str) -> None:
    below_alert_sent.add(ticker)


def reset_below_alert(ticker: str) -> None:
    below_alert_sent.discard(ticker)


def was_stop_alert_sent(ticker: str) -> bool:
    return ticker in stop_alert_sent


def mark_stop_alert_sent(ticker: str) -> None:
    stop_alert_sent.add(ticker)


def reset_stop_alert(ticker: str) -> None:
    stop_alert_sent.discard(ticker)


def was_recovery_alert_sent(ticker: str) -> bool:
    return ticker in recovery_alert_sent


def mark_recovery_alert_sent(ticker: str) -> None:
    recovery_alert_sent.add(ticker)


def reset_recovery_alert(ticker: str) -> None:
    recovery_alert_sent.discard(ticker)