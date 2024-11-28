import time
from fastapi import HTTPException, status
from jose import jwt, JWTError
from database.connection import Settings  # Settings 클래스 가져오기

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
    payload = {
        "user": email,
        "user_id": user_id,
        "iat": time.time(),  # 발급 시간
        "exp": time.time() + 3600  # 만료 시간 (1시간 후)
    }
    try:
        token = jwt.encode(payload, settings.secret_key, algorithm="HS256")
        return token
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token generation failed: {str(e)}"
        )

# JWT 검증 함수
def verify_jwt_token(token: str):
    """
    JWT 토큰 검증
    :param token: JWT 토큰
    :return: 디코딩된 페이로드
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        exp = payload.get("exp")
        if exp is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token: Missing expiration"
            )
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
# 테스트 코드
if __name__ == "__main__":
    try:
        # JWT 생성
        print("JWT 토큰 생성 중...")
        token = create_jwt_token("eun062323@gmail.com", 42)
        print("Generated Token:", token)

        # JWT 검증
        print("JWT 토큰 검증 중...")
        decoded_payload = verify_jwt_token(token)
        print("Decoded Payload:", decoded_payload)
    except HTTPException as e:
        print(f"Error: {e.detail}")
