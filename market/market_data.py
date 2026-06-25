import yfinance as yf


def get_current_price(ticker: str) -> float | None:
    if not ticker or not ticker.strip():
        print("Market data error: ticker is empty")
        return None

    symbol = ticker.strip().upper()

    try:
        data = yf.Ticker(symbol).history(period="5d")
        if data.empty:
            print(f"Market data error: no data returned for {symbol}")
            return None

        price = data["Close"].iloc[-1]
        if price != price:  # NaN check
            print(f"Market data error: latest close is NaN for {symbol}")
            return None

        return float(price)
    except Exception as exc:
        print(f"Market data error: failed to fetch price for {symbol} ({exc})")
        return None
