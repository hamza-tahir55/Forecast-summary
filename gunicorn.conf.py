# gunicorn.conf.py
bind = "0.0.0.0:8080"
timeout = 120  # Increase to 2 minutes (adjust as needed)
workers = 2    # You can tune this depending on memory
