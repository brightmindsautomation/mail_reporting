# scheduler.py
from datetime import datetime
import time
from report_generator import generate_report
import logging

def scheduler():
    while True:
        try:
            generate_report()
            # current_time = datetime.now().time()
            # if current_time.hour == 18 and current_time.minute == 0:
                # generate_report()
            time.sleep(10)  # Check every 10 seconds
        except Exception as e:
            logging.error("Unexpected error in scheduler loop", exc_info=True)
            raise
