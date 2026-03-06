import logging
import json

#The gunicorn logs are in a different format because gunicorn has its own logger that bypasses the JSONFormatter in app.py. 
#This is the custom log config file for gunicorn.

class JSONFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": "backend"
        })

def on_starting(server):
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    
    # Apply to gunicorn loggers
    for name in ["gunicorn", "gunicorn.error", "gunicorn.access"]:
        log = logging.getLogger(name)
        log.handlers = [handler]
        log.propagate = False