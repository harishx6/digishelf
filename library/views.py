from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.db.models import Q, Avg, Count, F
from django.db.models.functions import TruncDay
from django.contrib import messages
from django.utils import timezone
from datetime import date, timedelta
import random
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import LostAndFound
from .forms import LostAndFoundForm
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from datetime import date
from .models import IssuedBook
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.models import User
import uuid
from django.utils import timezone
from datetime import date
import uuid
from datetime import date
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Member, IssuedBook, Book
from .models import LostAndFound
from .forms import LostAndFoundForm
# library/views.py (Top of the file)
from django.core.mail import send_mail
from django.conf import settings
from .forms import SignUpForm, ReviewForm, MemberUpdateForm # 👈 Indha MemberUpdateForm-a add pannu
from .models import DigitalResource
# Unnoda files-la irundhu imports
from .forms import SignUpForm, ReviewForm
from .models import Book, Member, IssuedBook, Review, Reservation
from .models import GENRE_CHOICES, Book, Review
from django.db.models import Q, Avg
from django.core.mail import send_mail
from django.conf import settings
import uuid
from datetime import date
from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Member, IssuedBook
# ---------------------------------------------------
# SIGNUP & OTP LOGIC
# ---------------------------------------------------

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            # Session-la data store pandrom
            request.session['signup_data'] = request.POST.dict() 
            
            # OTP Generate
            otp = str(random.randint(100000, 999999))
            request.session['otp'] = otp
            
            # Send Mail
            email = form.cleaned_data.get('email')
            send_mail(
                'DigiShelf OTP Verification',
                f'Welcome to DigiShelf! Your verification code is: {otp}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=True
            )
            return redirect('verify_otp')
        else:
            print("❌ FORM ERROR:", form.errors) # Debugging
    else:
        form = SignUpForm()
    
    return render(request, 'registration/signup.html', {'form': form})

def verify_otp(request):
    context = {}
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        session_otp = request.session.get('otp')
        signup_data = request.session.get('signup_data')

        if session_otp and entered_otp == session_otp:
            form = SignUpForm(signup_data)
            if form.is_valid():
                user = form.save() # User table save
                
                # Retrieve extra fields
                phone = form.cleaned_data.get('phone_number')
                addr = form.cleaned_data.get('address')
                genre = form.cleaned_data.get('favorite_genre') # 👇 IDHU DHAAN MUKKIYAM

                # Member table save with Link to User
                Member.objects.create(
                    user=user, # Link pandrom
                    name=user.username,
                    email=user.email,
                    phone_number=phone,
                    address=addr,
                    favorite_genre=genre # Save favorite genre
                )
                
                # Clean up session
                del request.session['otp']
                del request.session['signup_data']
                
                context['status'] = 'success'
        else:
            context['status'] = 'error'

    return render(request, 'registration/verify_otp.html', context)

def issue_book(request, book_id):
    # 1. Login Check (Safety Mechanism)
    if not request.user.is_authenticated:
        return redirect(f'/accounts/login/?next={request.path}')

    book = get_object_or_404(Book, id=book_id)

    # 2. Stock Check
    if book.stock_count > 0:
        # 3. Member Handling (Admin/New User Safe Fix)
        # User-ah Member table-la thedurom, illana pudhusa create panrom
        member, created = Member.objects.get_or_create(
            email=request.user.email,
            defaults={'name': request.user.username}
        )
        
        # 4. Book Issue Process
        IssuedBook.objects.create(member=member, book=book)
        
        # Stock Update
        book.stock_count -= 1
        book.save()
        
        # 5. Success Message (Idhu thaan Popup-a varum)
        messages.success(request, "Book requested successfully!")
        
        # Profile page-ku anuppurom (Anga popup varum + Book list irukkum)
        return redirect('profile')
    
    else:
        # Stock illana Error message
        messages.error(request, "Book is out of stock!")
        return redirect('book_detail', book_id=book.id)

# library/views.py

# library/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import IssuedBook, Member
from datetime import date

