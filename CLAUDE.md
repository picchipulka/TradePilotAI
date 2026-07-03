# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

TradePilotAI is a personal trading decision-support tool, explicitly **not** an automated trading bot. It watches a list of tickers against user-defined buy zones/stop losses and fires desktop notifications when a thesis-relevant price event occurs. The AI never places trades — every design decision should preserve that boundary. Full philosophy is in `docs/guiding_principles.md` and `docs/trade_thesis_specification.md`; read those before adding features that touch alerting or "recommendation" behavior.

The project is early-stage (Sprint 3 of the roadmap in `docs/roadmap.md`), single-user, run locally on Windows, no test suite yet.

## Commands

```
pip install -r requirements.txt      # install deps (supabase, python-dotenv, requests, pandas, yfinance, winotify)
python app.py                        # run the continuous scanner (main entry point)
start_tradepilot.bat                 # same, double-clickable on Windows
```

There is no test runner, linter, or formatter configured yet (see `docs/future_enhancements.md` FE-004). There's no build step — this is plain Python, run directly.

Requires a `.env` file (gitignored) with `SUPABASE_URL` and `SUPABASE_KEY`. Missing/invalid values are handled gracefully (empty watchlist + printed error), not a hard crash.

## Architecture

Data flow (see `docs/architecture.md` for the full diagram):

```
Supabase (watchlist table) -> scanner -> alert state machine -> notifier (Windows toast)
```

- `database/supabase.py` — reads the watchlist table (hardcoded name `"Stock screener watchlist"`, see FE-001/FE-002) into `WatchlistEntry` dataclasses (`Ticker`, `Buy_Range_low`, `Buy_Range_high`, `Stop_loss`). Swallows Supabase/config errors and returns `[]` rather than raising.
- `market/market_data.py` — `get_current_price(ticker)` wraps `yfinance`, returns `float | None`. Yahoo Finance is an intentionally temporary provider (see `docs/decisions.md` Decision #1) — expect this to move behind a `MarketService` abstraction (FE-009) supporting Polygon/Alpaca later. Don't assume `yfinance` is permanent when designing new market-data code.
- `scanner/scanner.py` — pure functions, no I/O:
  - `get_range_status` -> `BELOW` / `IN RANGE` / `ABOVE` / `UNKNOWN` (simple price-vs-buy-range comparison, used for display)
  - `get_zone` -> `ABOVE_BUY_ZONE` / `IN_BUY_ZONE` / `BELOW_BUY_ZONE` / `STOP_ZONE` / `UNKNOWN` (the richer state used to drive alerts)
- `alerts/alert_state.py` — in-memory (per-process, not persisted) state machine tracking last zone per ticker and which alert types have already fired, so `app.py` can debounce repeat notifications. Sprint 3 introduced this; process restart resets all state.
- `alerts/notifier.py` — `send_notification(...)` fires a Windows toast via `winotify`; no-ops safely if `winotify` isn't available or price data is missing.
- `app.py` — orchestrates everything: `run_scan_once()` pulls the watchlist, scans each entry, sorts by distance to buy zone, prints a console summary, and calls `_process_alert()` per entry to drive the zone state machine and trigger alerts. `main()` loops every `SCAN_INTERVAL_SECONDS` (60s), only during `market_monitoring_hours()` (Mon-Fri, 4am-8pm local).
- `ai/agent.py` and `watchlist/watchlist.py` are currently empty placeholders for future sprints (AI reasoning, watchlist management) — don't assume behavior from their existence.

### Alert zone transitions (app.py `_process_alert`)

The zone state machine (not just the current zone) determines whether an alert fires — it looks at `last_zone -> current_zone` transitions:
- `IN_BUY_ZONE` (and not yet alerted) -> BUY alert, resets below/stop/recovery flags
- `IN_BUY_ZONE -> BELOW_BUY_ZONE` (and not yet alerted) -> "exited below buy zone" alert
- `BELOW_BUY_ZONE -> STOP_ZONE` (and not yet alerted) -> "entered stop zone" alert
- `STOP_ZONE -> BELOW_BUY_ZONE` (and not yet alerted) -> "heading back toward buy range" recovery alert

When modifying alert logic, preserve the "one alert per qualifying transition, reset on zone exit" behavior — this was a specific Sprint 3 goal (see `docs/sprint_checklist.md`).

## Conventions worth knowing

- Modules are intentionally decoupled: `scanner` has no I/O, `market_data`/`database`/`notifier` each own exactly one external dependency, and `app.py` is the only place that wires them together. Keep new code in the module matching its single responsibility rather than adding logic to `app.py`.
- Failures degrade gracefully (return `None`/`[]`/print a message) rather than raising, all the way up the stack — matches `docs/architecture.md`'s "handle failures gracefully" principle.
- `docs/future_enhancements.md` is the running backlog/tech-debt log (FE-### items) — check it before assuming something (e.g. hardcoded table name, print-based logging, lack of tests) is an oversight rather than a known, deferred tradeoff.
- `docs/decisions.md` is an ADR-style log; add an entry there for any non-obvious architectural choice.
