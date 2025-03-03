import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import os
from email.mime.base import MIMEBase
from email import encoders
import time

def generate_report():
    file_path = "To-Vend.xlsx"
    current_time = datetime.today().time()
    start_value = pd.to_datetime(input("Enter the start date (MM-DD-YYYY): "))# pd.to_datetime("2-4-25 0:00")
    end_value = pd.to_datetime(input("Enter the end date (MM-DD-YYYY): "))# pd.to_datetime("2-4-25 23:00")     
    recipient_emails = ["shiv@outlook.com", "deepu@outlook.com"]
    result_df = filter_excel_rows(file_path, start_value, end_value, recipient_emails)
    report_filename = f"report_{end_value.strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
    result_df.to_excel(report_filename, index=False)
    print(f"Report generated and saved as {report_filename}")

def filter_excel_rows(file_path, start_value, end_value, recipient_emails):
    # Read the Excel file
    df = pd.read_excel(file_path, header=0, parse_dates=[0])  # Parse first column as datetime
    
    # Rename the first column as it has no header
    first_col_name = "Datetime"
    df.insert(0, first_col_name, df.pop(df.columns[0]))
    
    # Filter rows based on the first column values
    filtered_df = df[(df[first_col_name] >= start_value) & (df[first_col_name] <= end_value)]
    
    # Further filter rows using specific column names
    selected_df = filtered_df[(filtered_df["6001.P"] > 6000) & (filtered_df["6002.P"] < 2000)]
    
    # Calculate Up Time for each column
    total_points = len(filtered_df)
    up_time_row = {col: 0 for col in selected_df.columns}
    up_time_row[first_col_name] = "Up Time"
    
    # Exclude columns "6001.P" and "6002.P" from percentage calculation
    excluded_columns = {"6001.P", "6002.P", "4022.M", "4040.M", "4045.M"}
    percentage_row = {col: 0 for col in selected_df.columns}
    percentage_row[first_col_name] = "Percentage"
    
    percentage_values = []
    grouped_columns = {"Group1": ["4009.M", "4010.M"], "Group2": ["4012.M", "4013.M", "4014.M"]}  # Define column groups
    min_percentage_per_group = {}
    
    for col in selected_df.columns[1:]:  # Exclude the first column
        if col in excluded_columns:
            up_time_row[col] = 0
            percentage_row[col] = 0
            continue
        
        if selected_df[col].dtype == object:  # Only process categorical columns
            total_countUtime = filtered_df[col].count()
            validTotal_count = selected_df[col].count()
            up_time = round((validTotal_count / total_countUtime) * 100, 2) if total_countUtime > 0 else 0
            up_time_row[col] = up_time
            
            if col == "4070.M":
                percentCount_value = (selected_df[col] == "MA").sum()
            else:
                percentCount_value = (selected_df[col] == "AU").sum()
            
            percentage = round((percentCount_value * 100) / validTotal_count, 2) if validTotal_count > 0 else 0
            
            # Assign percentage to its group
            for group, columns in grouped_columns.items():
                if col in columns:
                    if group not in min_percentage_per_group or percentage < min_percentage_per_group[group]:
                        min_percentage_per_group[group] = percentage
            
            percentage_row[col] = percentage
            percentage_values.append(percentage)
    
    # Keep only the lowest percentage per group
    filtered_percentage_row = {col: 0 for col in selected_df.columns}
    filtered_percentage_row[first_col_name] = "Filtered Percentage"
    for group, min_value in min_percentage_per_group.items():
        filtered_percentage_row[group] = min_value
    
    # Append the Up Time row before the percentage row
    up_time_df = pd.DataFrame([up_time_row])
    selected_df = pd.concat([selected_df, up_time_df], ignore_index=True)
    
    # Append the percentage row at the end
    percentage_df = pd.DataFrame([percentage_row])
    selected_df = pd.concat([selected_df, percentage_df], ignore_index=True)
    
    # Calculate and append the average percentage
    avg_percentage = round(sum(percentage_values) / len(percentage_values), 2) if percentage_values else 0
    ThresholdPercentage = avg_percentage
    print(avg_percentage)
    
    # Generate table with filtered values
    table_data = []
    for col, percentage in percentage_row.items():
        if col != first_col_name and percentage < 80:
            table_data.append([col, "Desc " + col, percentage])
    
    table_df = pd.DataFrame(table_data, columns=["Item Name", "Description", "Percentage in Normal State"])
    print(table_df)
    
    # Send email with table and ThresholdPercentage
    report_file = "Generated_Report.xlsx"
    selected_df.to_excel(report_file, index=False)

    for email in recipient_emails:
        send_email(table_df, ThresholdPercentage, email, report_file)
    
    return selected_df

# Execution stopped. Remove the loop to prevent continuous execution.
def send_email(table_df, ThresholdPercentage, recipient_email, report_file):
    sender_email = "sarmid97@gmail.com"
    sender_password = "usdt ujse ujgj ppmi"
    subject = "Generated Report"

    # Convert DataFrame to HTML
    table_html = table_df.to_html(index=False)

    body = f"""
    <html>
    <body>
        <p>Dear User,</p>
        <p>Please find the generated report attached.</p>
        <p><strong>Total percentage Normal State: {ThresholdPercentage}%</strong></p>
        {table_html}
        <p>Best Regards,</p>
        <p>Your Automation System</p>
    </body>
    </html>
    """

    # Setup the email message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    # Attach the report file
    with open(report_file, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(report_file)}")
    msg.attach(part)

    # Send the email
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)  # Change SMTP server and port as needed
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()
        print("Email sent successfully with attachment!")
    except Exception as e:
        print(f"Failed to send email: {e}")

while True:
    current_time = datetime.now().time()
    if current_time.hour == 18 and current_time.minute == 0:
        generate_report()
        time.sleep(60)  # Wait a minute to avoid multiple triggers
    time.sleep(10)  # Check every 10 seconds

# generate_report()
# time.sleep(30)
