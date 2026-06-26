# TradePilotAI Future Enhancements & Technical Debt

This document captures improvements we intentionally defer so they are not forgotten.

---

# Sprint 1 Improvements

## FE-001: Rename Supabase table

### Current

`Stock screener watchlist`

### Proposed

`watchlist` or `trade_watchlist`

### Reason

Current table name has spaces and capitalization, which makes code and SQL more fragile.

### Priority

Medium

---

## FE-002: Move table name to environment variable

### Current

Table name is hardcoded in `database/supabase.py`.

### Proposed

Move to `.env`:

SUPABASE_WATCHLIST_TABLE=Stock screener watchlist

### Reason

Makes future table rename easier.

### Priority

Medium

---

## FE-003: Add structured logging

### Current

Uses `print()` for errors and output.

### Proposed

Use Python `logging`.

### Reason

Cleaner debugging, severity levels, easier production monitoring.

### Priority

Medium

---

## FE-004: Add automated tests

### Current

Testing is manual using:

python app.py

### Proposed

Add unit tests for:

* Supabase connection
* Watchlist parsing
* Price status logic
* Market data failures

### Priority

High before production use

---

## FE-005: Add Git/GitHub version control

### Current

Project is local only.

### Proposed

Initialize Git and push to GitHub with `.env` ignored.

### Reason

Rollback, history, safer Cursor experimentation.

### Priority

High before Sprint 3

---

## FE-006: Validate database rows

### Current

Missing ticker becomes empty string.

### Proposed

Skip invalid rows and report them clearly.

### Reason

Prevents silent bad data from entering scanner.

### Priority

Medium

---

## FE-007: Separate display logic from app.py

### Current

`app.py` formats output.

### Proposed

Move formatting to separate display/output module.

### Reason

Keeps app entry point simple.

### Priority

Low

---

# Sprint 2 Improvements

## FE-008: Use `math.isnan()` for NaN detection

### Current

Uses:

if price != price:

### Proposed

Use:

import math

if math.isnan(price):

### Reason

More readable and standard.

### Priority

Low

---

## FE-009: Add MarketService abstraction

### Current

App calls yfinance helper directly.

### Proposed

Create:

market/
market_service.py
providers/
yahoo_provider.py
polygon_provider.py
alpaca_provider.py

### Reason

Allows switching providers without changing scanner/app code.

### Priority

High before replacing Yahoo

---

## FE-010: Return PriceResult instead of float

### Current

`get_current_price()` returns `float | None`.

### Proposed

Return object with:

* price
* provider
* timestamp
* market_state
* error

### Reason

Needed for alerts and debugging.

### Priority

Medium

---

## FE-011: Add scanner module

### Current

Status logic lives in `app.py`.

### Proposed

Create:

scanner/scanner.py

Responsibilities:

* Compare price to buy range
* Return BELOW / IN RANGE / ABOVE / UNKNOWN

### Reason

Scanner will later include volume, earnings, market context, and AI review.

### Priority

High in Sprint 2B

---

## FE-012: Replace or supplement Yahoo with Polygon/Alpaca

### Current

Uses yfinance for quick validation.

### Proposed

Add Polygon or Alpaca provider.

### Reason

More reliable market data, better long-term provider support.

### Priority

Medium after architecture works

---

# General Engineering Rules

## 2-Minute Rule

If an improvement takes under 2 minutes and does not distract from the sprint, fix it now.

If not, document it here and continue.

## 10-Year Rule

Every file should be understandable within 2 minutes, even years later.

## Risk Rule

Any feature that can affect trading behavior must prioritize capital protection over excitement.

## FE-013: Sort scanner output by distance to buy zone

### Current
Scanner output prints tickers in database order.

### Proposed
Sort scanner output by closest distance to buy range.

### Reason
Useful for manual review, but not required for alert-based workflow.

The main product flow should notify only when a ticker enters range, so sorting all tickers is lower priority.

### Priority
Low

### Status
Deferred