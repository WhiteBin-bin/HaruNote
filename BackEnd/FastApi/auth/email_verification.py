from jose import jwt, JWTError, ExpiredSignatureError
from datetime import datetime, timedelta

class EmailVerification:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key

    def create_token(self, email: str, expire_minutes: int = 15) -> str:
        """
        이메일 인증 토큰 생성
        :param email: 사용자 이메일
        :param expire_minutes: 토큰 만료 시간 (기본값 15분)
        :return: 생성된 토큰
        """
        now = datetime.utcnow()
        expire = now + timedelta(minutes=expire_minutes)
        payload = {
            "sub": email,
            "iat": int(now.timestamp()),  # 발급 시간
            "exp": int(expire.timestamp())  # 만료 시간
        }
        try:
            return jwt.encode(payload, self.secret_key, algorithm="HS256")
        except Exception as e:
            raise RuntimeError(f"Token creation failed: {e}")

    def verify_token(self, token: str) -> str:
        """
        이메일 인증 토큰 검증
        :param token: 인증 토큰
        :return: 이메일 주소
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            email = payload.get("sub")
            exp = payload.get("exp")

            if not email:
                raise ValueError("Invalid token payload: 'sub' is missing.")
            if datetime.utcnow().timestamp() > exp:
                raise ExpiredSignatureError("Token expired.")

            return email
        except ExpiredSignatureError as e:
            raise ValueError(f"Token expired: {e}")
        except JWTError as e:
            raise ValueError(f"Invalid token: {e}")











