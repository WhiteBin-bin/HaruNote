from datetime import datetime, timedelta
from jose import jwt, JWTError
from database.connection import Settings

settings = Settings()

# 이메일 검증 토큰 생성
def create_email_verification_token(email: str, expire_minutes: int = 15) -> str:
    """
    이메일 검증용 JWT 토큰 생성
    """
    expire = datetime.utcnow() + timedelta(minutes=expire_minutes)
    payload = {
        "sub": email,
        "type": "email_verification",
        "exp": expire.timestamp()
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


# 이메일 검증 토큰 검증
def verify_email_verification_token(token: str) -> str:
    """
    이메일 검증용 JWT 토큰 검증
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "email_verification":
            raise ValueError("Invalid token type")

        exp_timestamp = payload.get("exp")
        if exp_timestamp is None or datetime.utcnow() > datetime.utcfromtimestamp(exp_timestamp):
            raise ValueError("Token has expired")

        email = payload.get("sub")
        if email is None:
            raise ValueError("Invalid token payload")

        return email
    except JWTError:
        raise ValueError("Invalid or expired token")
