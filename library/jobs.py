from datetime import date
from django.core.mail import send_mail
from django.conf import settings
from .models import IssuedBook

def send_due_date_alerts():
    print("🔄 [Scheduler] Checking books for today's alerts...") 
    today = date.today()
    
    # ரிட்டர்ன் பண்ணாத (issued) எல்லா புக்கையும் எடுக்குறோம்
    issued_books = IssuedBook.objects.filter(status='issued')

    for item in issued_books:
        # ==========================================
        # THE MASTER CHECK: ஒரு நாளைக்கு ஒரு மெயில் தான்!
        # ==========================================
        # இன்னைக்கு ஏற்கனவே மெயில் போயிருச்சான்னு பாக்குறோம்
        if item.last_alert_sent_date == today:
            continue  # ஆமா, போயிருச்சு! சோ இத ஸ்கிப் பண்ணிட்டு அடுத்த புக்குக்கு போ.

        # இன்னைக்கு தேதிக்கும், Due Date-க்கும் எவ்ளோ நாள் வித்தியாசம்னு பாக்குறோம்
        days_diff = (item.due_date - today).days

        subject = ""
        message = ""

        # ==========================================
        # நீ சொன்ன EXACT லாஜிக் (2 Days, 1 Day, Today, Overdue)
        # ==========================================
        if days_diff == 2:
            # Feb 25th நடக்கும்
            subject = f"Reminder: '{item.book.title}' is Due in 2 Days"
            message = (f"Hi {item.member.name},\n\n"
                       f"This is a gentle reminder from DigiShelf.\n\n"
                       f"The book '{item.book.title}' you borrowed is due on {item.due_date}.\n"
                       f"Please return it on time to avoid any late fines.\n\n"
                       f"Thank you,\n"
                       f"DigiShelf")
            
        elif days_diff == 1:
            # Feb 26th நடக்கும்
            subject = f"Reminder: '{item.book.title}' is Due Tomorrow"
            message = (f"Hi {item.member.name},\n\n"
                       f"This is a gentle reminder from DigiShelf.\n\n"
                       f"The book '{item.book.title}' you borrowed is due tomorrow, {item.due_date}.\n"
                       f"Please return it on time to avoid any late fines.\n\n"
                       f"Thank you,\n"
                       f"DigiShelf")
            
        elif days_diff == 0:
            # Feb 27th நடக்கும்
            
            subject = f"Urgent: '{item.book.title}' is Due TODAY"
            message = (f"Hi {item.member.name},\n\n"
                       f"This is an important update from DigiShelf.\n\n"
                       f"The book '{item.book.title}' you borrowed is due TODAY ({item.due_date}).\n"
                       f"Please return it by the end of the day to avoid any late fines.\n\n"
                       f"Thank you,\n"
                       f"DigiShelf")
            
        elif days_diff < 0:
            # Feb 28th, Mar 1st... தினமும் நடக்கும் (Overdue)
            days_late = abs(days_diff)
            subject = f"Overdue Alert: '{item.book.title}' is {days_late} Day(s) Late"
            message = (f"Hi {item.member.name},\n\n"
                       f"This is an urgent alert from DigiShelf.\n\n"
                       f"The book '{item.book.title}' you borrowed was due on {item.due_date} and is now {days_late} day(s) overdue.\n"
                       f"Please return it immediately to stop further late fines from accumulating.\n\n"
                       f"Thank you,\n"
                       f"DigiShelf")
        else:
            # 3 நாளோ, 10 நாளோ இருந்தா மெயில் அனுப்ப தேவையில்லை.
            continue 

        # ==========================================
        # மெயில் அனுப்புதல் & டேட்டாபேஸ் அப்டேட்
        # ==========================================
        if subject and message:
            # User-க்கு Email இருக்கான்னு செக் பண்ணி அனுப்புறோம்
            if item.member.email:
                full_message = message + "\n\n"
                try:
                    send_mail(subject, full_message, settings.EMAIL_HOST_USER, [item.member.email])
                    print(f"✅ Sent '{subject}' to {item.member.email}")
                    
                    # ரொம்ப முக்கியம்: மெயில் சக்சஸ் ஆனதும், "இன்னைக்கு முடிஞ்சது" னு Save பண்றோம்.
                    # இதனால அடுத்த 30 செகண்ட்ல Scheduler ரன் ஆனாலும் மெயில் போகாது!
                    item.last_alert_sent_date = today
                    item.save()
                    
                except Exception as e:
                    print(f"❌ Mail failed for {item.member.email}: {e}")
            else:
                print(f"⚠️ No email ID for user: {item.member.name}")