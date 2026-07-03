import os

import requests
from dotenv import load_dotenv

load_dotenv()

CALLMEBOT_URL = "https://api.callmebot.com/text.php"


def send_notification(
    ticker: str,
    current_price: float | None,
    buy_low: float | None,
    buy_high: float | None,
    title: str = "TradePilotAI Alert",
    message: str = "",
) -> None:
    telegram_user = os.getenv("CALLMEBOT_TELEGRAM_USER")

    if not telegram_user:
        print(
            "Telegram notification skipped: "
            "CALLMEBOT_TELEGRAM_USER must be set in .env (e.g. @yourusername)"
        )
        return

    if current_price is None or buy_low is None or buy_high is None:
        print(f"Telegram notification skipped: missing price data for {ticker}.")
        return

    text = (
        f"{title}\n"
        f"{ticker}: {message}\n"
        f"Current: {current_price:.2f}\n"
        f"Buy Zone: {buy_low:.2f} - {buy_high:.2f}"
    )

    try:
        response = requests.get(
            CALLMEBOT_URL,
            params={"user": telegram_user, "text": text},
            timeout=10,
        )
        if response.status_code != 200:
            print(
                f"Telegram notification failed for {ticker}: "
                f"HTTP {response.status_code}"
            )
    except requests.RequestException as exc:
        print(f"Telegram notification failed for {ticker}: {exc}")
