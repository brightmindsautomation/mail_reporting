# main.py
from logger import setup_logger
setup_logger()

import logging
from scheduler import scheduler

if __name__ == "__main__":
    logging.info("Starting application")
    try:
        scheduler()
    except Exception:
        logging.error("Unhandled exception in main.", exc_info=True)
        raise
    input("Press Enter to exit...")
