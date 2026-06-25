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


# Sprint 3 – Intelligent Alert Engine

## Objective

Transform TradePilotAI from a passive scanner into an active trading assistant by generating alerts only when a stock enters the predefined buy zone.

---

## Sprint 3A – Alert Trigger (Console)

### Goal

Generate an alert whenever a stock is detected inside the configured buy range.

### Tasks

* [ ] Detect when a stock status is `IN RANGE`.
* [ ] Print a clear alert message to the console.
* [ ] Include:

  * Ticker
  * Current Price
  * Buy Range
  * Stop Loss (if available)
* [ ] Continue displaying the full scanner output for development purposes.

### Deliverable

Example:

```
==================================
🚨 BUY ALERT 🚨

Ticker: PLTR
Current Price: 123.10
Buy Zone: 122 - 127
Status: IN RANGE

==================================
```

---

## Sprint 3B – Desktop Notification

### Goal

Display a native Windows notification whenever a buy alert is triggered.

### Tasks

* [ ] Create a notification service in `alerts/notifier.py`.
* [ ] Trigger the notification only for `IN RANGE` stocks.
* [ ] Notification should include:

  * Ticker
  * Current Price
  * Buy Range

### Deliverable

Windows notification example:

```
TradePilotAI

PLTR has entered your buy zone.

Current Price: 123.10
```

---

## Sprint 3C – Duplicate Alert Prevention

### Goal

Prevent TradePilotAI from repeatedly notifying while a stock remains inside the buy zone.

### Tasks

* [ ] Track whether an alert has already been sent.
* [ ] Send only one alert when entering the range.
* [ ] Reset the alert state once the stock exits the buy zone.
* [ ] Allow a new alert only after the stock re-enters.

### Expected Behavior

```
PLTR enters range
↓
Alert sent

PLTR remains in range
↓
No additional alerts

PLTR leaves range
↓
Alert state resets

PLTR re-enters range
↓
New alert sent
```

---

## Sprint 3 Success Criteria

* [ ] Scanner automatically detects stocks entering the buy range.
* [ ] Console alerts generated successfully.
* [ ] Desktop notifications working.
* [ ] No duplicate notifications while a stock remains inside the range.
* [ ] Alert state resets correctly after exiting the range.

---

## Out of Scope

The following features are intentionally deferred to future sprints:

* AI thesis validation
* AI conviction score
* WhatsApp / SMS / Email notifications
* Knowledge Graph
* Historical event tracking
* Multi-provider market data (Polygon, Alpaca)
* Alert prioritization and ranking

---

## Sprint Status

**Status:** ⏳ Planned
