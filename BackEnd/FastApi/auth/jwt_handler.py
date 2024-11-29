from time import time
from fastapi import HTTPException, status
from jose import jwt, JWTError
from database.connection import Settings
from pathlib import Path
from typing import Dict, Optional

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


# Token 생성 함수
def create_tokens(
        email: str,
        user_id: int,
        access_expires: int = 3600,  # 1시간
        refresh_expires: int = 604800  # 7일
) -> Dict[str, str]:
    current_time = time()

    # Access Token 생성
    access_payload = {
        "user": email,
        "user_id": user_id,
        "iat": current_time,
        "exp": current_time + access_expires,
        "type": "access"
    }

    # Refresh Token 생성
    refresh_payload = {
        "user": email,
        "user_id": user_id,
        "iat": current_time,
        "exp": current_time + refresh_expires,
        "type": "refresh"
    }

    access_token = jwt.encode(access_payload, private_key, algorithm="RS256")
    refresh_token = jwt.encode(refresh_payload, private_key, algorithm="RS256")

    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }


# JWT 토큰 검증
def verify_jwt_token(token: str, token_type: str = "access") -> Dict:
    try:
        payload = jwt.decode(token, public_key, algorithms=["RS256"])

        # 토큰 타입 검증
        if payload.get("type") != token_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"잘못된 토큰 타입입니다. {token_type} 토큰이 필요합니다."
            )

        # 만료 시간 검증
        exp = payload.get("exp")
        if exp is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="토큰에 만료 시간이 없습니다."
            )

        if time() > exp:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="토큰이 만료되었습니다."
            )

        return payload

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"유효하지 않은 토큰입니다: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"토큰 검증 실패: {str(e)}"
        )


# Refresh Token으로 새 Access Token 발급
def refresh_access_token(refresh_token: str) -> Dict[str, str]:
    try:
        # Refresh Token 검증
        payload = verify_jwt_token(refresh_token, token_type="refresh")

        # 새로운 토큰 쌍 생성
        return create_tokens(
            email=payload["user"],
            user_id=payload["user_id"]
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"토큰 갱신 실패: {str(e)}"
        )