import smtplib
from email.mime.text import MIMEText
from pydantic import BaseSettings, EmailStr
import logging

class Settings(BaseSettings):
    """
    환경 변수 관리
    """
    SMTP_SERVER: str = "smtp.gmail.com"  # 기본 값
    SMTP_PORT: int = 587
    SMTP_USER: EmailStr
    SMTP_PASSWORD: str

    class Config:
        env_file = ".env"  # 환경 변수 파일 위치


settings = Settings()

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def send_email(to_email: str, subject: str, body: str):
    """
    이메일 전송
    """
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_USER
    msg["To"] = to_email

    try:
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()  # TLS 활성화
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)  # 로그인
            server.sendmail(settings.SMTP_USER, to_email, msg.as_string())
        logging.info(f"Email successfully sent to {to_email}")
    except Exception as e:
        logging.error(f"Failed to send email to {to_email}: {e}")
        raise RuntimeError("Failed to send email") from e


def send_verification_email(email: str, verification_url: str):
    """
    이메일 검증 링크 전송
    """
    subject = "Email Verification"
    body = f"""
    Hello,

    Please verify your email by clicking the link below:

    {verification_url}

    If you did not request this email, please ignore it.

    Thank you.
    """
    send_email(email, subject, body)

