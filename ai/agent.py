import json
import os
from dataclasses import asdict, dataclass

from anthropic import Anthropic
from dotenv import load_dotenv

from database.supabase import WatchlistEntry
from market.alpha_vantage import (
    ECONOMIC_INDICATORS,
    get_latest_indicator_value,
    get_macro_news,
    get_stock_news,
)
from market.market_data import get_current_price

load_dotenv()

DEFAULT_MODEL = "claude-opus-4-8"

THESIS_STATUSES = ("Valid", "Partially Valid", "Weakening", "Invalid", "Insufficient Data")

SYSTEM_PROMPT = """You are the independent AI analyst inside TradePilotAI.

TradePilotAI is not an automated trading bot: you never place trades and you \
never simply confirm the user's opinion. For every thesis you review you must:

- Build your own thesis independently from the evidence given. Do not inherit \
or copy the user's reasoning.
- Actively search the supplied evidence for anything that CONTRADICTS the \
thesis, not just evidence that supports it.
- Separate facts (price, volume, news, macro data) from opinions (bullish/\
bearish conclusions, confidence).
- Classify the thesis as exactly one of: Valid, Partially Valid, Weakening, \
Invalid, Insufficient Data.
- Give an independent AI conviction score from 1-10 based only on current \
evidence, never on the user's stated confidence.
- Weigh broader market conditions, sector news, stock-specific news, and \
macro events (FOMC meetings, CPI, PPI, jobs reports, market sell-offs, sector \
rotation) alongside the price/technical data.
- Explain your reasoning clearly enough that a human could evaluate whether \
they agree with you.

Report your review using the submit_thesis_review tool."""

SUBMIT_THESIS_REVIEW_TOOL = {
    "name": "submit_thesis_review",
    "description": "Submit the independent AI thesis review for a watchlist ticker.",
    "strict": True,
    "input_schema": {
        "type": "object",
        "properties": {
            "ai_thesis": {
                "type": "string",
                "description": "The AI's own independent thesis on this ticker, in 2-4 sentences.",
            },
            "ai_conviction": {
                "type": "integer",
                "description": "Independent AI conviction score, 1 (very low) to 10 (very high).",
            },
            "thesis_status": {
                "type": "string",
                "enum": list(THESIS_STATUSES),
                "description": "How the user's original thesis holds up against current evidence.",
            },
            "supporting_evidence": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Concrete facts that support the thesis.",
            },
            "contradicting_evidence": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Concrete facts that contradict or weaken the thesis.",
            },
            "risks": {
                "type": "array",
                "items": {"type": "string"},
                "description": "What could go wrong; upcoming events that increase uncertainty.",
            },
            "reasoning": {
                "type": "string",
                "description": "Explanation of how the evidence led to the conviction score and status.",
            },
        },
        "required": [
            "ai_thesis",
            "ai_conviction",
            "thesis_status",
            "supporting_evidence",
            "contradicting_evidence",
            "risks",
            "reasoning",
        ],
        "additionalProperties": False,
    },
}


@dataclass
class AIThesisReview:
    ai_thesis: str
    ai_conviction: int
    thesis_status: str
    supporting_evidence: list[str]
    contradicting_evidence: list[str]
    risks: list[str]
    reasoning: str


def build_context(entry: WatchlistEntry, current_price: float | None) -> dict:
    stock_news = get_stock_news(entry.Ticker)
    macro_news = get_macro_news()
    spy_price = get_current_price("SPY")

    macro_indicators = {}
    for indicator in ECONOMIC_INDICATORS:
        value = get_latest_indicator_value(indicator)
        if value is not None:
            macro_indicators[indicator] = value

    return {
        "ticker": entry.Ticker,
        "current_price": current_price,
        "buy_zone": {"low": entry.Buy_Range_low, "high": entry.Buy_Range_high},
        "stop_loss": entry.Stop_loss,
        "stock_news": [asdict(item) for item in stock_news[:5]],
        "macro_news": [asdict(item) for item in macro_news[:5]],
        "macro_indicators": macro_indicators,
        "market_trend": {"spy_price": spy_price},
    }


def review_thesis(entry: WatchlistEntry, current_price: float | None) -> AIThesisReview | None:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("AI review skipped: ANTHROPIC_API_KEY not set in .env")
        return None

    model = os.getenv("CLAUDE_MODEL", DEFAULT_MODEL)
    context = build_context(entry, current_price)

    client = Anthropic(api_key=api_key)

    try:
        response = client.messages.create(
            model=model,
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            tools=[SUBMIT_THESIS_REVIEW_TOOL],
            tool_choice={"type": "tool", "name": "submit_thesis_review"},
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Review this trade thesis using the evidence below. "
                        "Call submit_thesis_review with your independent review.\n\n"
                        f"{json.dumps(context, indent=2)}"
                    ),
                }
            ],
        )
    except Exception as exc:
        print(f"AI review failed for {entry.Ticker}: {exc}")
        return None

    tool_use = next((b for b in response.content if b.type == "tool_use"), None)
    if tool_use is None:
        print(f"AI review failed for {entry.Ticker}: no tool_use block in response")
        return None

    result = tool_use.input
    return AIThesisReview(
        ai_thesis=result["ai_thesis"],
        ai_conviction=int(result["ai_conviction"]),
        thesis_status=result["thesis_status"],
        supporting_evidence=result["supporting_evidence"],
        contradicting_evidence=result["contradicting_evidence"],
        risks=result["risks"],
        reasoning=result["reasoning"],
    )
