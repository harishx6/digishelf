import re
from library.models import Book

print("Uploading books... Please wait ⏳")

# Read the text file
file_path = 'books_data.txt'
books_to_add = []

with open(file_path, 'r', encoding='utf-8') as file:
    for line in file:
        line = line.strip()
        # Skip empty lines, headers, or lines without the price symbol '₹'
        if not line or '₹' not in line:
            continue
        
        # Split the line by commas
        parts = [p.strip() for p in line.split(',')]
        
        if len(parts) >= 6:
            # 1. Title (Remove the number like "1. ")
            raw_title = parts[0]
            title = re.sub(r'^\d+\.\s*', '', raw_title)
            
            # 2. Author
            author = parts[1]
            
            # 3. Category
            category = parts[2]
            
            # 4. Publisher
            publisher = parts[3]
            
            # 5. Price (Remove '₹' and convert to float)
            raw_price = parts[4].replace('₹', '').replace(',', '').strip()
            try:
                price = float(raw_price)
            except ValueError:
                price = 0.00
            
            # 6. Year
            try:
                year = int(parts[5].strip())
            except ValueError:
                year = None
            
            # Create Book object (stock_count 10 னு வெச்சிருக்கேன், அப்போதான் available னு காட்டும்)
            book = Book(
                title=title,
                author=author,
                category=category,
                stock_count=10, 
                publisher=publisher,
                price=price,
                year_of_publication=year
            )
            books_to_add.append(book)

# Bulk create saves all books in just 1 query!
Book.objects.bulk_create(books_to_add)

print(f"✅ Success! {len(books_to_add)} Books magically uploaded to your database! 🚀")