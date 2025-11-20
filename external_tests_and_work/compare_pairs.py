from sqlite3 import dbapi2

import matplotlib.pyplot as plt
import pandas as pd


def load_and_calculate(csv_path, window=50):
    """Load CSV file and calculate CVD + order imbalance"""
    df = pd.read_csv(csv_path)

    # bereken buy/sell volumes
    df["buy_volume"] = df.apply(
        lambda row: row["volume"] if row["side"] == "buy" else 0, axis=1
    )
    df["sell_volume"] = df.apply(
        lambda row: row["volume"] if row["side"] == "sell" else 0, axis=1
    )

    df["volume_delta"] = df["buy_volume"] - df["sell_volume"]
    df["cvd"] = df["volume_delta"].cumsum()

    buy_sum = df["buy_volume"].rolling(window).sum()
    sell_sum = df["sell_volume"].rolling(window).sum()
    total_vol = buy_sum + sell_sum
    df["order_imbalance"] = (buy_sum - sell_sum) / total_vol

    print(f"\n{csv_path}:")
    print(f"Buy trades: {(df['side'] == 'buy').sum()}")
    print(f"Sell trades: {(df['side'] == 'sell').sum()}")
    print(
        f"Order imbalance range: {df['order_imbalance'].min():.3f} to {df['order_imbalance'].max():.3f}"
    )

    return df


if __name__ == "__main__":
    btc_usd = load_and_calculate("kraken_BTC_USD_trades_20251120_181231.csv")
    eth_usd = load_and_calculate("kraken_ETH_USD_trades_20251120_181231.csv")
    eth_eur = load_and_calculate("kraken_ETH_EUR_trades_20251120_181231.csv")
    btc_eur = load_and_calculate("kraken_BTC_EUR_trades_20251120_181231.csv")

    fig, axes = plt.subplots(3, 2, figsize=(14, 10))

    # BTC/USD
    axes[0, 0].plot(btc_usd["cvd"], label="CVD")
    axes[0, 0].plot(btc_usd["order_imbalance"], label="Order Imbalance")
    axes[0, 0].set_title("BTC/USD")
    axes[0, 0].legend()

    # ETH/USD
    axes[0, 1].plot(eth_usd["cvd"], label="CVD")
    axes[0, 1].plot(eth_usd["order_imbalance"], label="Order Imbalance")
    axes[0, 1].set_title("ETH/USD")
    axes[0, 1].legend()

    # ETH/EUR
    axes[1, 0].plot(eth_eur["cvd"], label="CVD")
    axes[1, 0].plot(eth_eur["order_imbalance"], label="Order Imbalance")
    axes[1, 0].set_title("ETH/EUR")
    axes[1, 0].legend()

    # BTC/EUR
    axes[1, 1].plot(btc_eur["cvd"], label="CVD")
    axes[1, 1].plot(btc_eur["order_imbalance"], label="Order Imbalance")
    axes[1, 1].set_title("BTC/EUR")
    axes[1, 1].legend()

    plt.tight_layout()
    plt.savefig("orderflow_comparison.png", dpi=150)
    print("Chart saved as orderflow_comparison.png")
    plt.show()
