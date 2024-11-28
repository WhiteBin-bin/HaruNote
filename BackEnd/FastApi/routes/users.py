from typing import List
from fastapi import APIRouter, HTTPException, status, Depends, Query
from auth.authenticate import authenticate
from auth.jwt_handler import create_jwt_token
from auth.email_handler import send_verification_email
from auth.email_verification import EmailVerification
from models.users import Page, User, UserSignIn, UserSignUp
from database.connection import get_session
from sqlmodel import select
from auth.hash_password import HashPassword
from uuid import uuid4
from datetime import datetime
from sqlalchemy.orm import Session
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)

# 이메일 인증 클래스 초기화
SECRET_KEY = "your_very_secure_secret_key"
email_verification = EmailVerification(secret_key=SECRET_KEY)

user_router = APIRouter()
hash_password = HashPassword()

# 공통 로직: 페이지 소유권 확인
def verify_page_ownership(page, current_user):
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    if page.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=403, detail="You do not have permission to perform this action."
        )

# 사용자 등록
@user_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def sign_new_user(data: UserSignUp, session=Depends(get_session)) -> dict:
    if not data.email or not data.password:
        raise HTTPException(status_code=400, detail="Email and password are required.")
    
    statement = select(User).where(User.email == data.email)
    user = session.exec(statement).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="A user with this email already exists."
        )

    new_user = User(
        email=data.email,
        password=hash_password.hash_password(data.password),
        username=data.username,
    )
    session.add(new_user)
    session.commit()
    logging.info(f"New user registered: {data.email}")
    return {"message": "User successfully registered."}

# 로그인 처리
@user_router.post("/signin")
def sign_in(data: UserSignIn, session=Depends(get_session)) -> dict:
    statement = select(User).where(User.email == data.email)
    user = session.exec(statement).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    if not hash_password.verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password.",
        )

    access_token = create_jwt_token(email=user.email, user_id=user.id)
    logging.info(f"User {user.email} signed in.")
    return {"message": "Login successful.", "access_token": access_token}

# 이메일 인증 요청
@user_router.post("/request-email-verification")
def request_email_verification(email: str, session: Session = Depends(get_session)):
    """
    이메일 인증 요청
    """
    logging.info(f"Email verification request received for email: {email}")

    user = session.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        token = email_verification.create_token(email)
        verification_url = f"http://localhost:8000/verify-email?token={token}"
        logging.info(f"Generated verification URL: {verification_url}")
        send_verification_email(email, verification_url)
    except Exception as e:
        logging.error(f"Error during email verification process: {e}")
        raise HTTPException(status_code=500, detail="Failed to send verification email")

    return {"message": "Verification email sent successfully."}

# 이메일 인증 처리
@user_router.get("/verify-email")
def verify_email(token: str = Query(...), session: Session = Depends(get_session)):
    """
    이메일 인증 처리
    """
    try:
        email = email_verification.verify_token(token)
        logging.info(f"Token verified successfully for email: {email}")

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
        logging.error(f"Token verification failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# 페이지 생성
@user_router.post("/pages", response_model=Page)
def create_page(
    page: Page,
    session=Depends(get_session),
    current_user: User = Depends(authenticate),
):
    new_page = Page(
        id=str(uuid4()),
        title=page.title,
        content=page.content,
        public=page.public,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        scheduled_at=page.scheduled_at or datetime.now(),
        owner_id=current_user.id,
    )
    session.add(new_page)
    session.commit()
    session.refresh(new_page)
    logging.info(f"Page created by {current_user.email}: {page.title}")
    return new_page

# 페이지 수정
@user_router.put("/pages/{page_id}", response_model=Page)
def update_page(
    page_id: str,
    updated_page: Page,
    session=Depends(get_session),
    current_user: User = Depends(authenticate),
):
    page = session.get(Page, page_id)
    verify_page_ownership(page, current_user)

    page.title = updated_page.title
    page.content = updated_page.content
    page.public = updated_page.public
    page.updated_at = datetime.now()

    if updated_page.scheduled_at:
        page.scheduled_at = updated_page.scheduled_at

    session.add(page)
    session.commit()
    session.refresh(page)
    logging.info(f"Page updated by {current_user.email}: {page.title}")
    return page

# 캘린더 뷰
@user_router.get("/pages/calendar-view", response_model=List[dict])
def get_calendar_view(
    start_date: datetime,
    end_date: datetime,
    session=Depends(get_session),
    current_user: User = Depends(authenticate),
):
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="Start date cannot be after end date.")

    statement = select(Page).where(Page.scheduled_at.between(start_date, end_date))
    pages = session.exec(statement).all()

    filtered_pages = [
        page for page in pages
        if page.public or page.owner_id == current_user.id
    ]

    calendar_data = {}
    for page in filtered_pages:
        date_key = page.scheduled_at.date()
        if date_key not in calendar_data:
            calendar_data[date_key] = []
        calendar_data[date_key].append({
            "id": page.id,
            "title": page.title,
            "content": page.content,
            "public": page.public,
            "owner_id": page.owner_id,
        })

    logging.info(f"Calendar view retrieved for {current_user.email}.")
    return [{"date": key, "pages": value} for key, value in sorted(calendar_data.items())]

# 페이지 삭제
@user_router.delete("/pages/{page_id}")
def delete_page(
    page_id: str,
    session=Depends(get_session),
    current_user: User = Depends(authenticate),
):
    page = session.get(Page, page_id)
    verify_page_ownership(page, current_user)

    session.delete(page)
    session.commit()
    logging.info(f"Page {page_id} deleted by {current_user.email}.")
    return {"message": f"Page {page_id} has been deleted."}

# 사용자 삭제
@user_router.delete("/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(authenticate),
    session: Session = Depends(get_session),
):
    user_to_delete = session.query(User).filter(User.id == user_id).first()
    if not user_to_delete:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="You cannot delete yourself")

    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can delete users")

    session.delete(user_to_delete)
    session.commit()
    logging.info(f"User {user_id} deleted by admin {current_user.email}.")
    return {"message": f"User {user_id} has been deleted."}



