import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from database.connection import Settings
import logging

settings = Settings()

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def send_verification_email(recipient_email: str, token: str):
    #이메일 검증 링크 전송
    smtp_server = settings.smtp_server
    smtp_port = settings.smtp_port
    smtp_user = settings.smtp_user
    smtp_pass = settings.smtp_password

    verification_url = f"http://example.com/verify?token={token}"
    subject = "Email Verification"

    # MIMEMultipart 객체 생성 (텍스트 및 확장 가능)
    message = MIMEMultipart()
    message["From"] = smtp_user
    message["To"] = recipient_email
    message["Subject"] = subject

    # 이메일 본문 (HTML 및 텍스트 동시 지원 가능)
    text_body = f"Please click the link below to verify your email:\n{verification_url}"
    html_body = f"""
    <html>
    <body>
        <p>Please click the link below to verify your email:</p>
        <a href="{verification_url}">{verification_url}</a>
    </body>
    </html>
    """
    message.attach(MIMEText(text_body, "plain"))  # 텍스트 메시지 추가
    message.attach(MIMEText(html_body, "html"))   # HTML 메시지 추가

    try:
        # SMTP 서버 연결 및 이메일 전송
        logging.info(f"Connecting to SMTP server {smtp_server}:{smtp_port}...")
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # TLS 활성화
            server.login(smtp_user, smtp_pass)  # 로그인
            server.sendmail(smtp_user, recipient_email, message.as_string())
        logging.info(f"Verification email sent successfully to {recipient_email}")
    except Exception as e:
        logging.error(f"Failed to send email to {recipient_email}: {e}")
        raise RuntimeError(f"Failed to send email: {e}")









