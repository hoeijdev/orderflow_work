from turtle import pos

import pandas as pd

# from pandas.core.apply import ResType
# from pandas.core.groupby.indexing import PositionalIndexer
# from pandas.core.sorting import IndexKeyFunc
# from pandas.util.version import PrePostDevType


def load_metrics(csv_path):
    df = pd.read_csv(csv_path)
    df["buy_volume"] = df.apply(
        lambda row: row["volume"] if row["side"] == "buy" else 0, axis=1
    )
    df["sell_volume"] = df.apply(
        lambda row: row["volume"] if row["side"] == "sell" else 0, axis=1
    )
    df["volume_delta"] = df["buy_volume"] - df["sell_volume"]
    df["cvd"] = df["volume_delta"].cumsum()
    window = 50
    buy_sum = df["buy_volume"].rolling(window=window).sum()
    sell_sum = df["sell_volume"].rolling(window=window).sum()
    total_vol = buy_sum + sell_sum
    df["order_imbalance"] = (buy_sum - sell_sum) / total_vol
    return df


def run_signal_backtest(
    df, signal_func, name="signal", results_csv="trade_results.csv"
):
    df[name] = df.apply(signal_func, axis=1)
    trades = []
    position = 0  # 1 = long, -1 = short, 0 = flat
    trade_pnl = []
    entry_price = 0
    last_price = None
    trade_records = []

    for idx, row in df.iterrows():
        price = row["price"]
        signal = row[name]
        last_price = price
        timestamp = row.get("datetime", idx)

        if signal == 1 and position == 0:
            position = 1
            entry_price = price
            entry_time = timestamp
        elif signal == -1 and position == 0:
            position = -1
            entry_price = price
            entry_time = timestamp
        elif signal == 0 and position != 0:
            pnl = price - entry_price
            trade_records.append(
                {
                    "entry_time": entry_time,
                    "entry_price": entry_price,
                    "exit_time": timestamp,
                    "exit_price": price,
                    "side": "long",
                    "pnl": pnl,
                }
            )
            position = -1
            entry_price = price
            entry_time = timestamp
        elif signal == 1 and position == -1:
            pnl = price - entry_price
            trade_records.append(
                {
                    "entry_time": entry_time,
                    "entry_price": entry_price,
                    "exit_time": timestamp,
                    "exit_price": price,
                    "side": "long",
                    "pnl": pnl,
                }
            )
            position = 1
            entry_price = price
            entry_time = timestamp

        if position != 0 and last_price is not None:
            side = "long" if position == 1 else "short"
            pnl = (
                (last_price - entry_price)
                if position == 1
                else (entry_price - last_price)
            )
            trade_records.append(
                {
                    "entry_time": entry_time,
                    "entry_price": entry_price,
                    "exit_time": timestamp,
                    "exit_price": last_price,
                    "side": side,
                    "pnl": pnl,
                }
            )
            trades_df = pd.DataFrame(trade_records)
            trades_df.to_csv(results_csv, index=False)
            print(f"Saved {len(trade_records)} trades to {results_csv}")
            print(trades_df.head())


def imbalance_signal(row):
    if row["order_imbalance"] > 0.2:
        return 1  # buy signal
    elif row["order_imbalance"] < -0.2:
        return -1  # sell signal
    else:
        return 0  # no signal


def cvd_reversal_signal(row, prev_cvd=[0]):
    signal = 0
    if row["cvd"] > prev_cvd[0] and prev_cvd[0] < 0:
        signal = 1
    elif row["cvd"] < prev_cvd[0] and prev_cvd[0] > 0:
        signal = -1
    prev_cvd[0] = row["cvd"]
    return signal


if __name__ == "__main__":
    path = "kraken_BTC_EUR_trades_20251120_181231.csv"
    df = load_metrics(path)
    print("Order Imbalance Backtest")
    run_signal_backtest(df, imbalance_signal, name="imbalance_sig")
results_csv = "btc_usd_trade_results.csv"

print(df["imbalance_sig"].value_counts())
print(trade_pnl)
