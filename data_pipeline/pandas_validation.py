import sqlite3
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).parent
DB_FILE = BASE_DIR / "outputs" / "books.db"

VALIDATION_DIR = (
    BASE_DIR
    / "outputs"
    / "pandas_validation"
)
def load_sql_results(connection):
    """Load at least two SQL query results into pandas."""

    query_1 = """
        SELECT
            title,
            price_gbp,
            price_inr,
            rating
        FROM books
        ORDER BY price_gbp DESC
        LIMIT 10;
    """

    query_2 = """
        SELECT
            b.title,
            b.price_gbp,
            b.rating,
            c.category_name
        FROM books AS b
        JOIN categories AS c
            ON b.category_id = c.category_id
        WHERE c.category_name IN (
            'Fiction',
            'Mystery',
            'History'
        )
        ORDER BY c.category_name, b.title;
    """

    result_1 = pd.read_sql(
        query_1,
        connection
    )

    result_2 = pd.read_sql(
        query_2,
        connection
    )

    print("SQL result 1 loaded into pandas:")
    print(result_1)

    print("\nSQL result 2 loaded into pandas:")
    print(result_2)

    return result_1, result_2
def compare_sql_join_with_pandas(connection):
    """Compare an SQL JOIN with an equivalent pandas merge."""

    sql_join_query = """
        SELECT
            b.book_id,
            b.title,
            b.price_gbp,
            b.price_inr,
            b.rating,
            b.in_stock,
            c.category_name
        FROM books AS b
        JOIN categories AS c
            ON b.category_id = c.category_id
        ORDER BY b.book_id;
    """

    sql_join_df = pd.read_sql(
        sql_join_query,
        connection
    )

    books_df = pd.read_sql(
        "SELECT * FROM books;",
        connection
    )

    categories_df = pd.read_sql(
        "SELECT * FROM categories;",
        connection
    )

    pandas_merge_df = pd.merge(
        books_df,
        categories_df,
        on="category_id",
        how="inner"
    )

    pandas_merge_df = pandas_merge_df[
        [
            "book_id",
            "title",
            "price_gbp",
            "price_inr",
            "rating",
            "in_stock",
            "category_name",
        ]
    ]

    pandas_merge_df = (
        pandas_merge_df
        .sort_values("book_id")
        .reset_index(drop=True)
    )

    sql_join_df = sql_join_df.reset_index(drop=True)

    match = sql_join_df.equals(pandas_merge_df)

    print("\nSQL JOIN rows:", len(sql_join_df))
    print("Pandas merge rows:", len(pandas_merge_df))
    print(
        "SQL JOIN and pandas merge match:",
        match
    )

    if not match:
        raise ValueError(
            "SQL JOIN and pandas merge results do not match."
        )

    return sql_join_df, pandas_merge_df
def save_validation_outputs(
    result_1,
    result_2,
    sql_join_df,
    pandas_merge_df
):
    """Save pandas and JOIN validation outputs."""

    VALIDATION_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    result_1.to_csv(
        VALIDATION_DIR / "sql_result_1.csv",
        index=False
    )

    result_2.to_csv(
        VALIDATION_DIR / "sql_result_2.csv",
        index=False
    )

    sql_join_df.to_csv(
        VALIDATION_DIR / "sql_join_result.csv",
        index=False
    )

    pandas_merge_df.to_csv(
        VALIDATION_DIR / "pandas_merge_result.csv",
        index=False
    )

    print(
        f"\nValidation outputs saved to: "
        f"{VALIDATION_DIR}"
    )
def main():

    if not DB_FILE.exists():
        raise FileNotFoundError(
            "books.db was not found. Run database.py first."
        )

    connection = sqlite3.connect(DB_FILE)

    try:
        result_1, result_2 = load_sql_results(
            connection
        )

        sql_join_df, pandas_merge_df = (
            compare_sql_join_with_pandas(
                connection
            )
        )

        save_validation_outputs(
            result_1,
            result_2,
            sql_join_df,
            pandas_merge_df
        )

    finally:
        connection.close()

    print("\nPandas validation completed successfully.")


if __name__ == "__main__":
    main()