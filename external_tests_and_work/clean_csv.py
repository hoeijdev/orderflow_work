import pandas as pd


def clean_trade_csv(file_path):
    """
    Clean and reformat a messy trade CSV file.

    Args:
        filepath: Path to the trade CSV file.
    """

    # read the CSV file
    df = pd.read_csv(file_path)

    # Format columns
    df["price"] = df["price"].round(2)
    df["volume"] = df["volume"].round(6)

    if "datetime" in df.columns:
        df["datetime"] = pd.to_datetime(df["datetime"])

    column_order = ["datetime", "price", "volume", "side"]
    df = df[column_order]

    clean_filepath = file_path.replace(".csv", "_clean.csv")
    df.to_csv(clean_filepath, index=False)
    print(f"Cleaned file saved to: {clean_filepath}")

    return df
