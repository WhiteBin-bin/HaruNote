from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends, Query
from auth.authenticate import authenticate
from auth.jwt_handler import create_jwt_token
from auth.email_verification import create_email_verification_token, verify_email_verification_token
from auth.email_handler import send_verification_email
from models.users import Page, User, UserSignIn, UserSignUp
from database.connection import get_session
from sqlmodel import select
from auth.hash_password import HashPassword
from uuid import uuid4
from datetime import datetime
from sqlalchemy.orm import Session

user_router = APIRouter()
hash_password = HashPassword()

# 1. 사용자 등록
@user_router.post("/Signup", status_code=status.HTTP_201_CREATED)
async def sign_new_user(data: UserSignUp, session=Depends(get_session)) -> dict:
    statement = select(User).where(User.email == data.email)
    user = session.exec(statement).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="동일한 사용자가 존재합니다."
        )

    new_user = User(
        email=data.email,
        password=hash_password.hash_password(data.password),
        username=data.username
    )
    session.add(new_user)
    session.commit()

    return {"message": "정상적으로 등록되었습니다."}


# 2. 로그인 처리
@user_router.post("/Signin")
def sign_in(data: UserSignIn, session=Depends(get_session)) -> dict:
    statement = select(User).where(User.email == data.email)
    user = session.exec(statement).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="일치하는 사용자가 존재하지 않습니다.",
        )

    if not hash_password.verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="패스워드가 일치하지 않습니다.",
        )

    access_token = create_jwt_token(email=user.email, user_id=user.id)
    return {"message": "로그인에 성공했습니다.", "access_token": access_token}


# 3. 이메일 검증 요청 엔드포인트
@user_router.post("/request-email-verification")
def request_email_verification(email: str, session: Session = Depends(get_session)):
    #이메일 검증 요청
    user = session.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    token = create_email_verification_token(email)  # 검증 토큰 생성
    send_verification_email(email, token)  # 검증 이메일 전송

    return {"message": "Verification email sent"}


# 4. 이메일 검증 엔드포인트
@user_router.get("/verify-email")
def verify_email(token: str = Query(...)):
    #이메일 검증
    try:
        email = verify_email_verification_token(token)  # 검증 토큰 확인
        return {"message": f"Email {email} successfully verified"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# 5. 페이지 생성
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
        scheduled_at=page.scheduled_at or datetime.now(),  # 디폴트로 현재 시간 사용
        owner_id=current_user.id,
    )
    session.add(new_page)
    session.commit()
    session.refresh(new_page)
    return new_page


# 6. 페이지 수정
@user_router.put("/pages/{page_id}", response_model=Page)
def update_page(
    page_id: str,
    updated_page: Page,
    session=Depends(get_session),
    current_user: User = Depends(authenticate),
):
    page = session.get(Page, page_id)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")

    if page.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only update your own pages.")

    page.title = updated_page.title
    page.content = updated_page.content
    page.public = updated_page.public
    page.updated_at = datetime.now()

    if updated_page.scheduled_at:
        page.scheduled_at = updated_page.scheduled_at

    session.add(page)
    session.commit()
    session.refresh(page)
    return page


# 7. 캘린더 뷰
@user_router.get("/pages/calendar-view", response_model=List[dict])
def get_calendar_view(
    start_date: datetime,
    end_date: datetime,
    session=Depends(get_session),
    current_user: User = Depends(authenticate),
):
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

    return [{"date": key, "pages": value} for key, value in sorted(calendar_data.items())]


# 8. 페이지 삭제
@user_router.delete("/pages/{page_id}")
def delete_page(
    page_id: str,
    session=Depends(get_session),
    current_user: User = Depends(authenticate),
):
    page = session.get(Page, page_id)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")

    if page.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own pages.")

    session.delete(page)
    session.commit()
    return {"message": "Page has been deleted."}
