# report_generator.py

from input_handler import get_user_input
from data_processing import filter_excel_rows
import logging
import pandas as pd

def generate_report():
    try:
        start_value, end_value = get_user_input()
        result_df = filter_excel_rows(
            start_value, end_value
        )
        report_filename = f"report_{end_value.strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
        result_df.to_excel(report_filename, index=False)
        logging.info(f"Report generated and saved as {report_filename}")
    except Exception as e:
        logging.error("Error in report generation", exc_info=True)
        raise