from pathlib import Path
import pandas as pd


GBP_TO_INR = 105.50

RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


def load_raw_data():
    """Load the raw book dataset created by the scraper."""

    input_file = Path(__file__).parent / "outputs" / "books_raw.csv"

    if not input_file.exists():
        raise FileNotFoundError(
            "books_raw.csv was not found. Run scraper.py first."
        )

    df = pd.read_csv(input_file)

    return df


def clean_books(df):
    """Clean and transform the raw book dataset."""

    df = df.copy()

    print(f"Rows before cleaning: {len(df)}")

    # 1. Convert price to numeric GBP value
    df["price_gbp"] = (
        df["price"]
        .astype(str)
        .str.replace("£", "", regex=False)
        .str.strip()
    )

    df["price_gbp"] = pd.to_numeric(
        df["price_gbp"],
        errors="coerce"
    )

    malformed_price_count = df["price_gbp"].isna().sum()

    print(
        f"Malformed/missing price values: "
        f"{malformed_price_count}"
    )

    if malformed_price_count > 0:
        df = df.dropna(subset=["price_gbp"]).copy()

    # 2. Convert textual star rating to integer
    df["rating"] = df["star_rating"].map(RATING_MAP)

    invalid_rating_count = df["rating"].isna().sum()

    print(
        f"Invalid/missing rating values: "
        f"{invalid_rating_count}"
    )

    if invalid_rating_count > 0:
        df = df.dropna(subset=["rating"]).copy()

    df["rating"] = df["rating"].astype(int)

    # 3. Convert availability to boolean
    df["in_stock"] = (
        df["availability"]
        .astype(str)
        .str.strip()
        .str.lower()
        .eq("in stock")
    )

    # 4. Convert GBP to INR using the fixed project rate
    df["price_inr"] = (
        df["price_gbp"] * GBP_TO_INR
    ).round(2)

    # 5. Keep final cleaned columns
    cleaned_columns = [
        "title",
        "price_gbp",
        "price_inr",
        "rating",
        "in_stock",
        "category",
    ]

    df = df[cleaned_columns]

    print(f"Rows after cleaning: {len(df)}")

    return df

def validate_clean_data(df):
    """Validate the cleaned dataset against project requirements."""

    # Dataset must still contain at least 60 books
    if len(df) < 60:
        raise ValueError(
            f"Cleaned dataset contains only {len(df)} rows. "
            "At least 60 books are required."
        )

    # price_gbp must not contain missing values
    if df["price_gbp"].isna().any():
        raise ValueError("price_gbp contains missing values.")

    # rating must not contain missing values
    if df["rating"].isna().any():
        raise ValueError("rating contains missing values.")

    # rating must be between 1 and 5
    if not df["rating"].between(1, 5).all():
        raise ValueError("Ratings must be between 1 and 5.")

    # Verify the fixed GBP → INR conversion
    expected_inr = (df["price_gbp"] * GBP_TO_INR).round(2)

    if not df["price_inr"].equals(expected_inr):
        raise ValueError(
            "price_inr does not match the fixed GBP to INR conversion."
        )

    print("Validation passed.")
def save_clean_data(df):
    """Save the cleaned dataset to a separate CSV file."""

    output_file = (
        Path(__file__).parent
        / "outputs"
        / "books_cleaned.csv"
    )

    df.to_csv(output_file, index=False)

    print(f"Cleaned dataset saved to: {output_file}")

def main():
    # Load raw data
    df = load_raw_data()

    # Clean and transform
    cleaned_df = clean_books(df)

    # Validate the cleaned data
    validate_clean_data(cleaned_df)

    # Save cleaned data
    save_clean_data(cleaned_df)

    print("\nCleaned dataset shape:")
    print(cleaned_df.shape)

    print("\nData types:")
    print(cleaned_df.dtypes)

    print("\nFirst 5 cleaned records:")
    print(cleaned_df.head())

    print("\nMissing values:")
    print(cleaned_df.isna().sum())


if __name__ == "__main__":
    main()