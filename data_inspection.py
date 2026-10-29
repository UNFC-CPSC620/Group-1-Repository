import pandas as pd
from pathlib import Path


def load_dataset(file_path="Airbnb_NYC.csv"):
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {file_path}")

    return pd.read_csv(path)


def inspect_dataset(df):
    print("Dataset dimensions:")
    print(f"Rows: {df.shape[0]}")
    print(f"Columns: {df.shape[1]}")

    print("\nColumn names and data types:")
    print(df.dtypes)

    print("\nMissing values by column:")
    print(df.isnull().sum())

    print("\nDuplicate rows:")
    print(df.duplicated().sum())

    if "id" in df.columns:
        print("Duplicate listing IDs:")
        print(df["id"].duplicated().sum())
    elif "listing_id" in df.columns:
        print("Duplicate listing IDs:")
        print(df["listing_id"].duplicated().sum())

    print("\nDataset preview:")
    print(df.head())


if __name__ == "__main__":
    dataset = load_dataset()
    inspect_dataset(dataset)
