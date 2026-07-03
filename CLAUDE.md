# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

TradePilotAI is a personal trading decision-support tool, explicitly **not** an automated trading bot. It watches a list of tickers against user-defined buy zones/stop losses and fires desktop notifications when a thesis-relevant price event occurs. The AI never places trades — every design decision should preserve that boundary. Full philosophy is in `docs/guiding_principles.md` and `docs/trade_thesis_specification.md`; read those before adding features that touch alerting or "recommendation" behavior.

The project is mid-roadmap (Sprint 4 – AI Context underway, see `docs/roadmap.md`), single-user, run locally on Windows, no test suite yet.

## Commands

```
pip install -r requirements.txt      # install deps (supabase, python-dotenv, requests, pandas, yfinance, anthropic)
python app.py                        # run the continuous scanner (main entry point)
start_tradepilot.bat                 # same, double-clickable on Windows
```

There is no test runner, linter, or formatter configured yet (see `docs/future_enhancements.md` FE-004). There's no build step — this is plain Python, run directly.

Requires a `.env` file (gitignored) with:
- `SUPABASE_URL`, `SUPABASE_KEY` — watchlist database
- `ANTHROPIC_API_KEY`, optional `CLAUDE_MODEL` (defaults to `claude-opus-4-8`) — AI thesis review
- `ALPHA_VANTAGE_API_KEY` — news/macro data feeding the AI review
- `CALLMEBOT_TELEGRAM_USER` (e.g. `@yourusername`) — Telegram notifications via CallMeBot

Missing/invalid values are handled gracefully (empty watchlist, skipped AI review, skipped notification + printed error) rather than a hard crash.

GitHub Actions is wired up (`.github/workflows/claude.yml`, `claude-code-review.yml`) for Claude PR assistance and automated code review on this repo.

## Architecture

Data flow (see `docs/architecture.md` for the original diagram; AI review and Telegram are newer additions):

```
Supabase (watchlist table) -> scanner -> alert state machine -> [AI thesis review] -> notifier (Telegram via CallMeBot)
```

- `database/supabase.py` — reads the watchlist table (hardcoded name `"Stock screener watchlist"`, see FE-001/FE-002) into `WatchlistEntry` dataclasses (`Ticker`, `Buy_Range_low`, `Buy_Range_high`, `Stop_loss`). Swallows Supabase/config errors and returns `[]` rather than raising.
- `market/market_data.py` — `get_current_price(ticker)` wraps `yfinance`, returns `float | None`. Yahoo Finance is an intentionally temporary provider (see `docs/decisions.md` Decision #1) — expect this to move behind a `MarketService` abstraction (FE-009) supporting Polygon/Alpaca later.
- `market/alpha_vantage.py` — Alpha Vantage client feeding the AI review: `get_stock_news`/`get_macro_news` (`NEWS_SENTIMENT`) and `get_latest_indicator_value` for `ECONOMIC_INDICATORS` (CPI, unemployment, nonfarm payroll, fed funds rate). Returns `[]`/`None` on missing key, rate limit, or request failure — never raises.
- `scanner/scanner.py` — pure functions, no I/O:
  - `get_range_status` -> `BELOW` / `IN RANGE` / `ABOVE` / `UNKNOWN` (simple price-vs-buy-range comparison, used for display)
  - `get_zone` -> `ABOVE_BUY_ZONE` / `IN_BUY_ZONE` / `BELOW_BUY_ZONE` / `STOP_ZONE` / `UNKNOWN` (the richer state used to drive alerts)
- `alerts/alert_state.py` — in-memory (per-process, not persisted) map of ticker -> current state (`ABOVE_BUY_ZONE` / `IN_BUY_ZONE` / `BELOW_BUY_ZONE` / `STOP_ZONE` / `RECOVERING_TO_BUY_ZONE`). Process restart resets all state.
- `alerts/notifier.py` — `send_notification(...)` sends a Telegram message via the CallMeBot API (`requests.get` to `api.callmebot.com`); no-ops with a printed message if `CALLMEBOT_TELEGRAM_USER` isn't set or price data is missing.
- `ai/agent.py` — `review_thesis(entry, current_price)` calls Claude (via `anthropic` SDK) with a forced tool call (`submit_thesis_review`) to produce an independent `AIThesisReview`: its own thesis, a 1-10 conviction score, a `thesis_status` (Valid/Partially Valid/Weakening/Invalid/Insufficient Data), supporting/contradicting evidence, risks, and reasoning. `build_context()` assembles the evidence package (stock news, macro news, macro indicators, SPY price) from `market/alpha_vantage.py` and `market/market_data.py`. The system prompt (see `SYSTEM_PROMPT`) is the code-level enforcement of `docs/guiding_principles.md` Principles 3/9/10/11 — it must never be softened into "agree with the user." No-ops (returns `None`) if `ANTHROPIC_API_KEY` is unset or the API call fails.
- `app.py` — orchestrates everything: `run_scan_once()` pulls the watchlist, scans each entry, sorts by distance to buy zone, prints a console summary, and calls `_process_alert()` per entry to drive the zone state machine and trigger alerts. Alerts whose title is in `AI_REVIEW_ALERT_TITLES` (BUY ALERT, DECISION ALERT — the two thesis-lifecycle-significant events) additionally call `review_thesis()` and append the AI's independent verdict to the notification. `main()` loops every `SCAN_INTERVAL_SECONDS` (60s), only during `market_monitoring_hours()` (Mon-Fri, 4am-8pm local).
- `watchlist/watchlist.py` is currently an empty placeholder — don't assume behavior from its existence.

### Alert state machine (app.py `_process_alert`)

This is edge-triggered against `docs/Trade_alert_state_diagram.png` — read that diagram before touching this function. The scanner's `get_zone()` output doesn't map 1:1 to alert state: `BELOW_BUY_ZONE` splits into two distinct alert states depending on history —
- Falling from `IN_BUY_ZONE` -> `BELOW_BUY_ZONE`: fires "exited below buy zone, heading toward stop"
- Recovering from `STOP_ZONE` -> `BELOW_BUY_ZONE`: becomes `RECOVERING_TO_BUY_ZONE`, fires "heading back toward buy range low" instead

The critical invariant (Rule 6): if `RECOVERING_TO_BUY_ZONE` re-enters `IN_BUY_ZONE`, **no** BUY alert fires — that's a recovery back to the zone the user already knows about, not a new opportunity. Preserve this when modifying alert logic; it was a deliberate fix, not an oversight.

## Conventions worth knowing

- Modules are intentionally decoupled: `scanner` has no I/O, and `market_data`/`alpha_vantage`/`database`/`notifier`/`ai` each own exactly one external dependency; `app.py` is the only place that wires them together. Keep new code in the module matching its single responsibility rather than adding logic to `app.py`.
- Failures degrade gracefully (return `None`/`[]`/print a message) rather than raising, all the way up the stack — matches `docs/architecture.md`'s "handle failures gracefully" principle.
- The AI is an *independent* reviewer, not a rubber stamp — this is a hard product requirement (`docs/guiding_principles.md` Principles 3, 9, 10, 11), not a style preference. Any change to `ai/agent.py`'s prompt or schema must keep forcing the model to state contradicting evidence and an independent conviction score, never just validate the user's stated thesis.
- `docs/future_enhancements.md` is the running backlog/tech-debt log (FE-### items) — check it before assuming something (e.g. hardcoded table name, print-based logging, lack of tests) is an oversight rather than a known, deferred tradeoff.
- `docs/decisions.md` is an ADR-style log; add an entry there for any non-obvious architectural choice.
