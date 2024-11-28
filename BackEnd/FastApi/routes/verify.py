from fastapi import APIRouter, HTTPException, Query, Depends
from sqlmodel import Session
from models.users import User
from database.connection import get_session
from auth.email_handler import send_verification_email
from auth.email_verification import EmailVerification
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)

# 설정
email_verification = EmailVerification(secret_key="your_very_secure_secret_key")

router = APIRouter()

@router.post("/request-email-verification")
def request_email_verification(email: str, session: Session = Depends(get_session)):
    """이메일 인증 요청"""
    user = session.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    token = email_verification.create_token(email)
    verification_url = f"http://localhost:8000/verify-email?token={token}"
    send_verification_email(email, verification_url)
    logging.info(f"Verification email sent to {email}")

    return {"message": "Verification email sent."}

@router.get("/verify-email")
def verify_email(token: str = Query(...), session: Session = Depends(get_session)):
    """이메일 인증 처리"""
    try:
        email = email_verification.verify_token(token)
        user = session.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if user.is_verified:
            return {"message": "Email already verified"}

        user.is_verified = True
        session.commit()
        logging.info(f"Email verified successfully for {email}")
        return {"message": "Email verified successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))




