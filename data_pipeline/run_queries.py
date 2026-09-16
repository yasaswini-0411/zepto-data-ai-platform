import sqlite3
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).parent

DB_FILE = BASE_DIR / "outputs" / "books.db"

RESULTS_DIR = BASE_DIR / "outputs" / "sql_results"
QUERIES = {
    "query_1_top_10_expensive": """
        SELECT
            title,
            price_gbp,
            price_inr,
            rating
        FROM books
        ORDER BY price_gbp DESC
        LIMIT 10;
    """,

    "query_2_high_rated_price_range": """
        SELECT
            title,
            price_gbp,
            rating
        FROM books
        WHERE rating >= 4
          AND price_gbp BETWEEN 20 AND 40
        ORDER BY rating DESC, price_gbp DESC;
    """,

    "query_3_distinct_ratings": """
        SELECT DISTINCT
            rating
        FROM books
        ORDER BY rating;
    """,

    "query_4_selected_categories": """
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
    """,

    "query_5_books_with_categories": """
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
        ORDER BY c.category_name, b.title;
    """
}
def run_queries():
    """Execute all required SQL queries and save their outputs."""

    if not DB_FILE.exists():
        raise FileNotFoundError(
            "books.db was not found. Run database.py first."
        )

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_FILE)

    try:
        for query_name, sql_query in QUERIES.items():

            result = pd.read_sql_query(
                sql_query,
                connection
            )

            output_file = RESULTS_DIR / f"{query_name}.csv"

            result.to_csv(
                output_file,
                index=False
            )

            print(f"\n{query_name}")
            print("-" * 60)
            print(result)
            print(f"Rows returned: {len(result)}")
            print(f"Saved to: {output_file}")

    finally:
        connection.close()
def main():
    run_queries()

    print("\nAll SQL queries executed successfully.")


if __name__ == "__main__":
    main()