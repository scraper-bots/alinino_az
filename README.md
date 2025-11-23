# Alinino.az Book Scraper

This scraper extracts book data from alinino.az for analysis purposes.

## Features

- Scrapes book listings from collection pages
- Extracts detailed information from each book page
- Saves data to CSV format
- Respectful scraping with delays between requests

## Data Extracted

For each book, the scraper collects:
- URL
- Title
- Current price
- Old price
- Discount percentage
- ISBN
- Publisher
- Author
- Number of pages
- Language
- Cover type (hardcover/softcover)
- Description
- Rating
- Number of reviews
- Availability status
- Labels (Bestseller, Express, etc.)
- Categories/Tags
- Main image URL

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Run the scraper with default settings (scrapes bestsellers, first 5 pages):
```bash
python scraper.py
```

### Custom Usage

Edit `scraper.py` to customize:

```python
# Change collection URL
collection_url = "https://alinino.az/collection/knigi-na-angliyskom-yazyke"

# Remove page limit to scrape all pages
books = scraper.scrape_collection(collection_url)  # No max_pages parameter

# Change output filename
scraper.save_to_csv(books, 'my_books_data.csv')
```

### Example: Scrape Multiple Collections

```python
scraper = AlininoScraper()

collections = [
    "https://alinino.az/collection/bestsellery",
    "https://alinino.az/collection/knigi-na-angliyskom-yazyke",
    "https://alinino.az/collection/klassika"
]

all_books = []
for collection_url in collections:
    books = scraper.scrape_collection(collection_url)
    all_books.extend(books)

scraper.save_to_csv(all_books, 'all_collections.csv')
```

## Output

The scraper generates a CSV file with columns:
- url
- title
- current_price
- old_price
- discount_percent
- isbn
- publisher
- author
- pages
- language
- cover_type
- description
- rating
- reviews_count
- availability
- labels
- categories
- image_url

## Notes

- The scraper includes a 1-second delay between requests to be respectful to the server
- If you encounter errors, check your internet connection and ensure the website structure hasn't changed
- For large collections, the scraping process may take some time

## Example Output

```csv
url,title,current_price,old_price,discount_percent,isbn,...
https://alinino.az/product/ali-and-nino-3,Ali and Nino,11.04 AZN,12.99 AZN,−15%,2000923387071,...
```
