import sqlite3
from pathlib import Path
import pandas as pd
DB_FILE = Path(__file__).parent / "outputs" / "books.db"
CLEANED_FILE = (
    Path(__file__).parent
    / "outputs"
    / "books_cleaned.csv"
)
def get_connection():
    """Create a connection to the SQLite database."""

    connection = sqlite3.connect(DB_FILE)

    # SQLite requires foreign-key enforcement to be enabled
    # for each database connection.
    connection.execute("PRAGMA foreign_keys = ON;")

    return connection
def create_tables(connection):
    """Create the normalized categories and books tables."""

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS categories (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT NOT NULL UNIQUE
        );
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS books (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            price_gbp REAL NOT NULL,
            price_inr REAL NOT NULL,
            rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
            in_stock INTEGER NOT NULL CHECK (in_stock IN (0, 1)),
            category_id INTEGER NOT NULL,

            FOREIGN KEY (category_id)
                REFERENCES categories(category_id)
        );
        """
    )

    connection.commit()

    print("Database tables created successfully.")
def load_cleaned_data():
    """Load the cleaned books dataset."""

    if not CLEANED_FILE.exists():
        raise FileNotFoundError(
            "books_cleaned.csv was not found. "
            "Run clean_data.py first."
        )

    return pd.read_csv(CLEANED_FILE)
def insert_data(connection, df):
    """Insert categories and books into the normalized database."""

    cursor = connection.cursor()

    # Clear existing records so rerunning this script
    # does not create duplicate books.
    cursor.execute("DELETE FROM books;")
    cursor.execute("DELETE FROM categories;")

    # Insert each unique category
    categories = sorted(df["category"].dropna().unique())

    for category in categories:
        cursor.execute(
            """
            INSERT INTO categories (category_name)
            VALUES (?);
            """,
            (category,)
        )

    # Create a mapping:
    # category name -> category ID
    cursor.execute(
        """
        SELECT category_id, category_name
        FROM categories;
        """
    )

    category_map = {
        category_name: category_id
        for category_id, category_name in cursor.fetchall()
    }

    # Insert all books using category_id as the foreign key
    for _, row in df.iterrows():
        cursor.execute(
            """
            INSERT INTO books (
                title,
                price_gbp,
                price_inr,
                rating,
                in_stock,
                category_id
            )
            VALUES (?, ?, ?, ?, ?, ?);
            """,
            (
                row["title"],
                float(row["price_gbp"]),
                float(row["price_inr"]),
                int(row["rating"]),
                int(row["in_stock"]),
                category_map[row["category"]],
            )
        )

    connection.commit()

    print("Cleaned data inserted successfully.")
def verify_database(connection):
    """Verify database row counts and relationships."""

    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM categories;")
    category_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM books;")
    book_count = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM books AS b
        JOIN categories AS c
            ON b.category_id = c.category_id;
        """
    )
    joined_book_count = cursor.fetchone()[0]

    cursor.execute("PRAGMA foreign_key_check;")
    foreign_key_errors = cursor.fetchall()

    print(f"Categories stored: {category_count}")
    print(f"Books stored: {book_count}")
    print(f"Books matched through JOIN: {joined_book_count}")
    print(f"Foreign key violations: {len(foreign_key_errors)}")

    if book_count < 60:
        raise ValueError(
            "Database contains fewer than 60 books."
        )

    if joined_book_count != book_count:
        raise ValueError(
            "Some books do not have a valid category relationship."
        )

    if foreign_key_errors:
        raise ValueError(
            "Foreign key violations were detected."
        )

    print("Database verification passed.")
def main():
    connection = get_connection()

    try:
        create_tables(connection)

        df = load_cleaned_data()

        insert_data(connection, df)

        verify_database(connection)

    finally:
        connection.close()


if __name__ == "__main__":
    main()