def profile(request):
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        member = Member.objects.get(email=request.user.email)
    except Member.DoesNotExist:
        member = Member.objects.create(name=request.user.username, email=request.user.email)

    # 👇 WE USE __icontains TO AVOID CASE-SENSITIVE ISSUES
    active_books = IssuedBook.objects.filter(member=member, status__icontains='issued')
    reserved_books = IssuedBook.objects.filter(member=member, status__icontains='reserved').order_by('issue_date')
    history_books = IssuedBook.objects.filter(member=member, status__icontains='returned')

    total_fine = 0
    today = date.today()
    for record in active_books:
        if record.due_date and today > record.due_date:
            total_fine += (today - record.due_date).days * 10

    context = {
        'member': member,
        'active_books': active_books, 
        'reserved_books': reserved_books, 
        'history_books': history_books, 
        'total_fine': total_fine,
        'today': today
    }
    return render(request, 'registration/profile.html', context)

def reserve_book(request, book_id):
    # 1. Login Check
    if not request.user.is_authenticated:
        return redirect(f'/accounts/login/?next={request.path}')

    book = get_object_or_404(Book, id=book_id)

    # 2. Member Profile Handling (Email based)
    member, created = Member.objects.get_or_create(
        email=request.user.email,
        defaults={'name': request.user.username}
    )

    # 3. Validation: Stock irundha reserve panna vida koodathu
    if book.stock_count > 0:
        messages.warning(request, "Book is available right now! Just request it.")
        return redirect('book_detail', book_id=book.id)

    # 4. Duplicate Check: User already waiting list-la irukkarra?
    # Note: 'issued' status-la irundhaalum thirumba reserve panna vida koodathu
    already_active = IssuedBook.objects.filter(
        member=member, 
        book=book, 
        status__in=['reserved', 'issued']
    ).exists()

    if already_active:
        messages.info(request, "You already have this book or you are already in the waiting list!")
    else:
        # 5. Create Reservation (Strictly 'reserved' status)
        # issue_date inga 'Booking Time'-ah work aagum
        IssuedBook.objects.create(
            member=member, 
            book=book, 
            status='reserved',
            issue_date=timezone.now() 
        )
        messages.success(request, "Book Reserved! We will auto-assign it to you when it's your turn.")

    return redirect('book_detail', book_id=book.id)

# library/views.py

# library/views.py

from .forms import ReviewForm # Idhu irukka nu check panniko

# library/views.py

from django.utils import timezone
from datetime import timedelta, date
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import IssuedBook

def return_book(request, issue_id):
    if not request.user.is_authenticated:
        return redirect('login')

    # get_object_or_404 use pannunga, try-except-a vida safe
    current_issue = get_object_or_404(IssuedBook, id=issue_id)
    
    if current_issue.status == 'returned':
        return redirect('profile')

    book = current_issue.book
    today = date.today()
    
    # 👇 MACHA, INGA DHAAN PUDHU UPDATE (FINE CHECK LOGIC) 👇
    # புக்குக்கு டியூ டேட் முடிஞ்சிருக்கான்னு ஃபர்ஸ்ட் செக் பண்றோம்
    if current_issue.due_date and today > current_issue.due_date:
        messages.warning(request, f"'{book.title}' is overdue! Redirecting to fine payment...")
        return redirect('pay_fine') # நேரா ஃபைன் பேஜுக்கு அனுப்பிடுறோம்
    # 👆 ---------------------------------------------------- 👆

    # 1. Status and Date update
    current_issue.returned_date = today
    current_issue.status = 'returned'
    current_issue.save() # Indha save kandippa nadakkanum

    # 2. Priority Logic (WAITLIST SYNC)
    # status__iexact='reserved' nu mathiruken, so models.py property kooda sync aagum
    next_reservation = IssuedBook.objects.filter(
        book=book, 
        status__iexact='reserved'
    ).order_by('issue_date').first()

    if next_reservation:
        next_reservation.status = 'issued'
        next_reservation.issue_date = timezone.now() # timezone.now() is safe for DateTimeField
        next_reservation.due_date = today + timedelta(days=14)
        next_reservation.save()
        
        # 👇 Notify waitlist user via Email
        try:
            subject = f"Good News! '{book.title}' is now Available for You"
            message = f"Hi {next_reservation.member.name},\n\nThe wait is over! The book '{book.title}' has just been returned. Since you were next in line on our waitlist, we have automatically issued it to you.\n\nYou have 14 days to read it (Due: {next_reservation.due_date.strftime('%d %B, %Y')}).\n\nEnjoy your reading!\n\nRegards,\nThe DigiShelf Team"
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [next_reservation.member.email],
                fail_silently=True
            )
            print(f"📧 Notification sent to {next_reservation.member.email}")
        except Exception as e:
            print(f"Error sending waitlist email: {e}")
        # 👆 ----------------------------
        
        messages.info(request, f"Book auto-issued to waitlist user: {next_reservation.member.name}")
    else:
        book.stock_count += 1
        book.save()
        messages.success(request, "Book returned successfully!")

    # 3. Redirecting to add_review as you requested
    return redirect('add_review', book_id=book.id)
    

