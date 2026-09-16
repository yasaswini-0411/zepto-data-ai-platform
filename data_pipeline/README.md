# Data Pipeline

This module implements a complete data pipeline using book data collected from Books to Scrape. It covers web scraping, data cleaning and transformation, normalized SQLite storage, SQL analysis, and pandas-based validation.

## 1. Web Scraping

Book data is collected from Books to Scrape using Python `requests` and `BeautifulSoup`.

The scraper processes the first five paginated All Products pages:

- `page-1.html`
- `page-2.html`
- `page-3.html`
- `page-4.html`
- `page-5.html`

A total of 100 books are collected.

For every book, the following raw attributes are captured:

- `title`
- `price`
- `star_rating`
- `availability`
- `category`

The category is retrieved from each book's detail page using its breadcrumb information.

The website responses are explicitly decoded using UTF-8 to prevent incorrect price symbols during scraping.

The raw dataset is stored in:

`outputs/books_raw.csv`

## 2. Data Cleaning and Transformation

The raw dataset is cleaned using pandas.

### Price

The pound symbol is removed from the raw `price` field and the value is converted to a numeric floating-point column named `price_gbp`.

Numeric conversion uses `errors="coerce"` so malformed or non-numeric prices become missing values (`NaN`).

Rows containing malformed or missing prices are dropped. Price represents a factual product attribute, so imputing a fabricated price could misrepresent the original book data.

In the collected dataset, no malformed or missing prices were detected.

### Star Rating

Text ratings are converted to integers using the following mapping:

- One → 1
- Two → 2
- Three → 3
- Four → 4
- Five → 5

The resulting column is named `rating`.

Invalid or missing rating values are treated as invalid records and dropped. No invalid or missing ratings were detected in the collected dataset.

### Availability

The textual availability field is converted into the boolean column `in_stock`.

`In stock` becomes `True`; otherwise the value becomes `False`.

### Currency Conversion

INR prices use the required fixed conversion baseline:

`1 GBP = 105.50 INR`

Therefore:

`price_inr = price_gbp × 105.50`

The submitted INR values do not depend on a live exchange-rate API.

The final cleaned dataset contains:

- `title`
- `price_gbp`
- `price_inr`
- `rating`
- `in_stock`
- `category`

After cleaning, 100 records remain with no missing values in the cleaned dataset.

The cleaned dataset is stored in:

`outputs/books_cleaned.csv`

## 3. SQLite Database

The cleaned dataset is stored in a normalized SQLite database:

`outputs/books.db`

The database contains two related tables.

### categories

| Column | Description |
| --- | --- |
| `category_id` | Primary key |
| `category_name` | Unique category name |

### books

| Column | Description |
| --- | --- |
| `book_id` | Primary key |
| `title` | Book title |
| `price_gbp` | Price in GBP |
| `price_inr` | Price converted to INR |
| `rating` | Integer rating from 1 to 5 |
| `in_stock` | Stock status stored as 0 or 1 |
| `category_id` | Foreign key referencing `categories.category_id` |

This creates a one-to-many relationship in which one category can contain many books.

Database verification produced:

- 29 categories
- 100 books
- 100 books matched through the table JOIN
- 0 foreign-key violations

## 4. SQL Queries

Five SQL queries are included in:

`queries.sql`

The queries collectively demonstrate all required SQL concepts:

- `SELECT`
- `WHERE`
- `ORDER BY`
- `LIMIT`
- `DISTINCT`
- `BETWEEN`
- `IN`
- `JOIN`

The queries analyze:

1. Top 10 most expensive books
2. Highly rated books within a selected GBP price range
3. Distinct ratings in the dataset
4. Books belonging to selected categories
5. Books joined with their category names

The actual query outputs are saved in:

`outputs/sql_results/`

The five result files are:

- `query_1_top_10_expensive.csv`
- `query_2_high_rated_price_range.csv`
- `query_3_distinct_ratings.csv`
- `query_4_selected_categories.csv`
- `query_5_books_with_categories.csv`

## 5. pandas SQL and JOIN Validation

SQL query results are also loaded into pandas using `pd.read_sql()`.

At least two SQL results are explicitly loaded as pandas DataFrames.

To validate the normalized database relationship, the SQL JOIN between the `books` and `categories` tables is independently reproduced using `pd.merge()`.

The validation produced:

- SQL JOIN rows: 100
- pandas merge rows: 100
- SQL JOIN and pandas merge match: `True`

This confirms that the pandas merge reproduces the SQL JOIN result.

Validation outputs are stored in:

`outputs/pandas_validation/`

## 6. Running the Module

Run the commands from the repository root with the project virtual environment activated.

### Scrape the book data

```bash
python data_pipeline/scraper.py