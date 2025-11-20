from datetime import datetime

import pandas as pd
import requests


def fetch_kraken_trades(pair: str = "XXBTZUSD", limit: int = 1000):
    """
    Fetch recent trades from Kraken public API

    Note: Kraken API returns ~1000 max (no limit parameter supported)

    Args:
        pair (str): Trading pair (default: 'XXBTZUSD')

    Returns: pandas DataFrame with columns ['time', 'price', 'volume', 'side']
    """

    url = f"https://api.kraken.com/0/public/Trades?pair={pair}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if data.get("error"):
            raise Exception(f"Kraken API error: {data['error']}")

        trades_raw = data["result"][pair]

        trades = [
            {
                "time": float(tr[2]),
                "price": float(tr[0]),
                "volume": float(tr[1]),
                "side": "buy" if tr[3] == "b" else "sell",
            }
            for tr in trades_raw
        ]

        df = pd.DataFrame(trades)
        df["datetime"] = pd.to_datetime(df["time"], unit="s")

        return df

    except Exception as e:
        print(f"Error fetching Kraken trades: {e}")
        return None


def save_trades_csv(df, pair: str = "BTC", timestamp: bool = True):
    """Save trades to CSV file"""
    if df is None or df.empty:
        print("No trades to save")
        return

    if timestamp:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = f"kraken_{pair}_trades_{ts}.csv"
    else:
        filepath = f"kraken_{pair}_trades.csv"

    df.to_csv(filepath, index=False)
    print(f"Saved {len(df)} trades to {filepath}")

if __name__ == "__main__":
    pairs = [
        ("XXBTZUSD", "BTC_USD"),
        ("XETHZUSD", "ETH_USD"),
        ("XXBTZEUR", "BTC_EUR"),
        ("XETHZEUR", "ETH_EUR")
    ]

    for kraken_pair, save_name in pairs:
        print(f"\nFetching {save_name}...")
        df = fetch_kraken_trades(pair=kraken_pair)

        if df is not None:
            print(f"Fetched {len(df)} trades")
            save_trades_csv(df, pair=save_name)
        else:
            print(f"Failed to fetch {save_name}")
