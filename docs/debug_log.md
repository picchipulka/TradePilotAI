# TradePilotAI Debug Log

## Issue 1: Supabase Invalid API Key

### Problem
Running `python app.py` returned:

Invalid API key / 401 error

### Cause
`.env` had a placeholder key instead of the real Supabase Publishable Key.

### Fix
Updated `.env`:

SUPABASE_URL=https://newvlxrnxytvegoiertj.supabase.co
SUPABASE_KEY=real_supabase_publishable_key

### Status
Fixed.

---

## Issue 2: App ran but printed no watchlist rows

### Problem
`python app.py` ran without error but returned 0 rows.

### Cause
Supabase Row Level Security blocked public read access using the publishable key.

### Fix
Created SELECT/read policy on table:

"Stock screener watchlist"

Policy:

FOR SELECT
USING (true)

### Status
Fixed.

---

## Notes
- Supabase read policy remains active until manually changed or deleted.
- Do not commit `.env` to GitHub.
- Keep `.env` inside `.gitignore`.

## Milestone 1: Supabase connection successful

### Result
`python app.py` successfully returned 13 watchlist entries.

### Confirmed tickers
AMTM, ONDS, NOK, CLSK, HLIT, HOOD, RBRK, GLW, AAOI, ANET, PLTR, RBLX, APLD

### Status
Completed.