def add_review(request, book_id):
    book = Book.objects.get(id=book_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.book = book
            # Member kandupidikka (User email vechu)
            member = Member.objects.get(email=request.user.email)
            review.member = member
            review.save()
            return redirect('profile')
    else:
        # Idhu thaan miss aachu! GET request varumpodhu empty form create aaganum.
        form = ReviewForm()
    
    return render(request, 'library/add_review.html', {'form': form, 'book': book})

def home(request):
    query = request.GET.get('q')
    selected_category = request.GET.get('category') 

    if query:
        books = Book.objects.filter(
            Q(title__icontains=query) | 
            Q(author__icontains=query) | 
            Q(category__icontains=query)
        )
    elif selected_category:
        books = Book.objects.filter(category=selected_category)
    else:
        books = Book.objects.all()
    
    for book in books:
        avg_rating = Review.objects.filter(book=book).aggregate(Avg('rating'))['rating__avg']
        book.avg_rating = round(avg_rating, 1) if avg_rating else "New"

    # -----------------------------------------------------------
    # 👇 MACHA, IDHU DHAAN PUDHU RECOMMENDATION LOGIC 👇
    # -----------------------------------------------------------
    recommended_books = None
    if request.user.is_authenticated:
        try:
            # யூசரோட Member ப்ரொஃபைலை எடுக்குறோம்
            member = Member.objects.get(user=request.user) 
            # அவங்களுக்கு புடிச்ச கேட்டகிரில ஸ்டாக் இருக்கிற 4 புக்ஸை மட்டும் எடுக்குறோம்
            recommended_books = Book.objects.filter(category=member.favorite_genre).exclude(stock_count=0)[:4]
            
            # ரெக்கமெண்டேஷன் புக்ஸுக்கும் ரேட்டிங் கால்குலேட் பண்றோம்
            for r_book in recommended_books:
                r_avg = Review.objects.filter(book=r_book).aggregate(Avg('rating'))['rating__avg']
                r_book.avg_rating = round(r_avg, 1) if r_avg else "New"
        except Member.DoesNotExist:
            pass
    # -----------------------------------------------------------

    context = {
        'books': books,
        'categories': GENRE_CHOICES, 
        'selected_category': selected_category,
        'recommended_books': recommended_books # 👈 இதையும் சேர்த்து அனுப்புறோம்
    }
    
    return render(request, 'index.html', context)

def load_more_books(request):
    category = request.GET.get('category')
    offset = int(request.GET.get('offset', 0)) # Evlo books already kaatitom
    limit = 6 # Aduthu evlo kaatanum
    
    books = Book.objects.filter(category=category).order_by('-id')[offset:offset+limit]
    
    data = []
    for book in books:
        # JSON ah mathi JS ku anupurom
        data.append({
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'category': book.category,
            'avg_rating': book.avg_rating if book.avg_rating else "New",
            'stock_count': book.stock_count,
        })
    
    return JsonResponse({'books': data})

def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    # Antha book-oda ella reviews-ayum edukurom (Latest first varum)
    reviews = Review.objects.filter(book=book).order_by('-created_at')
    
    return render(request, 'library/book_detail.html', {
        'book': book, 
        'reviews': reviews
    })

# library/views.py

# library/views.py

def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    
    # 👇 CORRECT CHECK: Login user email-um, Review potta member email-um onna?
    if request.user.email == review.member.email:
        review.delete()
        
    # Owner illana delete aagathu, summa redirect aagidum (Safety)
    return redirect('book_detail', book_id=review.book.id)

def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    book_id = review.book.id
    
    # 👇 CORRECT CHECK: Only Owner can Edit
    if request.user.email == review.member.email:
        review.delete() # Pazhaya review delete pannitu
        return redirect('add_review', book_id=book_id) # Puthusa eludha anupurom
        
    return redirect('book_detail', book_id=book_id)

# library/views.py kulla indha helper logic-a use pannalam

def get_waitlist_position(book, member):
    # 'reserved' status-la irukura ellarayum time padi adukkurom
    queue = IssuedBook.objects.filter(book=book, status='reserved').order_by('issue_date')
    
    # Adhula namma member-a thedurom
    for index, entry in enumerate(queue):
        if entry.member == member:
            return index + 1  # 1-st position, 2-nd position, etc.
    return None

def admin_dashboard(request):
    # Only Admin/Staff access verification
    if not request.user.is_staff:
        return redirect('home')

    # 1. Basic Stats Cards
    total_books = Book.objects.count()
    total_members = Member.objects.count()
    issued_count = IssuedBook.objects.filter(status='issued').count()
    returned_count = IssuedBook.objects.filter(status='returned').count()

    # 2. Graph Data: Last 7 Days - Books Issued vs Returned
    today = timezone.now().date()
    last_week = today - timedelta(days=7)

    # Group by Day (Issues)
    daily_issues = IssuedBook.objects.filter(
        issue_date__gte=last_week
    ).annotate(day=TruncDay('issue_date')).values('day').annotate(count=Count('id')).order_by('day')

    # Data prepare panrom JSON format la Chart.js kaga
    labels = []
    issue_data = []
    
    # Empty dates fill panna oru logic (Optional, but clean ah irukum)
    for i in range(7):
        date_point = last_week + timedelta(days=i)
        date_str = date_point.strftime('%d %b') # Ex: "24 Feb"
        labels.append(date_str)
        
        # Check if we have data for this date
        count = 0
        for entry in daily_issues:
            if entry['day'].date() == date_point:
                count = entry['count']
                break
        issue_data.append(count)

    context = {
        'total_books': total_books,
        'total_members': total_members,
        'issued_count': issued_count,
        'returned_count': returned_count,
        'graph_labels': labels,   # X-Axis (Dates)
        'graph_data': issue_data, # Y-Axis (Count)
    }
    return render(request, 'admin_dashboard.html', context)

def send_new_arrival_alert(book):
    # Yaarukellam indha category pudikum?
    interested_members = Member.objects.filter(favorite_genre=book.category)
    
    emails = [m.email for m in interested_members]
    
    if emails:
        subject = f"New Arrival in {book.category}: {book.title}"
        message = f"Hi Book Lover!\n\nA new book '{book.title}' by {book.author} has just arrived in your favorite category ({book.category}).\n\nLogin to DigiShelf and reserve it now!\n\nHappy Reading!"
        
        # Ellarukum ore nerathula anupurom (BCC maari thani thaniya loop layum podalam)
        send_mail(subject, message, settings.EMAIL_HOST_USER, emails, fail_silently=True)
        print(f"✅ Sent New Arrival Alert to {len(emails)} members.")


def reset_password(request):
    if request.method == 'POST':
        new_pass = request.POST.get('pass1')
        conf_pass = request.POST.get('pass2')
        email = request.session.get('reset_email')

        if new_pass == conf_pass:
            user = User.objects.get(email=email)
            user.set_password(new_pass) # 👇 Idhu dhaan password-a encrypt panni save pannum
            user.save()
            messages.success(request, "Password changed successfully! Login now.")
            return redirect('login')
        
# 1. Email vaangi OTP anupura function
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if User.objects.filter(email=email).exists():
            otp = str(random.randint(100000, 999999))
            request.session['reset_email'] = email
            request.session['reset_otp'] = otp
            
            send_mail(
                'Password Reset OTP',
                f'Your OTP for resetting DigiShelf password is: {otp}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=True
            )
            return redirect('reset_password_verify_otp')
        else:
            messages.error(request, "Email not found!")
    return render(request, 'registration/forgot_password.html')

# 2. OTP check pandra function
def reset_password_verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        session_otp = request.session.get('reset_otp')
        
        if entered_otp == session_otp:
            return redirect('set_new_password')
        else:
            messages.error(request, "Invalid OTP!")
    return render(request, 'registration/reset_password_verify_otp.html')

# 3. Pudhu password set pandra function
def set_new_password(request):
    if request.method == 'POST':
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')
        email = request.session.get('reset_email')
        
        if pass1 == pass2:
            user = User.objects.get(email=email)
            user.set_password(pass1) # Password-a encrypt pannum
            user.save()
            
            # Sessions-a clean pannidalam
            del request.session['reset_otp']
            del request.session['reset_email']
            
            messages.success(request, "Password reset successful! Please login.")
            return redirect('login')
        else:
            messages.error(request, "Passwords do not match!")
    return render(request, 'registration/set_new_password.html')

# library/views.py

# library/views.py

# library/views.py

def edit_profile(request):
    if not request.user.is_authenticated:
        return redirect('login')

    # 👇 Ippo namma User table-la irundhu directly email-a check panrom
    try:
        member = Member.objects.get(user=request.user)
    except Member.DoesNotExist:
        # User-kku profile illana, pudhusa create pandrom, but check panni create pandrom
        # 'email' unique ah irukkathala, first check pandrom
        if Member.objects.filter(email=request.user.email).exists():
            # Irundha antha existing member record-kku intha user-a link panrom
            member = Member.objects.get(email=request.user.email)
            member.user = request.user
            member.save()
        else:
            # Illana pudhusa create panrom
            member = Member.objects.create(
                user=request.user,
                name=request.user.username,
                email=request.user.email
            )
    
    if request.method == 'POST':
        form = MemberUpdateForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
    else:
        form = MemberUpdateForm(instance=member)
    
    return render(request, 'registration/edit_profile.html', {'form': form})


import uuid
from datetime import date
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Member, IssuedBook, Book # உன்னோட imports

# ... மத்த ஃபங்ஷன்ஸ் ...

# Mela imports-la idhu irukka nu check pannikko:
from django.core.mail import send_mail
from django.conf import settings
import uuid
from datetime import date
from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Member, IssuedBook

def pay_fine(request):
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        # யூசர் ப்ரொஃபைலை எடுக்குறோம்
        member = Member.objects.get(user=request.user)
    except Member.DoesNotExist:
        # Member profile இல்லன்னா, எரர் வராம புதுசா க்ரியேட் பண்றோம் இல்ல லிங்க் பண்றோம்
        if Member.objects.filter(email=request.user.email).exists():
            member = Member.objects.get(email=request.user.email)
            member.user = request.user
            member.save()
        else:
            member = Member.objects.create(
                user=request.user,
                name=request.user.username,
                email=request.user.email
            )
            
    # Active-ஆ இருக்குற புக்ஸை மட்டும் எடுக்குறோம்
    active_books = IssuedBook.objects.filter(member=member, status='issued')
    
    total_fine = 0
    today = date.today()
    
    overdue_books = [] 
    
    for record in active_books:
        # Due Date தாண்டிடுச்சானு செக் பண்றோம்
        if record.due_date and today > record.due_date:
            fine = (today - record.due_date).days * 10
            total_fine += fine
            
            # ஃபைன் இருக்குற புக்கை இந்த லிஸ்ட்ல சேர்க்குறோம்
            overdue_books.append(record)
            
    if total_fine == 0:
        messages.info(request, "You have no pending fines to pay.")
        return redirect('profile')

    transaction_id = "TXN" + str(uuid.uuid4().hex)[:10].upper()
    payment_date = timezone.now()

    # ஃபைன் கட்டுன புக்ஸை மட்டும் Return பண்றோம்
    for record in overdue_books:
        record.status = 'returned'
        record.returned_date = today
        record.save()
        
        # ஸ்டாக் ஏத்துறோம்
        book = record.book
        book.stock_count += 1
        book.save()

    # 👇 MACHA, INGA DHAAN MAIL ANUPPURA LOGIC ADD PANNIRUKEN 👇
    try:
        subject = "Payment Successful - No Pending Dues!"
        message = f"Hi {member.name},\n\nWe have successfully received your fine payment of ₹{total_fine}.\n\nTransaction ID: {transaction_id}\n\nYour overdue books have been automatically returned, and you currently have NO pending dues in your account.\n\nKeep reading and exploring with us!\n\nRegards,\nDigiShelf"
        
        # User-oda email-ku anuppurom
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [member.email],
            fail_silently=True # Error vandhalum crash aagama irukka
        )
    except Exception as e:
        print(f"Mail anuppumbodhu error: {e}")
    # 👆 ----------------------------------------------------- 👆

    # Receipt-க்கு டேட்டா அனுப்புறோம்
    context = {
        'member': member,
        'amount_paid': total_fine,
        'transaction_id': transaction_id,
        'date': payment_date,
        'paid_for_books': overdue_books, 
    }
    
    return render(request, 'library/fine_receipt.html', context)

