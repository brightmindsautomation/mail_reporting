# data_processing.py
import pandas as pd
import os
from email_sender import send_email
from config import RECIPIENT_EMAILS, FILE_PATH

def filter_excel_rows(start_value, end_value):
    df = pd.read_excel(FILE_PATH, header=0, parse_dates=[0])
    df.insert(0, "Datetime", df.pop(df.columns[0]))

    filtered_df = df[(df["Datetime"] >= start_value) & (df["Datetime"] <= end_value)]
    selected_df = filtered_df[(filtered_df["6001.P"] > 6000) & (filtered_df["6002.P"] < 2000)]

    total_points = len(filtered_df)
    up_time_row = {col: 0 for col in selected_df.columns}
    up_time_row["Datetime"] = "Up Time"

    excluded_columns = {"6001.P", "6002.P", "4022.M", "4040.M", "4045.M"}
    percentage_row = {col: 0 for col in selected_df.columns}
    percentage_row["Datetime"] = "Percentage"

    percentage_values = []
    grouped_columns = {"Group1": ["4009.M", "4010.M"], "Group2": ["4012.M", "4013.M", "4014.M"]}
    min_percentage_per_group = {}

    for col in selected_df.columns[1:]:
        if col in excluded_columns:
            continue
        if selected_df[col].dtype == object:
            valid_count = selected_df[col].count()
            total_count = filtered_df[col].count()
            up_time = round((valid_count / total_count) * 100, 2) if total_count > 0 else 0
            up_time_row[col] = up_time

            if col == "4070.M":
                percent_count = (selected_df[col] == "MA").sum()
            else:
                percent_count = (selected_df[col] == "AU").sum()

            percentage = round((percent_count * 100) / valid_count, 2) if valid_count > 0 else 0
            percentage_row[col] = percentage
            percentage_values.append(percentage)

            for group, columns in grouped_columns.items():
                if col in columns:
                    if group not in min_percentage_per_group or percentage < min_percentage_per_group[group]:
                        min_percentage_per_group[group] = percentage

    table_data = []
    for col, percentage in percentage_row.items():
        if col != "Datetime" and percentage < 80:
            table_data.append([col, "Desc " + col, percentage])

    avg_percentage = round(sum(percentage_values) / len(percentage_values), 2) if percentage_values else 0

    selected_df = pd.concat([selected_df, pd.DataFrame([up_time_row]), pd.DataFrame([percentage_row])], ignore_index=True)
    report_file = "Generated_Report.xlsx"
    selected_df.to_excel(report_file, index=False)

    table_df = pd.DataFrame(table_data, columns=["Item Name", "Description", "Percentage in Normal State"])

    for email in RECIPIENT_EMAILS:
        send_email(table_df, avg_percentage, email, report_file)
    
    return selected_df
