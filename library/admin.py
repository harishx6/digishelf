from django.contrib import admin
from .models import Book, Member, IssuedBook, Review
from datetime import date
from .models import LostAndFound
from .models import DigitalResource

# 1. Book Dashboard (Safe Mode: No Image Logic)
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'stock_count') 
    search_fields = ('title', 'author', 'category')
    list_filter = ('category',)

# 2. Member Dashboard
@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'email')
    search_fields = ('name', 'email')

# 3. Transaction Dashboard
@admin.register(IssuedBook)
class IssuedBookAdmin(admin.ModelAdmin):
    list_display = ('member_name', 'book_title', 'issue_date', 'due_date', 'return_status', 'days_overdue')
    list_filter = ('issue_date', 'returned_date')
    search_fields = ('member__name', 'book__title')
    
    def member_name(self, obj):
        return obj.member.name
        
    def book_title(self, obj):
        return obj.book.title

    # Status Logic
    def return_status(self, obj):
        if obj.returned_date:
            return "✅ Returned"
        elif obj.due_date and obj.due_date < date.today():
            return "🔥 Overdue!"
        else:
            return "🔵 Active"
    
    # Fine Calculation
    def days_overdue(self, obj):
        if not obj.returned_date and obj.due_date and obj.due_date < date.today():
            days = (date.today() - obj.due_date).days
            return f"{days} Days (Fine: ₹{days * 10})"
        return "-"

# 4. Review Dashboard
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('book_title', 'member_name', 'rating', 'short_comment', 'created_at')
    list_filter = ('rating',)
    
    def book_title(self, obj):
        return obj.book.title
        
    def member_name(self, obj):
        return obj.member.name
    
    def short_comment(self, obj):
        return obj.comment[:50] + "..." if obj.comment and len(obj.comment) > 50 else obj.comment
    
# ... (Mela irukura code apdiye irukkatum) ...

# 👇 ADD THESE 3 LINES AT THE END 👇
admin.site.site_header = "DigiShelf Admin Dashboard"
admin.site.site_title = "DigiShelf Library Portal"
admin.site.index_title = "Welcome to Library Management System"

@admin.register(LostAndFound)
class LostAndFoundAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'status', 'reported_by', 'date_reported')
    list_filter = ('status', 'date_reported')
    search_fields = ('item_name', 'description', 'storage_location')

@admin.register(DigitalResource)
class DigitalResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'uploaded_at')
    list_filter = ('category', 'uploaded_at')
    search_fields = ('title', 'description')