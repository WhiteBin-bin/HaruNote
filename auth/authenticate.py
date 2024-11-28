from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from models.users import User
from auth.jwt_handler import verify_jwt_token
from database.connection import get_session

# 요청이 들어올 때, Authorization 헤더에 토큰을 추출
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/signin")


async def authenticate(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    if not token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="액세스 토큰이 누락되었습니다.")

    # JWT 토큰에서 페이로드를 추출하여 user_id를 얻음
    payload = verify_jwt_token(token)
    user_id = payload.get("user_id")

    if not user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="유효하지 않은 토큰입니다.")

    # user_id를 통해 User 객체를 데이터베이스에서 조회

    user = session.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="사용자를 찾을 수 없습니다.")

    return user  # 이제는 User 객체를 반환