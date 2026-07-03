import os
from dataclasses import dataclass

import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://www.alphavantage.co/query"

# Alpha Vantage NEWS_SENTIMENT topics relevant to macro/market-wide conditions
# (FOMC, rate decisions, inflation prints, broad sell-offs, sector rotation).
MACRO_TOPICS = ["economy_macro", "economy_monetary", "economy_fiscal", "financial_markets"]

# Alpha Vantage has no PPI series; CPI/UNEMPLOYMENT/NONFARM_PAYROLL/FEDERAL_FUNDS_RATE
# cover CPI, jobs report, and rate-decision context.
ECONOMIC_INDICATORS = ["CPI", "UNEMPLOYMENT", "NONFARM_PAYROLL", "FEDERAL_FUNDS_RATE"]


@dataclass
class NewsItem:
    title: str
    summary: str
    source: str
    url: str
    time_published: str
    overall_sentiment_label: str
    overall_sentiment_score: float


def _get(params: dict) -> dict | None:
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        print("Alpha Vantage error: ALPHA_VANTAGE_API_KEY not set in .env")
        return None

    try:
        response = requests.get(
            BASE_URL, params={**params, "apikey": api_key}, timeout=15
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"Alpha Vantage request failed: {exc}")
        return None

    data = response.json()

    if "Note" in data or "Information" in data:
        print(f"Alpha Vantage limit/info: {data.get('Note') or data.get('Information')}")
        return None

    return data


def _parse_news(data: dict) -> list[NewsItem]:
    items = []
    for feed in data.get("feed", []):
        items.append(
            NewsItem(
                title=feed.get("title", ""),
                summary=feed.get("summary", ""),
                source=feed.get("source", ""),
                url=feed.get("url", ""),
                time_published=feed.get("time_published", ""),
                overall_sentiment_label=feed.get("overall_sentiment_label", ""),
                overall_sentiment_score=float(feed.get("overall_sentiment_score", 0.0)),
            )
        )
    return items


def get_stock_news(ticker: str, limit: int = 10) -> list[NewsItem]:
    data = _get(
        {
            "function": "NEWS_SENTIMENT",
            "tickers": ticker,
            "limit": str(limit),
            "sort": "LATEST",
        }
    )
    if not data:
        return []
    return _parse_news(data)


def get_macro_news(limit: int = 10) -> list[NewsItem]:
    data = _get(
        {
            "function": "NEWS_SENTIMENT",
            "topics": ",".join(MACRO_TOPICS),
            "limit": str(limit),
            "sort": "LATEST",
        }
    )
    if not data:
        return []
    return _parse_news(data)


def get_latest_indicator_value(function: str) -> dict | None:
    if function not in ECONOMIC_INDICATORS:
        raise ValueError(f"Unsupported economic indicator: {function}")

    data = _get({"function": function})
    if not data:
        return None

    series = data.get("data", [])
    if not series:
        return None

    return series[0]
