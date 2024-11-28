from time import time, sleep
from jose import jwt, JWTError, status
from fastapi import HTTPException

# 테스트를 위한 SECRET_KEY 설정
class Settings:
    SECRET_KEY = "your_very_secure_secret_key"

settings = Settings()

# 수정된 JWT 함수 코드 (위에서 제공한 코드 삽입)
def create_jwt_token(email: str, user_id: int) -> str:
    if not settings.SECRET_KEY:
        raise ValueError("SECRET_KEY가 설정되지 않았습니다.")
    payload = {
        "user": email,
        "user_id": user_id,
        "iat": int(time()),
        "exp": int(time()) + 3600
    }
    try:
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        return token
    except Exception as e:
        raise RuntimeError(f"JWT 토큰 생성 실패: {e}")

def verify_jwt_token(token: str):
    if not settings.SECRET_KEY:
        raise ValueError("SECRET_KEY가 설정되지 않았습니다.")
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        exp = payload.get("exp")
        if exp is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token: 'exp' missing"
            )
        if time() > exp:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Token expired"
            )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid token: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unexpected error: {e}"
        )

# 테스트 함수
def test_jwt():
    print("\n--- 테스트 시작 ---\n")

    # 정상 토큰 생성 및 검증
    try:
        print("1. 정상 토큰 생성 및 검증")
        email = "test@example.com"
        user_id = 123
        token = create_jwt_token(email, user_id)
        print("Generated Token:", token)

        payload = verify_jwt_token(token)
        print("Verified Payload:", payload)
        assert payload["user"] == email
        assert payload["user_id"] == user_id
        print("✅ 정상 검증 성공\n")
    except Exception as e:
        print(f"❌ 정상 검증 실패: {e}\n")

    # 만료된 토큰 테스트
    try:
        print("2. 만료된 토큰 테스트")
        short_lived_token = create_jwt_token("expired@example.com", 456)
        print("Generated Short-lived Token:", short_lived_token)

        sleep(2)  # 2초 뒤 만료 (만료 시간 수정 필요 시 변경)
        verify_jwt_token(short_lived_token)
        print("❌ 만료된 토큰이 검증되었습니다. (오류 발생 필요)")
    except HTTPException as e:
        if e.detail == "Token expired":
            print("✅ 만료된 토큰 검증 실패 성공: Token expired\n")
        else:
            print(f"❌ 만료된 토큰 검증 실패: {e.detail}\n")

    # 잘못된 토큰 테스트
    try:
        print("3. 잘못된 토큰 테스트")
        invalid_token = "invalid.jwt.token"
        verify_jwt_token(invalid_token)
        print("❌ 잘못된 토큰이 검증되었습니다. (오류 발생 필요)")
    except HTTPException as e:
        if e.detail.startswith("Invalid token"):
            print("✅ 잘못된 토큰 검증 실패 성공: Invalid token\n")
        else:
            print(f"❌ 잘못된 토큰 검증 실패: {e.detail}\n")

    # SECRET_KEY가 없는 경우 테스트
    try:
        print("4. SECRET_KEY 없는 경우 테스트")
        original_key = settings.SECRET_KEY
        settings.SECRET_KEY = None  # SECRET_KEY 제거

        create_jwt_token("keyless@example.com", 789)
        print("❌ SECRET_KEY 없이 토큰이 생성되었습니다. (오류 발생 필요)")
    except ValueError as e:
        print(f"✅ SECRET_KEY 검증 실패 성공: {e}\n")
    finally:
        settings.SECRET_KEY = original_key  # SECRET_KEY 복원

    print("--- 테스트 종료 ---\n")

# 테스트 실행
test_jwt()
