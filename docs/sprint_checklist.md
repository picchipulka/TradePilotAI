# TradePilotAI Sprint Checklist

---

# Sprint 1 – Foundation ✅

## Objective

Build a reliable foundation for the application.

### Database

* [x] Create Supabase project
* [x] Create watchlist table
* [x] Import watchlist
* [x] Remove duplicate imports
* [x] Verify 13 watchlist entries

### Development Environment

* [x] Install Cursor
* [x] Create project structure
* [x] Configure Python
* [x] Configure virtual environment (optional for now)

### Security

* [x] Create `.env`
* [x] Store Supabase credentials
* [x] Add `.gitignore`
* [x] Prevent secrets from entering Git

### Connectivity

* [x] Connect Python to Supabase
* [x] Read watchlist
* [x] Display watchlist

### Reliability

* [x] Handle invalid API key
* [x] Handle missing configuration
* [x] Handle Supabase query errors
* [x] Fix Row Level Security policy

### Documentation

* [x] Debug log
* [x] Roadmap
* [x] Architecture
* [x] Sprint checklist

Status:
✅ COMPLETE

---

# Sprint 2 – Live Market Data

## Objective

Connect the watchlist to live market prices.

### Market Service

* [ ] Select market data provider
* [ ] Create Market Service
* [ ] Retrieve one ticker successfully
* [ ] Handle invalid ticker
* [ ] Handle API/network failures

### Scanner

* [ ] Read watchlist
* [ ] Retrieve live prices
* [ ] Compare against buy range
* [ ] Determine:

  * BELOW
  * IN RANGE
  * ABOVE
  * UNKNOWN

### Output

* [ ] Display current price
* [ ] Display buy range
* [ ] Display status

### Reliability

* [ ] Retry transient failures
* [ ] Handle missing prices gracefully
* [ ] Validate ticker format

### Documentation

* [ ] Update debug log
* [ ] Update architecture
* [ ] Update roadmap

Definition of Done:

* Every watchlist stock has a live price or a clear error.
* Status is correct.
* No crashes.

---

# Sprint 3 – Notifications

## Objective

Notify the user when a stock enters its range.

### Features

* [ ] Desktop notifications
* [ ] Duplicate alert prevention
* [ ] Alert history
* [ ] Cooldown timer

Definition of Done:
One alert per qualifying event.

---

# Sprint 4 – AI Context

## Objective

Explain *why* a stock matters.

### Features

* [ ] Load trade thesis
* [ ] Load conviction
* [ ] Earnings awareness
* [ ] Market context
* [ ] AI-generated explanation

Definition of Done:
Every alert includes reasoning and risks, not just a price.

---

# Sprint 5 – Dashboard

## Objective

Provide a single place to monitor trading.

### Features

* [ ] Watchlist
* [ ] Alerts
* [ ] Portfolio
* [ ] AI Notes
* [ ] Trade history

Definition of Done:
Dashboard updates correctly from live data.

---

# Sprint 6 – Learning Engine

## Objective

Help improve trading decisions over time.

### Features

* [ ] Track completed trades
* [ ] Record outcomes
* [ ] Measure win/loss statistics
* [ ] Analyze mistakes
* [ ] Suggest improvements

Definition of Done:
TradePilotAI can review historical trades and provide insights.


# Sprint 2 – Live Market Scanner ✅

## Objective
Connect watchlist tickers to live/latest market prices and determine whether each ticker is below, inside, or above the planned buy range.

## Completed
- [x] Added market data dependency
- [x] Created market data service using yfinance
- [x] Retrieved latest available price
- [x] Created scanner module
- [x] Added range status logic
- [x] Connected scanner output to app.py
- [x] Verified all 13 watchlist tickers scan successfully

## Status
✅ COMPLETE