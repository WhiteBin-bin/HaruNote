import smtplib
from email.mime.text import MIMEText
from pydantic_settings import BaseSettings
from pydantic import Field, EmailStr, ValidationError
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# SMTP 설정 클래스
class Settings(BaseSettings):
    smtp_server: str = Field(env="SMTP_SERVER")  # SMTP 서버 주소
    smtp_port: int = Field(env="SMTP_PORT")      # SMTP 포트
    smtp_user: EmailStr = Field(env="SMTP_USER") # 발신자 이메일
    smtp_password: str = Field(env="SMTP_PASSWORD")  # 발신자 비밀번호 또는 앱 비밀번호
    database_url: str = Field(env="DATABASE_URL", default=None)     # 데이터베이스 URL
    secret_key: str = Field(env="SECRET_KEY", default=None)         # 애플리케이션 비밀 키

    class Config:
        env_file = ".env"  # .env 파일 경로
        env_file_encoding = "utf-8"  # 파일 인코딩
        extra = "allow"  # 추가 입력 허용

# SMTP 설정 로드
try:
    settings = Settings()
    logging.info("Settings loaded successfully.")
except ValidationError as e:
    logging.error("Settings validation failed. Please check your .env file: %s", e)
    raise SystemExit("Failed to load SMTP settings. Exiting...")

# SMTP 설정 출력 (디버깅용, 실제 서비스에서는 제거 가능)
logging.info(f"SMTP Server: {settings.smtp_server}")
logging.info(f"SMTP Port: {settings.smtp_port}")
logging.info(f"SMTP User: {settings.smtp_user}")

# 이메일 전송 함수
def send_test_email(recipient_email: str, subject: str, body: str):
    """
    이메일 전송 함수
    """
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = settings.smtp_user
    msg["To"] = recipient_email

    try:
        logging.info("테스트 이메일 전송 중...")
        # SMTP 서버 연결
        with smtplib.SMTP(settings.smtp_server, settings.smtp_port) as server:
            server.starttls()  # TLS 활성화
            server.login(settings.smtp_user, settings.smtp_password)  # SMTP 로그인
            server.sendmail(settings.smtp_user, recipient_email, msg.as_string())  # 이메일 전송
        logging.info(f"테스트 이메일 전송 성공! Recipient: {recipient_email}")
    except smtplib.SMTPAuthenticationError as e:
        logging.error(f"SMTP 인증 실패: {e.smtp_code} - {e.smtp_error.decode()}")
        raise RuntimeError(f"SMTP Authentication failed: {e}")
    except smtplib.SMTPException as e:
        logging.error(f"SMTP 오류 발생: {e}")
        raise RuntimeError(f"SMTP error occurred: {e}")
    except Exception as e:
        logging.error(f"알 수 없는 오류로 이메일 전송 실패: {e}")
        raise RuntimeError(f"Failed to send email: {e}")

# 테스트 실행 코드
if __name__ == "__main__":
    try:
        # 테스트 이메일 정보
        test_recipient = "theman0149@gmail.com"
        test_subject = "테스트 이메일"
        test_body = "이 이메일은 SMTP 설정 테스트를 위해 전송되었습니다."

        # 이메일 전송
        send_test_email(test_recipient, test_subject, test_body)
    except Exception as e:
        logging.error(f"테스트 이메일 전송 실패: {e}")


