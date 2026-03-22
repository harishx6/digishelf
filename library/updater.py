from apscheduler.schedulers.background import BackgroundScheduler
from .jobs import send_due_date_alerts

def start():
    scheduler = BackgroundScheduler()
    
    # 12 Hours-க்கு ஒருக்கா ரன் ஆக செட் பண்ணியாச்சு!
    scheduler.add_job(send_due_date_alerts, 'interval', hours=12)
    
    scheduler.start()