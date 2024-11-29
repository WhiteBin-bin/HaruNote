import random
import smtplib
from email.mime.text import MIMEText

def generate_verification_code():
    return str(random.randint(1000, 9999))

def send_email_verification(email: str, code: str):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "whrudgh83@gmail.com"
    sender_password = "ayjd vmrb rjif pffz"

    message = MIMEText(f"Your verification code is: {code}")
    message['Subject'] = "Verification Code"
    message['From'] = sender_email
    message['To'] = email

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email, message.as_string())