# library/views.py


def lost_and_found(request):
    # 👇 MACHA, INGA DHAAN UPDATE PANNIRUKEN (exclude-a thookitu all() potachu) 👇
    items = LostAndFound.objects.all().order_by('-date_reported')
    
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')
            
        form = LostAndFoundForm(request.POST)
        if form.is_valid():
            lf_item = form.save(commit=False)
            lf_item.reported_by = request.user
            
            # 👇 MACHA, INGA DHAAN BUTTON LOGIC 👇
            action = request.POST.get('action') # Endha button click aachu nu paakurom
            
            if action == 'lost':
                lf_item.status = 'lost'
                messages.error(request, "Item reported as Lost. Admin will notify you once found.")
            elif action == 'found':
                lf_item.status = 'found'
                # User porul kedaichadhu nu sonna, udane Thanks mail!
                subject = "Thank you for your Help!"
                message = f"Hi {request.user.username},\n\nThank you for finding and reporting the '{lf_item.item_name}'. Your help is much appreciated!\n\nPlease hand it over to the Admin storage.\n\nRegards,\nDigiShelf"
                send_mail(subject, message, settings.EMAIL_HOST_USER, [request.user.email], fail_silently=True)
                messages.success(request, "Thanks for your help! Item reported as Found.")
                
            lf_item.save()
            return redirect('lost_and_found')
    else:
        form = LostAndFoundForm()
        
    return render(request, 'library/lost_and_found.html', {'items': items, 'form': form})

def digital_hub(request):
    category_filter = request.GET.get('category')
    search_query = request.GET.get('q') # 👇 சர்ச் பண்ண டைப் பண்ண வார்த்தை
    
    resources = DigitalResource.objects.all().order_by('-uploaded_at')
    
    # கேட்டகிரி செலக்ட் பண்ணிருந்தா...
    if category_filter:
        resources = resources.filter(category=category_filter)
        
    # சர்ச் பாக்ஸ்ல டைப் பண்ணிருந்தா...
    if search_query:
        resources = resources.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
        )
        
    categories = DigitalResource.CATEGORY_CHOICES
    
    return render(request, 'library/digital_hub.html', {
        'resources': resources,
        'categories': categories,
        'current_category': category_filter,
        'search_query': search_query # 👇 HTML-க்கு அனுப்புறோம்
    })