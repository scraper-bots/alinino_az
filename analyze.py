import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
from collections import Counter

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)

# Read the CSV
print("Loading data...")
df = pd.read_csv('alinino_books.csv')

# Convert numeric columns
df['current_price_numeric'] = pd.to_numeric(df['current_price_numeric'], errors='coerce')
df['old_price_numeric'] = pd.to_numeric(df['old_price_numeric'], errors='coerce')
df['discount_numeric'] = pd.to_numeric(df['discount_numeric'], errors='coerce')
df['pages_numeric'] = pd.to_numeric(df['pages_numeric'], errors='coerce')
df['rating_numeric'] = pd.to_numeric(df['rating_numeric'], errors='coerce')
df['reviews_count'] = pd.to_numeric(df['reviews_count'], errors='coerce')

print(f"Total books loaded: {len(df)}")

# Create statistics dictionary
stats = {
    'total_books': len(df),
    'price_statistics': {},
    'discount_statistics': {},
    'pages_statistics': {},
    'rating_statistics': {},
    'language_distribution': {},
    'publisher_top_10': {},
    'author_top_10': {},
    'labels_distribution': {},
    'cover_type_distribution': {},
    'availability_statistics': {}
}

# Price statistics
stats['price_statistics'] = {
    'average': float(df['current_price_numeric'].mean()),
    'median': float(df['current_price_numeric'].median()),
    'min': float(df['current_price_numeric'].min()),
    'max': float(df['current_price_numeric'].max()),
    'std': float(df['current_price_numeric'].std())
}

# Discount statistics
books_with_discount = df[df['discount_numeric'] > 0]
stats['discount_statistics'] = {
    'books_with_discount': len(books_with_discount),
    'percentage_with_discount': float(len(books_with_discount) / len(df) * 100),
    'average_discount': float(df['discount_numeric'].mean()),
    'max_discount': float(df['discount_numeric'].max())
}

# Pages statistics
stats['pages_statistics'] = {
    'average': float(df['pages_numeric'].mean()),
    'median': float(df['pages_numeric'].median()),
    'min': float(df['pages_numeric'].min()),
    'max': float(df['pages_numeric'].max())
}

# Rating statistics
books_with_rating = df[df['rating_numeric'] > 0]
stats['rating_statistics'] = {
    'books_with_rating': len(books_with_rating),
    'average_rating': float(books_with_rating['rating_numeric'].mean()) if len(books_with_rating) > 0 else 0,
    'median_rating': float(books_with_rating['rating_numeric'].median()) if len(books_with_rating) > 0 else 0
}

# Language distribution
stats['language_distribution'] = df['language'].value_counts().head(10).to_dict()

# Publisher top 10
stats['publisher_top_10'] = df['publisher'].value_counts().head(10).to_dict()

# Author top 10
stats['author_top_10'] = df['author'].value_counts().head(10).to_dict()

# Labels distribution
all_labels = []
for labels in df['labels'].dropna():
    if labels:
        all_labels.extend([label.strip() for label in str(labels).split(',')])
label_counts = Counter(all_labels)
stats['labels_distribution'] = dict(label_counts.most_common(10))

# Cover type distribution
stats['cover_type_distribution'] = df['cover_type'].value_counts().to_dict()

# Availability
stats['availability_statistics'] = df['availability'].value_counts().to_dict()

# Save statistics to JSON
print("\nSaving statistics...")
with open('charts/statistics.json', 'w', encoding='utf-8') as f:
    json.dump(stats, f, indent=2, ensure_ascii=False)

