import multiprocessing
import os

# Gunicorn configuration
bind = "0.0.0.0:" + os.environ.get("PORT", "10000")
workers = 1 # Single worker for maximum stability on 512MB RAM
timeout = 120 # Increased timeout for slow DB/Video
worker_class = 'sync'
preload_app = True
