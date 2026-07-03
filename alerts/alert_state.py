ABOVE_BUY_ZONE = "ABOVE_BUY_ZONE"
IN_BUY_ZONE = "IN_BUY_ZONE"
BELOW_BUY_ZONE = "BELOW_BUY_ZONE"
STOP_ZONE = "STOP_ZONE"
RECOVERING_TO_BUY_ZONE = "RECOVERING_TO_BUY_ZONE"

_state_by_ticker: dict[str, str] = {}


def get_state(ticker: str) -> str | None:
    return _state_by_ticker.get(ticker)


def set_state(ticker: str, state: str) -> None:
    _state_by_ticker[ticker] = state
