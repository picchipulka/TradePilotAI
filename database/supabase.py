import os
from dataclasses import dataclass

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

TABLE_NAME = "Stock screener watchlist"


@dataclass
class WatchlistEntry:
    Ticker: str
    Buy_Range_low: float | None
    Buy_Range_high: float | None
    Stop_loss: float | None


def _get_client() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env")
    return create_client(url, key)


def get_watchlist() -> list[WatchlistEntry]:
    try:
        client = _get_client()
        response = client.table(TABLE_NAME).select("*").execute()
    except ValueError as exc:
        print(f"Supabase configuration error: {exc}")
        return []
    except Exception as exc:
        print(f"Supabase query failed: {exc}")
        return []

    rows = response.data or []
    return [
        WatchlistEntry(
            Ticker=row.get("Ticker") or "",
            Buy_Range_low=row.get("Buy_Range_low"),
            Buy_Range_high=row.get("Buy_Range_high"),
            Stop_loss=row.get("Stop_loss"),
        )
        for row in rows
    ]
