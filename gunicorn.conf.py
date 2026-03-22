import multiprocessing
import os

# Gunicorn configuration
bind = "0.0.0.0:" + os.environ.get("PORT", "10000")
workers = 2 # Fixed small number of workers for free tier
timeout = 120 # Increased timeout for slow DB/Video
worker_class = 'sync'
preload_app = True
