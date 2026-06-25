# TradePilotAI Architecture

## Vision

TradePilotAI is not an automated trading bot.

It is an AI-powered trading assistant that helps review opportunities, remind the user of their own thesis, monitor market conditions, and surface relevant information before a trading decision.

Final trade decisions are always made by the user.

---

# High-Level Architecture

```
Google Sheet
        │
        ▼
Supabase Database
        │
        ▼
Watchlist Service
        │
 ┌──────┴─────────┐
 ▼                ▼
Market Service    AI Knowledge
 │                │
 ▼                ▼
Live Prices    Trade Thesis
 │                │
 └──────┬─────────┘
        ▼
Decision Engine
        │
        ▼
Notification Service
        │
        ▼
Desktop
WhatsApp
Email
Dashboard
```

---

## Design Principles

* Keep services independent.
* Avoid hardcoded values.
* Use environment variables for configuration.
* Handle failures gracefully.
* Every module should have one responsibility.
* AI should assist, not make trading decisions.
