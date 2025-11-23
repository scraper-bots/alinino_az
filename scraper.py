import aiohttp
import asyncio
from bs4 import BeautifulSoup
import csv
from urllib.parse import urljoin
import re

class AlininoScraper:
    def __init__(self, max_concurrent=5, batch_size=50):
        self.base_url = "https://alinino.az"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.semaphore = asyncio.Semaphore(max_concurrent)  # Limit concurrent requests
        self.batch_size = batch_size
        self.timeout = aiohttp.ClientTimeout(total=30)  # 30 second timeout

    async def get_book_links_from_page(self, session, url):
        """Extract all book links from a collection page"""
        print(f"Fetching book links from: {url}")
        async with self.semaphore:
            async with session.get(url, headers=self.headers) as response:
                content = await response.text()
                soup = BeautifulSoup(content, 'html.parser')

                book_links = []
                # Find all product cards
                product_cards = soup.find_all('form', {'data-product-id': True})

                for card in product_cards:
                    # Find the link to the product page
                    link = card.find('a', class_='product-card__title')
                    if link and link.get('href'):
                        full_url = urljoin(self.base_url, link['href'])
                        book_links.append(full_url)

                print(f"Found {len(book_links)} books on this page")
                return book_links

    async def extract_book_data(self, session, url):
        """Extract detailed data from a book page"""
        try:
            async with self.semaphore:
                async with session.get(url, headers=self.headers) as response:
                    content = await response.text()

            soup = BeautifulSoup(content, 'html.parser')
            data = {
                'url': url,
                'title': '',
                'current_price': '',
                'current_price_numeric': '',
                'old_price': '',
                'old_price_numeric': '',
                'discount_percent': '',
                'discount_numeric': '',
                'isbn': '',
                'publisher': '',
                'author': '',
                'pages': '',
                'pages_numeric': '',
                'language': '',
                'cover_type': '',
                'description': '',
                'rating': '',
                'rating_numeric': '',
                'reviews_count': '',
                'availability': '',
                'labels': '',
                'categories': '',
                'image_url': ''
            }

            # Title
            title = soup.find('h1', class_='product__title')
            if title:
                data['title'] = title.text.strip()

            # Prices
            current_price = soup.find('div', class_='product__price')
            if current_price:
                price_text = current_price.text.strip()
                data['current_price'] = price_text
                # Extract numeric value
                price_num = re.search(r'([\d.,]+)', price_text.replace(' ', ''))
                if price_num:
                    data['current_price_numeric'] = price_num.group(1).replace(',', '.')

            old_price = soup.find('div', class_='product__old-price')
            if old_price:
                price_text = old_price.text.strip()
                data['old_price'] = price_text
                # Extract numeric value
                price_num = re.search(r'([\d.,]+)', price_text.replace(' ', ''))
                if price_num:
                    data['old_price_numeric'] = price_num.group(1).replace(',', '.')

            # Discount
            discount = soup.find('span', class_='labels__item_type_sale')
            if discount:
                discount_text = discount.text.strip()
                data['discount_percent'] = discount_text
                # Extract numeric value
                discount_num = re.search(r'(\d+)', discount_text)
                if discount_num:
                    data['discount_numeric'] = discount_num.group(1)

            # Properties (ISBN, Publisher, Author, etc.)
            properties = soup.find_all('div', class_='properties__item')
            for prop in properties:
                name = prop.find('div', class_='properties__item-name')
                value = prop.find('div', class_='properties__item-value')

                if name and value:
                    name_text = name.text.strip().replace(':', '').lower()
                    value_text = value.text.strip()

                    if 'isbn' in name_text or 'artikul' in name_text:
                        data['isbn'] = value_text
                    elif 'nəşriyyat' in name_text or 'publisher' in name_text:
                        data['publisher'] = value_text
                    elif 'müəllif' in name_text or 'author' in name_text:
                        data['author'] = value_text
                    elif 'səhifə' in name_text or 'pages' in name_text:
                        data['pages'] = value_text
                        # Extract numeric value
                        pages_num = re.search(r'(\d+)', value_text)
                        if pages_num:
                            data['pages_numeric'] = pages_num.group(1)
                    elif 'dil' in name_text or 'language' in name_text:
                        data['language'] = value_text
                    elif 'cild' in name_text or 'cover' in name_text:
                        data['cover_type'] = value_text

            # Description
            description_div = soup.find('div', class_='text')
            if description_div:
                # Get text from all paragraphs
                paragraphs = description_div.find_all('p')
                description_text = ' '.join([p.text.strip() for p in paragraphs])
                data['description'] = description_text

            # Rating
            rating_span = soup.find('span', class_='rating__stars')
            if rating_span and rating_span.get('data-rating'):
                rating_value = rating_span['data-rating']
                data['rating'] = rating_value
                data['rating_numeric'] = rating_value  # Already numeric

            # Reviews count
            reviews_count = soup.find('span', class_='rating__count')
            if reviews_count:
                count_text = reviews_count.text.strip()
                # Extract just the number
                number = re.search(r'\d+', count_text)
                if number:
                    data['reviews_count'] = number.group()
                else:
                    data['reviews_count'] = '0'
            else:
                data['reviews_count'] = '0'

            # Availability
            availability = soup.find('span', {'data-product-card-available': True})
            if availability:
                data['availability'] = availability.text.strip()

            # Labels (Bestseller, Express, etc.) - only from product form
            product_form = soup.find('form', {'data-main-form': True}) or soup.find('div', class_='product__form')
            label_texts = []
            if product_form:
                labels_div = product_form.find('div', class_='labels')
                if labels_div:
                    labels = labels_div.find_all('span', class_='labels__item')
                    seen_labels = set()  # Avoid duplicates
                    for label in labels:
                        # Skip discount labels and get data-label-title or text
                        if 'labels__item_type_sale' not in label.get('class', []):
                            label_title = label.get('data-label-title') or label.text.strip()
                            if label_title and label_title.strip() and label_title not in seen_labels:
                                label_texts.append(label_title.strip())
                                seen_labels.add(label_title)
            data['labels'] = ', '.join(label_texts) if label_texts else ''

            # Categories/Tags
            tags = soup.find('div', class_='product__tags')
            if tags:
                tag_links = tags.find_all('a', class_='product-tags__item')
                data['categories'] = ', '.join([tag.text.strip() for tag in tag_links])

            # Main image - try multiple sources
            # First try the main product gallery
            product_gallery = soup.find('div', class_='product-gallery__main')
            if product_gallery:
                img = product_gallery.find('img')
                if img:
                    # Try src, then data-src
                    img_url = img.get('src') or img.get('data-src')
                    if img_url and 'products' in img_url:  # Make sure it's a product image, not a placeholder
                        data['image_url'] = img_url

            # If no valid image found, try the first picture element with product image
            if not data['image_url']:
                pictures = soup.find_all('picture')
                for picture in pictures:
                    source = picture.find('source')
                    if source:
                        srcset = source.get('srcset') or source.get('data-srcset', '')
                        if 'products' in srcset:
                            # Extract first URL from srcset
                            url_match = re.search(r'(https://[^\s]+)', srcset)
                            if url_match:
                                data['image_url'] = url_match.group(1).split()[0]
                                break

            return data

        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            return None

    async def scrape_collection(self, collection_url, max_pages=None):
        """Scrape all books from a collection"""
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            # First, collect all book links from all pages
            all_book_links = []
            page = 1

            while True:
                if max_pages and page > max_pages:
                    break

                # Construct page URL
                if page == 1:
                    page_url = collection_url
                else:
                    page_url = f"{collection_url}?page={page}"

                # Get book links from this page
                book_links = await self.get_book_links_from_page(session, page_url)

                if not book_links:
                    print(f"No books found on page {page}, stopping")
                    break

                all_book_links.extend(book_links)
                page += 1

            print(f"\nTotal books to scrape: {len(all_book_links)}")
            print(f"Processing in batches of {self.batch_size}...\n")

            # Scrape books in batches
            all_books = []
            for i in range(0, len(all_book_links), self.batch_size):
                batch = all_book_links[i:i + self.batch_size]
                batch_num = i // self.batch_size + 1
                total_batches = (len(all_book_links) + self.batch_size - 1) // self.batch_size

                print(f"Processing batch {batch_num}/{total_batches} ({len(batch)} books)...")

                tasks = [self.extract_book_data(session, link) for link in batch]
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)

                # Filter out None values and exceptions
                for result in batch_results:
                    if result is not None and not isinstance(result, Exception):
                        all_books.append(result)
                    elif isinstance(result, Exception):
                        print(f"Error in batch: {str(result)}")

                print(f"Batch {batch_num} complete. Total scraped: {len(all_books)}")

                # Small delay between batches to be respectful
                if i + self.batch_size < len(all_book_links):
                    await asyncio.sleep(1)

            return all_books

    def save_to_csv(self, books, filename='books_data.csv'):
        """Save scraped data to CSV"""
        if not books:
            print("No data to save")
            return

        fieldnames = books[0].keys()

        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(books)

        print(f"Saved {len(books)} books to {filename}")

async def main():
    scraper = AlininoScraper()

    # Scrape bestsellers collection - all pages
    collection_url = "https://alinino.az/collection/bestsellery"

    # Scrape all pages
    books = await scraper.scrape_collection(collection_url)

    # Save to CSV
    scraper.save_to_csv(books, 'alinino_books.csv')

if __name__ == "__main__":
    asyncio.run(main())