# Create text report
print("Creating text report...")
with open('charts/statistics.txt', 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\n")
    f.write("ALININO.AZ BOOKS ANALYSIS REPORT\n")
    f.write("=" * 80 + "\n\n")

    f.write(f"Total Books: {stats['total_books']}\n\n")

    f.write("PRICE STATISTICS\n")
    f.write("-" * 40 + "\n")
    f.write(f"Average Price: {stats['price_statistics']['average']:.2f} AZN\n")
    f.write(f"Median Price: {stats['price_statistics']['median']:.2f} AZN\n")
    f.write(f"Min Price: {stats['price_statistics']['min']:.2f} AZN\n")
    f.write(f"Max Price: {stats['price_statistics']['max']:.2f} AZN\n")
    f.write(f"Std Dev: {stats['price_statistics']['std']:.2f} AZN\n\n")

    f.write("DISCOUNT STATISTICS\n")
    f.write("-" * 40 + "\n")
    f.write(f"Books with Discount: {stats['discount_statistics']['books_with_discount']}\n")
    f.write(f"Percentage: {stats['discount_statistics']['percentage_with_discount']:.1f}%\n")
    f.write(f"Average Discount: {stats['discount_statistics']['average_discount']:.1f}%\n")
    f.write(f"Max Discount: {stats['discount_statistics']['max_discount']:.0f}%\n\n")

    f.write("PAGES STATISTICS\n")
    f.write("-" * 40 + "\n")
    f.write(f"Average Pages: {stats['pages_statistics']['average']:.0f}\n")
    f.write(f"Median Pages: {stats['pages_statistics']['median']:.0f}\n")
    f.write(f"Min Pages: {stats['pages_statistics']['min']:.0f}\n")
    f.write(f"Max Pages: {stats['pages_statistics']['max']:.0f}\n\n")

    f.write("RATING STATISTICS\n")
    f.write("-" * 40 + "\n")
    f.write(f"Books with Rating: {stats['rating_statistics']['books_with_rating']}\n")
    f.write(f"Average Rating: {stats['rating_statistics']['average_rating']:.2f}/5\n\n")

    f.write("TOP 10 LANGUAGES\n")
    f.write("-" * 40 + "\n")
    for lang, count in stats['language_distribution'].items():
        f.write(f"{lang}: {count}\n")

    f.write("\nTOP 10 PUBLISHERS\n")
    f.write("-" * 40 + "\n")
    for pub, count in stats['publisher_top_10'].items():
        f.write(f"{pub}: {count}\n")

    f.write("\nTOP 10 AUTHORS\n")
    f.write("-" * 40 + "\n")
    for author, count in stats['author_top_10'].items():
        f.write(f"{author}: {count}\n")

    f.write("\nTOP 10 LABELS\n")
    f.write("-" * 40 + "\n")
    for label, count in stats['labels_distribution'].items():
        f.write(f"{label}: {count}\n")

print("\n" + "=" * 80)
print("Creating visualizations...")
print("=" * 80 + "\n")

# Chart 1: Price Distribution
print("1. Price Distribution Histogram...")
plt.figure(figsize=(12, 6))
plt.hist(df['current_price_numeric'].dropna(), bins=50, color='skyblue', edgecolor='black')
plt.xlabel('Price (AZN)', fontsize=12)
plt.ylabel('Number of Books', fontsize=12)
plt.title('Price Distribution of Books', fontsize=14, fontweight='bold')
plt.axvline(df['current_price_numeric'].mean(), color='red', linestyle='--', label=f'Mean: {df["current_price_numeric"].mean():.2f} AZN')
plt.axvline(df['current_price_numeric'].median(), color='green', linestyle='--', label=f'Median: {df["current_price_numeric"].median():.2f} AZN')
plt.legend()
plt.tight_layout()
plt.savefig('charts/01_price_distribution.png', dpi=300)
plt.close()

# Chart 2: Discount Distribution
print("2. Discount Analysis...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

# Pie chart
discount_data = [len(books_with_discount), len(df) - len(books_with_discount)]
ax1.pie(discount_data, labels=['With Discount', 'No Discount'], autopct='%1.1f%%', colors=['#ff9999', '#66b3ff'])
ax1.set_title('Books with Discounts', fontsize=14, fontweight='bold')

# Histogram of discount percentages
ax2.hist(df[df['discount_numeric'] > 0]['discount_numeric'].dropna(), bins=20, color='coral', edgecolor='black')
ax2.set_xlabel('Discount Percentage', fontsize=12)
ax2.set_ylabel('Number of Books', fontsize=12)
ax2.set_title('Distribution of Discount Percentages', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/02_discount_analysis.png', dpi=300)
plt.close()

# Chart 3: Top 10 Languages
print("3. Language Distribution...")
plt.figure(figsize=(12, 6))
lang_data = df['language'].value_counts().head(10)
plt.barh(range(len(lang_data)), lang_data.values, color='lightgreen')
plt.yticks(range(len(lang_data)), lang_data.index)
plt.xlabel('Number of Books', fontsize=12)
plt.ylabel('Language', fontsize=12)
plt.title('Top 10 Languages', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('charts/03_language_distribution.png', dpi=300)
plt.close()

# Chart 4: Top 10 Publishers
print("4. Top Publishers...")
plt.figure(figsize=(12, 6))
pub_data = df['publisher'].value_counts().head(10)
plt.barh(range(len(pub_data)), pub_data.values, color='plum')
plt.yticks(range(len(pub_data)), pub_data.index, fontsize=10)
plt.xlabel('Number of Books', fontsize=12)
plt.ylabel('Publisher', fontsize=12)
plt.title('Top 10 Publishers', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('charts/04_top_publishers.png', dpi=300)
plt.close()

# Chart 5: Top 10 Authors
print("5. Top Authors...")
plt.figure(figsize=(12, 6))
author_data = df['author'].value_counts().head(10)
plt.barh(range(len(author_data)), author_data.values, color='lightsalmon')
plt.yticks(range(len(author_data)), author_data.index, fontsize=10)
plt.xlabel('Number of Books', fontsize=12)
plt.ylabel('Author', fontsize=12)
plt.title('Top 10 Authors', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('charts/05_top_authors.png', dpi=300)
plt.close()

# Chart 6: Pages Distribution
print("6. Pages Distribution...")
plt.figure(figsize=(12, 6))
plt.hist(df['pages_numeric'].dropna(), bins=50, color='lightcoral', edgecolor='black')
plt.xlabel('Number of Pages', fontsize=12)
plt.ylabel('Number of Books', fontsize=12)
plt.title('Distribution of Book Pages', fontsize=14, fontweight='bold')
plt.axvline(df['pages_numeric'].mean(), color='red', linestyle='--', label=f'Mean: {df["pages_numeric"].mean():.0f} pages')
plt.axvline(df['pages_numeric'].median(), color='green', linestyle='--', label=f'Median: {df["pages_numeric"].median():.0f} pages')
plt.legend()
plt.tight_layout()
plt.savefig('charts/06_pages_distribution.png', dpi=300)
plt.close()

# Chart 7: Labels Distribution
print("7. Labels Distribution...")
plt.figure(figsize=(12, 6))
label_counter = Counter(all_labels)
top_labels = dict(label_counter.most_common(10))
plt.barh(range(len(top_labels)), list(top_labels.values()), color='gold')
plt.yticks(range(len(top_labels)), list(top_labels.keys()))
plt.xlabel('Number of Books', fontsize=12)
plt.ylabel('Label', fontsize=12)
plt.title('Top 10 Book Labels', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('charts/07_labels_distribution.png', dpi=300)
plt.close()

# Chart 8: Price vs Pages Scatter
print("8. Price vs Pages Correlation...")
plt.figure(figsize=(12, 6))
clean_data = df[['current_price_numeric', 'pages_numeric']].dropna()
plt.scatter(clean_data['pages_numeric'], clean_data['current_price_numeric'], alpha=0.5, color='steelblue')
plt.xlabel('Number of Pages', fontsize=12)
plt.ylabel('Price (AZN)', fontsize=12)
plt.title('Price vs Number of Pages', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('charts/08_price_vs_pages.png', dpi=300)
plt.close()

# Chart 9: Cover Type Distribution
print("9. Cover Type Distribution...")
if df['cover_type'].notna().sum() > 0:
    plt.figure(figsize=(12, 6))
    cover_data = df['cover_type'].value_counts()
    plt.barh(range(len(cover_data)), cover_data.values, color='teal')
    plt.yticks(range(len(cover_data)), cover_data.index)
    plt.xlabel('Number of Books', fontsize=12)
    plt.ylabel('Cover Type', fontsize=12)
    plt.title('Cover Type Distribution', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('charts/09_cover_type_distribution.png', dpi=300)
    plt.close()

# Chart 10: Rating Distribution
print("10. Rating Distribution...")
if books_with_rating['rating_numeric'].notna().sum() > 0:
    plt.figure(figsize=(12, 6))
    plt.hist(books_with_rating['rating_numeric'].dropna(), bins=20, color='mediumpurple', edgecolor='black')
    plt.xlabel('Rating (out of 5)', fontsize=12)
    plt.ylabel('Number of Books', fontsize=12)
    plt.title('Rating Distribution', fontsize=14, fontweight='bold')
    plt.axvline(books_with_rating['rating_numeric'].mean(), color='red', linestyle='--',
                label=f'Mean: {books_with_rating["rating_numeric"].mean():.2f}')
    plt.legend()
    plt.tight_layout()
    plt.savefig('charts/10_rating_distribution.png', dpi=300)
    plt.close()

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE!")
print("=" * 80)
print(f"\nCharts saved to: charts/")
print(f"Statistics saved to: charts/statistics.json and charts/statistics.txt")
print(f"\nTotal charts created: 10")
