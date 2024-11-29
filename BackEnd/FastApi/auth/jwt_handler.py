from time import time
from fastapi import HTTPException, status
from jose import jwt
from database.connection import Settings
from pathlib import Path

settings = Settings()

# 키 파일 읽기
def load_keys():
    current_dir = Path(__file__).parent
    with open(current_dir / "private.pem", "r") as f:
        private_key = f.read()
    with open(current_dir / "public.pem", "r") as f:
        public_key = f.read()
    return private_key, public_key

private_key, public_key = load_keys()

# JWT 토큰 생성 (private key 사용)
def create_jwt_token(email: str, user_id: int) -> str:
    payload = {
        "user": email,
        "user_id": user_id,
        "iat": time(),
        "exp": time() + 3600
    }
    token = jwt.encode(payload, private_key, algorithm="RS256")
    return token

# JWT 토큰 검증 (public key 사용)
def verify_jwt_token(token: str):
    try:
        payload = jwt.decode(token, public_key, algorithms=["RS256"])
        exp = payload.get("exp")
        if exp is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token"
            )
        if time() > exp:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Token expired"
            )
        return payload
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token"
        )