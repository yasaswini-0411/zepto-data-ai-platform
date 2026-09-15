import pandas as pd
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://books.toscrape.com/"
CATALOGUE_URL = urljoin(BASE_URL, "catalogue/")


def get_soup(url):
    """
    Downloads a web page and converts its HTML into a BeautifulSoup object.
    """
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    response.encoding = "utf-8"

    return BeautifulSoup(response.text, "html.parser")

def get_category(book_url):
    """
    Opens an individual book page and extracts the category
    from the breadcrumb navigation.
    """
    soup = get_soup(book_url)

    breadcrumb = soup.select("ul.breadcrumb li a")

    if len(breadcrumb) >= 3:
        return breadcrumb[2].get_text(strip=True)

    return "Unknown"


def scrape_page(page_number):
    """
    Scrapes all books from one All Products page.
    """
    page_url = urljoin(CATALOGUE_URL, f"page-{page_number}.html")

    print(f"Scraping page {page_number}: {page_url}")

    soup = get_soup(page_url)

    books = []

    book_cards = soup.select("article.product_pod")

    for book in book_cards:

        title_element = book.select_one("h3 a")
        title = title_element["title"]

        price = book.select_one("p.price_color").get_text(strip=True)

        star_rating = book.select_one("p.star-rating")["class"][1]

        availability = book.select_one(
            "p.instock.availability"
        ).get_text(strip=True)

        relative_link = title_element["href"]

        book_url = urljoin(page_url, relative_link)

        category = get_category(book_url)

        books.append(
            {
                "title": title,
                "price": price,
                "star_rating": star_rating,
                "availability": availability,
                "category": category,
            }
        )

    return books


def main():
    all_books = []

    for page_number in range(1, 6):
        books = scrape_page(page_number)
        all_books.extend(books)

    print("\nScraping completed.")
    print(f"Total books collected: {len(all_books)}")

    # Convert the collected records into a DataFrame
    df = pd.DataFrame(all_books)

    # Validate the minimum dataset requirement
    if len(df) < 60:
        raise ValueError(
            f"Only {len(df)} books were collected. "
            "The project requires at least 60 books."
        )

    # Define the output folder relative to this script
    output_dir = Path(__file__).parent / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save the untouched scraped data
    output_file = output_dir / "books_raw.csv"
    df.to_csv(output_file, index=False)

    print(f"Raw dataset saved to: {output_file}")

    print("\nDataset shape:")
    print(df.shape)

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nFirst 5 records:")
    print(df.head())

    print("\nBooks per category:")
    print(df["category"].value_counts())


if __name__ == "__main__":
    main()