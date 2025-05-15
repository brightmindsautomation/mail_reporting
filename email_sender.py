# email_sender.py
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from config import SENDER_EMAIL, EMAIL_PASSWORD, SMTP_SERVER, SMTP_PORT
import os
import logging

#def send_email(table_df, percentage, recipient_email, report_file, sender_email, email_password, smtp_server, smtp_port):
def send_email(table_df, percentage, recipient_email, report_file):
    subject = "Generated Report"
    body = f"""
    <html>
    <body>
        <p>Dear User,</p>
        <p>Please find the generated report attached.</p>
        <p><strong>Total percentage Normal State: {percentage}%</strong></p>
        {table_df.to_html(index=False)}
        <p>Best Regards,<br>Your Automation System</p>
    </body>
    </html>
    """

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    with open(report_file, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(report_file)}")
        msg.attach(part)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, EMAIL_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())
        logging.info(f"Report data processed and emails sent to {recipient_email}")
    except Exception as e:
        logging.error(f"Failed to send email to {recipient_email}", exc_info=True)
        raise
