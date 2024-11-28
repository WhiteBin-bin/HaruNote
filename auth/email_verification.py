from jose import jwt, JWTError, ExpiredSignatureError
from datetime import datetime, timedelta
from database.connection import Settings

settings = Settings()

def create_email_verification_token(email: str, expire_minutes: int = 15) -> str:
    #이메일 검증 토큰 생성
    now = datetime.utcnow()
    expire = now + timedelta(minutes=expire_minutes)
    payload = {
        "sub": email,
        "iat": now.timestamp(),
        "exp": expire.timestamp()
    }
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")

def verify_email_verification_token(token: str) -> str:
    #이메일 검증 토큰 검증
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        exp = payload.get("exp")
        sub = payload.get("sub")

        if not sub:
            raise ValueError("Token payload missing 'sub' field")
        if datetime.utcnow().timestamp() > exp:
            raise ExpiredSignatureError("Token has expired")

        return sub

    except ExpiredSignatureError:
        raise ValueError("Token has expired")
    except JWTError:
        raise ValueError("Invalid token format")


