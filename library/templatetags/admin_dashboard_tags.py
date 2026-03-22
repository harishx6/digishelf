from django import template
from django.contrib.auth.models import User
from django.db.models import Count
from django.db.models.functions import TruncDay
from django.utils import timezone
from datetime import timedelta
from library.models import Book, IssuedBook, Member 

register = template.Library()

@register.inclusion_tag('admin/dashboard_stats.html')
def show_dashboard_stats():
    # 1. Basic Stats
    total_books = Book.objects.count()
    total_members = Member.objects.count()
    issued_count = IssuedBook.objects.filter(status='issued').count()
    returned_count = IssuedBook.objects.filter(status='returned').count()

    # 2. Graph Logic (Pre-fetch for 90 Days)
    today = timezone.now().date()
    start_date = today - timedelta(days=89) 
    
    # --- ISSUED DATA ---
    daily_issues = IssuedBook.objects.filter(
        issue_date__gte=start_date
    ).annotate(day=TruncDay('issue_date')).values('day').annotate(count=Count('id'))

    # Safe Check: Date object ah irundha apdiye edu, datetime ah irundha .date() podu
    issues_dict = {}
    for entry in daily_issues:
        d = entry['day']
        if hasattr(d, 'date'): d = d.date()
        issues_dict[d] = entry['count']

    # --- RETURNED DATA (New Addition) ---
    daily_returns = IssuedBook.objects.filter(
        status='returned',
        returned_date__gte=start_date
    ).annotate(day=TruncDay('returned_date')).values('day').annotate(count=Count('id'))

    # Safe Check for Returns too
    returns_dict = {}
    for entry in daily_returns:
        d = entry['day']
        if hasattr(d, 'date'): d = d.date()
        returns_dict[d] = entry['count']

    labels_90 = []
    data_issued_90 = []
    data_returned_90 = [] # New List
    
    for i in range(90):
        date_point = start_date + timedelta(days=i)
        labels_90.append(date_point.strftime('%d %b'))
        
        # Append both Issued and Returned counts
        data_issued_90.append(issues_dict.get(date_point, 0))
        data_returned_90.append(returns_dict.get(date_point, 0))

    return {
        'total_books': total_books,
        'total_members': total_members,
        'issued_count': issued_count,
        'returned_count': returned_count,
        'graph_labels': labels_90,
        'graph_data_issued': data_issued_90,     # Renamed
        'graph_data_returned': data_returned_90, # New Data
    }