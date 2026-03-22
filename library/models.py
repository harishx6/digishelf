from django.db import models
from datetime import date, timedelta
from django.utils import timezone
from django.contrib.auth.models import User # User model import
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings

# 1. GENRE LIST (Top of the file)
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

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    category = models.CharField(max_length=100, choices=GENRE_CHOICES) # Category-kum drop down use pannalam
    stock_count = models.IntegerField(default=0)
    
    publisher = models.CharField(max_length=255, null=True, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    year_of_publication = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.title

class Member(models.Model):
    # Link to Django's built-in User model
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True) 
    
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True) # Unnoda field name 'phone_number'
    address = models.TextField(null=True, blank=True)
    
    # 👇 MACHA, IDHU DHAAN PUDHU FIELD (Favorite Genre) 👇
    favorite_genre = models.CharField(max_length=50, choices=GENRE_CHOICES, default='fiction')

    def __str__(self):
        return self.name

class IssuedBook(models.Model):
    STATUS_CHOICES = [
        ('issued', 'Issued'),
        ('returned', 'Returned'),
        ('reserved', 'Reserved'),
    ]

    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    issue_date = models.DateTimeField(default=timezone.now) 
    due_date = models.DateField(null=True, blank=True)
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    returned_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='issued')
    last_alert_sent_date = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.due_date and self.status == 'issued':
            self.due_date = date.today() + timedelta(days=14)
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        if self.due_date and date.today() > self.due_date and self.status == 'issued':
            return True
        return False

    def __str__(self):
        return f"{self.book.title} - {self.member.name}"

    @property
    def waitlist_position(self):
        if not self.status or self.status.strip().lower() != 'reserved':
            return None
        queue = IssuedBook.objects.filter(book=self.book, status__iexact='reserved').order_by('id') 
        for index, entry in enumerate(queue):
            if entry.id == self.id:
                return index + 1
        return 1

class Reservation(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    reserved_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.member.name} reserved {self.book.title}"

class Review(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    rating = models.IntegerField(default=5)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.rating} Stars for {self.book.title}"
    
@receiver(post_save, sender=Book)
def announce_new_book(sender, instance, created, **kwargs):
    # 'created=True' naala pudhu book add panna mattum work aagum. Edit panna work aagathu.
    if created:
        print(f"🚀 New Book Added: {instance.title} ({instance.category})")
        
        # 1. Yaarukellam indha category pudikum nu thedurom
        # 'favorite_genre' field Member model-la irukanum (Check models.py)
        interested_members = Member.objects.filter(favorite_genre=instance.category)
        
        # 2. Avanga Email list edukkurom
        recipient_list = [member.email for member in interested_members]
        
        # 3. Email irundha mattum anupurom
        if recipient_list:
            subject = f"📚 New Arrival: {instance.title} is here!"
            message = (
                f"Hi Book Lover!\n\n"
                f"Great news! A new book '{instance.title}' by {instance.author} "
                f"has just been added to our {instance.category} collection.\n\n"
                f"Login to DigiShelf now to reserve your copy before it runs out!\n\n"
                f"Happy Reading,\nDigiShelf Team"
            )
            
            try:
                # fail_silently=True potta, mail pogalanaalum server crash aagadhu
                send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list, fail_silently=True)
                print(f"✅ Sent New Arrival Alert to {len(recipient_list)} members.")
            except Exception as e:
                print(f"❌ Mail Error: {e}")
        else:
            print("⚠️ No members found for this category.")

# library/models.py (Kadaisiyila add pannu)

    
# library/models.py

from django.db import models
from django.contrib.auth.models import User # User model கண்டிப்பா import ஆகியிருக்கணும்

# (உன்னோட பழைய மாடல்ஸ் Book, Member, IssuedBook எல்லாம் மேல இருக்கும்)

# library/models.py
from django.core.mail import send_mail
from django.conf import settings

# library/models.py

class LostAndFound(models.Model):
    STATUS_CHOICES = (
        ('lost', 'Lost'),
        ('found', 'Found'), # யூசர் கண்டுபிடிச்சா இது காட்டும்
        ('recovered', 'recovered'), # 👇 தொலைஞ்சது கிடைச்சா இது காட்டும் 👇
        ('claimed', 'Claimed')
    )
    item_name = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='lost')
    storage_location = models.CharField(max_length=150, blank=True, null=True, help_text="Admin Use: Where is this item kept?")
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE)
    date_reported = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # 👇 MACHA, INGA 'found' KU BADHILA 'recovered' NU MAATHIYACHU 👇
        if self.pk: 
            old_item = LostAndFound.objects.get(pk=self.pk)
            if old_item.status == 'lost' and self.status == 'recovered':
                subject = f"Good News! Your lost item '{self.item_name}' has been found."
                message = f"Hello {self.reported_by.username},\n\nWe have found your reported lost item: {self.item_name}.\nIt is currently securely stored at: {self.storage_location or 'the Admin Desk'}.\n\nPlease collect it from the library as soon as possible.\n\nRegards,\nDigiShelf"
                send_mail(subject, message, settings.EMAIL_HOST_USER, [self.reported_by.email], fail_silently=True)
                
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item_name} - {self.get_status_display()}"
    

# library/models.py

class DigitalResource(models.Model):
    CATEGORY_CHOICES = (
        ('exam_material', 'Govt Exam Materials'),
        ('question_paper', 'Old Question Papers'),
        ('e_magazine', 'E-Magazines'),
        ('e_book', 'E-Books (Online Read/Download)'),
    )
    
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True, null=True, help_text="Short detail about the PDF")
    
    # PDF ஃபைல் அப்லோட் பண்றதுக்கான Field
    file = models.FileField(upload_to='digital_resources/pdfs/')
    
    # UI-ல பாக்க அழகா இருக்க ஒரு கவர் இமேஜ் (Optional)
    cover_image = models.ImageField(upload_to='digital_resources/covers/', blank=True, null=True)
    
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"