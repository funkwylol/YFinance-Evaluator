import os
import json
import yfinance as yf

def fetch_and_save(ticker_symbol: str = "MSFT", filename: str = "MSFT_Data.json", history_period: str = "1mo") -> str:
    """Fetch data for `ticker_symbol` using yfinance and save serializable JSON to `filename`.

    The saved JSON contains two keys:
      - info: the dictionary returned by Ticker.info
      - history: a list of historical rows (each row is a dict); dates are ISO strings

    Returns the path to the written file.
    """
    t = yf.Ticker(ticker_symbol)
    out = {"info": {}, "history": []}

    # Safely get info (may raise network / parsing errors)
    try:
        out["info"] = t.info or {}
    except Exception:
        out["info"] = {}

    # Get history and convert to list-of-dicts with ISO date strings for JSON
    try:
        hist = t.history(period=history_period)
        if not hist.empty:
            hist_reset = hist.reset_index()
            # first column is usually the datetime index (e.g. 'Date') — convert values to ISO strings
            date_col = hist_reset.columns[0]
            try:
                hist_reset[date_col] = hist_reset[date_col].apply(lambda x: x.isoformat() if hasattr(x, 'isoformat') else x)
            except Exception:
                # fallback: leave values as-is
                pass
            out["history"] = hist_reset.to_dict(orient="records")
        else:
            out["history"] = []
    except Exception:
        out["history"] = []

    # Ensure directory exists
    dirpath = os.path.dirname(os.path.abspath(filename))
    if dirpath and not os.path.exists(dirpath):
        os.makedirs(dirpath, exist_ok=True)

    # Write JSON with pretty printing and UTF-8 encoding
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    return os.path.abspath(filename)


if __name__ == "__main__":
    out_path = fetch_and_save("MSFT", "MSFT_Data.json", history_period="1mo")
    print(f"Saved data to: {out_path}")
