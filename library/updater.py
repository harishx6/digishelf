from apscheduler.schedulers.background import BackgroundScheduler
from .jobs import send_due_date_alerts

def start():
    scheduler = BackgroundScheduler()
    
    # 30 Seconds-க்கு ஒருக்கா ரன் ஆக செட் பண்ணியாச்சு!
    scheduler.add_job(send_due_date_alerts, 'interval', seconds=10)
    
    scheduler.start()