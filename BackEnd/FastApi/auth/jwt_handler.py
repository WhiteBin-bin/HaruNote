import time
from fastapi import HTTPException, status
from jose import jwt, JWTError
from database.connection import Settings  # 절대 경로 사용

# Settings 인스턴스 생성
settings = Settings()

# JWT 생성 함수
def create_jwt_token(email: str, user_id: int) -> str:
    """
    JWT 토큰 생성
    :param email: 사용자 이메일
    :param user_id: 사용자 ID
    :return: JWT 토큰 문자열
    """
    if not settings.secret_key:
        raise ValueError("SECRET_KEY가 설정되지 않았습니다.")

    payload = {
        "user": email,
        "user_id": user_id,
        "iat": int(time.time()),   # 발급 시간
        "exp": int(time.time()) + 3600  # 만료 시간 (1시간 후)
    }

    try:
        token = jwt.encode(payload, settings.secret_key, algorithm="HS256")
        return token
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"JWT 토큰 생성 실패: {str(e)}"
        )

# JWT 검증 함수
def verify_jwt_token(token: str):
    """
    JWT 토큰 검증
    :param token: JWT 토큰
    :return: 디코딩된 페이로드
    """
    if not settings.secret_key:
        raise ValueError("SECRET_KEY가 설정되지 않았습니다.")

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])

        # 필수 필드 확인
        if "user" not in payload or "user_id" not in payload:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token payload: Missing required fields"
            )

        # 만료 시간 확인
        exp = payload.get("exp")
        if time.time() > exp:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Token expired"
            )

        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid token: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unexpected error: {str(e)}"
        )

# 테스트 코드
if __name__ == "__main__":
    try:
        # JWT 생성 테스트
        print("JWT 토큰 생성 중...")
        token = create_jwt_token(email="test@example.com", user_id=123)
        print("생성된 JWT 토큰:", token)

        # JWT 검증 테스트
        print("JWT 토큰 검증 중...")
        decoded_payload = verify_jwt_token(token)
        print("디코딩된 페이로드:", decoded_payload)
    except HTTPException as e:
        print(f"Error: {e.detail}")
    except Exception as e:
        print(f"Unexpected Error: {e}")
