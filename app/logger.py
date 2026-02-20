import logging
import os
from logging.handlers import RotatingFileHandler
from contextvars import ContextVar

# ContextVar לשמירת ה-Trace ID
request_id_contextvar = ContextVar("request_id", default="SYSTEM")

def setup_logging():
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logger = logging.getLogger("menumaster")
    logger.setLevel(logging.INFO)
    
    # מניעת כפילות לוגים
    if logger.hasHandlers():
        logger.handlers.clear()

    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [TraceID: %(request_id)s] %(message)s'
    )

    # כתיבה לקובץ עם Rotation
    file_handler = RotatingFileHandler(
        f"{log_dir}/app.log", maxBytes=5*1024*1024, backupCount=5
    )
    file_handler.setFormatter(formatter)

    # כתיבה לטרמינל
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    class RequestIDFilter(logging.Filter):
        def filter(self, record):
            record.request_id = request_id_contextvar.get()
            return True

    logger.addFilter(RequestIDFilter())
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

logger = setup_logging()