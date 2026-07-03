import os

import requests
from dotenv import load_dotenv

load_dotenv()

CALLMEBOT_URL = "https://api.callmebot.com/whatsapp.php"


def send_notification(
    ticker: str,
    current_price: float | None,
    buy_low: float | None,
    buy_high: float | None,
    title: str = "TradePilotAI Alert",
    message: str = "",
) -> None:
    phone = os.getenv("CALLMEBOT_PHONE")
    api_key = os.getenv("CALLMEBOT_APIKEY")

    if not phone or not api_key:
        print(
            "WhatsApp notification skipped: "
            "CALLMEBOT_PHONE and CALLMEBOT_APIKEY must be set in .env"
        )
        return

    if current_price is None or buy_low is None or buy_high is None:
        print(f"WhatsApp notification skipped: missing price data for {ticker}.")
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
            params={"phone": phone, "text": text, "apikey": api_key},
            timeout=10,
        )
        if response.status_code != 200:
            print(
                f"WhatsApp notification failed for {ticker}: "
                f"HTTP {response.status_code}"
            )
    except requests.RequestException as exc:
        print(f"WhatsApp notification failed for {ticker}: {exc}")
