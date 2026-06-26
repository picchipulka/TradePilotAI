def get_range_status(
    price: float | None,
    buy_low: float | None,
    buy_high: float | None,
) -> str:
    if price is None or buy_low is None or buy_high is None:
        return "UNKNOWN"
    if price < buy_low:
        return "BELOW"
    if price > buy_high:
        return "ABOVE"
    return "IN RANGE"


def get_distance_to_range(
    price: float | None,
    buy_low: float | None,
    buy_high: float | None,
) -> float | None:
    if price is None or buy_low is None or buy_high is None:
        return None
    if buy_low <= price <= buy_high:
        return 0.0
    if price < buy_low:
        return buy_low - price
    return price - buy_high


def get_zone(
    price: float | None,
    buy_low: float | None,
    buy_high: float | None,
    stop_loss: float | None,
) -> str:
    if price is None or buy_low is None or buy_high is None:
        return "UNKNOWN"

    if price > buy_high:
        return "ABOVE_BUY_ZONE"

    if buy_low <= price <= buy_high:
        return "IN_BUY_ZONE"

    if stop_loss is not None and price <= stop_loss:
        return "STOP_ZONE"

    if price < buy_low:
        return "BELOW_BUY_ZONE"

    return "UNKNOWN"