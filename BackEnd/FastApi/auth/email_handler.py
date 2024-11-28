from smtplib import SMTP, SMTPAuthenticationError, SMTPException
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from database.connection import Settings
import logging

settings = Settings()

# 로깅 설정
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

def send_verification_email(recipient_email: str, verification_url: str):
    """
    이메일 인증 링크 전송
    """
    smtp_server = settings.smtp_server
    smtp_port = settings.smtp_port
    smtp_user = settings.smtp_user
    smtp_pass = settings.smtp_password

    if not smtp_server or not smtp_port or not smtp_user or not smtp_pass:
        raise ValueError("SMTP 설정이 올바르지 않습니다.")

    subject = "Email Verification"
    message = MIMEMultipart()
    message["From"] = smtp_user
    message["To"] = recipient_email
    message["Subject"] = subject

    text_body = f"Please verify your email using the link below:\n{verification_url}"
    html_body = f"""
    <html>
    <body>
        <p>Please verify your email using the link below:</p>
        <a href="{verification_url}">{verification_url}</a>
    </body>
    </html>
    """
    message.attach(MIMEText(text_body, "plain"))
    message.attach(MIMEText(html_body, "html"))

    try:
        logging.info(f"Connecting to SMTP server {smtp_server}:{smtp_port}...")
        with SMTP(smtp_server, smtp_port, timeout=10) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, recipient_email, message.as_string())
        logging.info(f"Email sent to {recipient_email}")
    except SMTPAuthenticationError as e:
        logging.error(f"SMTP Authentication failed: {e}")
        raise
    except SMTPException as e:
        logging.error(f"SMTP Server error: {e}")
        raise
    except Exception as e:
        logging.error(f"Email sending failed: {e}")
        raise












