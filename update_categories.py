from library.models import Book

# நீ அனுப்புன உன்னோட Choices லிஸ்ட்
GENRE_CHOICES = [
    ('computer-science', 'Computer Science'), ('it', 'Information Technology'),
    ('gk', 'General Knowledge'), ('encyclopedias', 'Encyclopedias'),
    ('philosophy', 'Philosophy'), ('psychology', 'Psychology'),
    ('religion', 'Religion'), ('spirituality', 'Spirituality'),
    ('social-sciences', 'Social Sciences'), ('sociology', 'Sociology'),
    ('economics', 'Economics'), ('political-science', 'Political Science'),
    ('law', 'Law'), ('education', 'Education'),
    ('language', 'Language'), ('linguistics', 'Linguistics'),
    ('grammar', 'Grammar'), ('literature', 'Literature'),
    ('fiction', 'Fiction'), ('non-fiction', 'Non-Fiction'),
    ('sci-fi', 'Science Fiction'), ('fantasy', 'Fantasy'),
    ('mystery-thriller', 'Mystery & Thriller'), ('romance', 'Romance'),
    ('biography', 'Biography'), ('autobiography', 'Autobiography'),
    ('history', 'History'), ('geography', 'Geography'),
    ('pure-science', 'Pure Science'), ('physics', 'Physics'),
    ('chemistry', 'Chemistry'), ('mathematics', 'Mathematics'),
    ('biology', 'Biology'), ('environmental-science', 'Environmental Science'),
    ('applied-science', 'Applied Science'), ('engineering', 'Engineering'),
    ('medicine', 'Medicine'), ('agriculture', 'Agriculture'),
    ('technology', 'Technology'), ('ai', 'Artificial Intelligence'),
    ('data-science', 'Data Science'), ('business', 'Business'),
    ('management', 'Management'), ('finance', 'Finance'),
    ('accounting', 'Accounting'), ('marketing', 'Marketing'),
    ('self-help', 'Self-Help'), ('motivation', 'Motivation'),
    ('health-fitness', 'Health & Fitness'), ('arts', 'Arts'),
    ('music', 'Music'), ('photography', 'Photography'),
    ('sports', 'Sports'), ('travel', 'Travel'),
    ('childrens-books', 'Children’s Books'), ('young-adult', 'Young Adult'),
    ('competitive-exams', 'Competitive Exam Books'), ('journals', 'Journals'),
    ('magazines', 'Magazines'), ('reference-books', 'Reference Books'),
    ('research-papers', 'Research Papers'), ('digital-resources', 'Digital Resources'),
    ('comics', 'Comics & Graphic Novels'), ('drama', 'Drama'), ('poetry', 'Poetry'),
]

print("Fixing Categories... ⏳")

# "Computer Science" -> "computer-science" னு மேட்ச் பண்ண ஒரு Dictionary
category_map = {display_name: db_key for db_key, display_name in GENRE_CHOICES}

books = Book.objects.all()
updated_books = []

for book in books:
    # டேட்டாபேஸ்ல இருக்கிற தப்பான கேட்டகிரியை எடுக்குறோம்
    current_cat = str(book.category).strip() 
    
    # அது நம்ம லிஸ்ட்ல இருந்தா, கரெக்ட்டான Short-key-க்கு மாத்துறோம்
    if current_cat in category_map:
        book.category = category_map[current_cat]
        updated_books.append(book)

# எல்லா புக்ஸையும் ஒரே அடியா அப்டேட் பண்றோம் (Bulk Update)
if updated_books:
    Book.objects.bulk_update(updated_books, ['category'])
    print(f"✅ Success! {len(updated_books)} Books categories have been perfectly updated! 🚀")
else:
    print("⚠️ No books needed updating. Something went wrong.")