# input_handler.py
import pandas as pd
import logging

def get_user_input():
    try:
        start_value = pd.to_datetime(input("Enter the start date (MM-DD-YYYY): "))
        end_value = pd.to_datetime(input("Enter the end date (MM-DD-YYYY): "))
        return start_value, end_value
    except Exception as e:
        logging.error("Invalid date input. Please enter dates in MM-DD-YYYY format.", exc_info=True)
        raise
