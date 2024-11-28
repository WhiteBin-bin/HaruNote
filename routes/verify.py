from fastapi import APIRouter, HTTPException, Query, Depends
from auth.email_handler import send_verification_email
from auth.email_verification import create_email_verification_token, verify_email_verification_token
from sqlmodel import Session
from models.users import User
from database.connection import get_session
import logging

router = APIRouter()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

@router.post("/request-email-verification")
def request_email_verification(email: str, session: Session = Depends(get_session)):
    """
    이메일 검증 요청
    """
    logging.info(f"Received email verification request for: {email}")

    # 사용자 검색
    user = session.query(User).filter(User.email == email).first()
    if not user:
        logging.error(f"No user found with email: {email}")
        raise HTTPException(status_code=404, detail="User not found")

    try:
        # 검증 토큰 생성
        token = create_email_verification_token(email)
        verification_url = f"http://localhost:8000/verify-email?token={token}"
        logging.info(f"Generated verification URL: {verification_url}")

        # 이메일 전송
        send_verification_email(email, verification_url)
        logging.info(f"Verification email sent to: {email}")

    except Exception as e:
        # 에러 발생 시 로그 출력
        logging.error(f"Error sending verification email: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return {"message": "Verification email sent"}

@router.get("/verify-email")
def verify_email(token: str = Query(...), session: Session = Depends(get_session)):
    """
    이메일 검증
    """
    try:
        email = verify_email_verification_token(token)
        user = session.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # 이메일 검증 상태 업데이트
        user.is_verified = True
        session.add(user)
        session.commit()

        return {"message": f"Email {email} successfully verified"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
