from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends, Query
from auth.authenticate import authenticate
from auth.jwt_handler import create_jwt_token
from models.users import Page, User, UserSignIn, UserSignUp
from database.connection import get_session
from sqlmodel import select
from auth.hash_password import HashPassword
from uuid import uuid4
from datetime import datetime
from sqlalchemy.orm import Session


user_router = APIRouter()
hash_password = HashPassword()


#1.사용자 등록
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


#2.로그인 처리
#2. 수동으로 관리자 설정 ex)SELECT id FROM user WHERE email = 'user@example.com';
#UPDATE user
#SET is_admin = true
#WHERE id = 1;
@user_router.post("/Signin")
def sign_in(data: UserSignIn, session=Depends(get_session)) -> dict:
    statement = select(User).where(User.email == data.email)
    user = session.exec(statement).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="일치하는 사용자가 존재하지 않습니다.",
        )

    # if user.password != data.password:
    if hash_password.verify_password(data.password, user.password) == False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="패스워드가 일치하지 않습니다.",
        )

    access_token = create_jwt_token(email=user.email, user_id=user.id)
    return {"message": "로그인에 성공했습니다.", "access_token": access_token}

#3.페이지 생성
@user_router.post("/pages", response_model=Page)
def create_page(
    page: Page,
    session=Depends(get_session),
    current_user: User = Depends(authenticate)  # 인증된 사용자만 생성 가능
):
    # 현재 시간을 가져온 뒤 replace()로 수정
    new_page = Page(
        id=str(uuid4()),
        title=page.title,
        content=page.content,
        public=page.public,  # 공개 여부 설정
        created_at=datetime.now(),
        updated_at=page.updated_at,
        owner_id=current_user.id  # 인증된 사용자의 ID를 owner_id로 설정
    )
    session.add(new_page)
    session.commit()
    session.refresh(new_page)
    return new_page

#4.모든 페이지 조회
@user_router.get("/pages", response_model=List[Page])
def get_pages(session=Depends(get_session)):
    pages = session.query(Page).all()  # 모든 페이지 조회
    return pages

#5.특정 페이지 조회
@user_router.get("/pages/", response_model=List[Page])
def get_pages_by_title(
    title: str = Query(..., description="조회할 페이지의 제목"),
    session: Session = Depends(get_session),
    current_user: User = Depends(authenticate)  # 인증된 사용자
):
    # 데이터베이스에서 제목으로 페이지 조회
    pages = session.query(Page).filter(Page.title == title).all()

    if not pages:
        raise HTTPException(status_code=404, detail="No pages found with the given title")

    # 비공개 페이지 접근 권한 확인
    filtered_pages = []
    for page in pages:
        if not page.public and page.owner_id != current_user.id:
            continue  # 비공개 페이지는 소유자가 아닌 경우 접근 불가
        filtered_pages.append(page)

    if not filtered_pages:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to access the requested pages"
        )

    return filtered_pages


#6.날짜별로 그룹화
@user_router.get("/pages/calendar-view", response_model=List[dict])
def get_calendar_view(
        start_date: datetime,
        end_date: datetime,
        session=Depends(get_session),
        current_user: User = Depends(authenticate)  # 인증된 사용자만
):
    # 지정된 기간 내의 페이지 가져오기
    pages = (
        session.query(Page)
        .filter(Page.updated_at.between(start_date, end_date))  # 날짜 범위 필터링
        .all()
    )

    # 비공개 페이지는 소유자만 접근 가능하도록 필터링
    filtered_pages = []
    for page in pages:
        if not page.public and page.owner_id != current_user.id:
            continue  # 비공개 페이지는 소유자가 아니면 건너뜀
        filtered_pages.append(page)

    # 날짜별로 페이지 그룹화
    calendar_data = {}
    for page in filtered_pages:
        date_key = page.updated_at.date()  # 날짜만 추출
        if date_key not in calendar_data:
            calendar_data[date_key] = []
        calendar_data[date_key].append({
            "id": page.id,
            "title": page.title,
            "content": page.content,
            "public": page.public,
            "owner_id" : page.owner_id
        })

    # 날짜별로 정렬 (오름차순)
    sorted_calendar_data = sorted(calendar_data.items(), key=lambda x: x[0])

    # 정렬된 데이터를 반환
    return [{"date": key, "pages": value} for key, value in sorted_calendar_data]



#7.페이지 수정
@user_router.put("/pages/{page_id}", response_model=Page)
def update_page(page_id: str, updated_page: Page, session=Depends(get_session), current_user: User = Depends(authenticate)):
    page = session.query(Page).filter(Page.id == page_id).first()
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")

    # 페이지 소유자만 수정 가능
    if page.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only update your own pages.")

    # owner_id는 변경되지 않도록 방지
    if updated_page.owner_id != page.owner_id:
        raise HTTPException(status_code=400, detail="You cannot change the owner of the page.")

    page.title = updated_page.title
    page.content = updated_page.content
    page.public = updated_page.public
    page.updated_at = datetime.now()  # 수정 시 updated_at을 업데이트

    session.commit()
    session.refresh(page)
    return page



#8.페이지 삭제
@user_router.delete("/pages/{page_id}")
def delete_page(page_id: str, session=Depends(get_session), current_user: User = Depends(authenticate)):
    page = session.query(Page).filter(Page.id == page_id).first()
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")

    # 페이지 소유자만 삭제 가능
    if page.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own pages.")

    session.delete(page)
    session.commit()
    return {"message" : "Page has been deleted."}



#9.페이지 리스트(제목으로만)로 정렬
@user_router.get("/pages/titles", response_model=List[str])
def get_sorted_page_titles(
    order_by: str = Query("asc", enum=["asc", "desc"], description="정렬 순서: asc(오름차순) 또는 desc(내림차순)"),
    session: Session = Depends(get_session)):
    statement = select(Page.title)
    result = session.exec(statement).all()

    # 정렬
    if order_by == "asc":
        sorted_titles = sorted(result)
    else:
        sorted_titles = sorted(result, reverse=True)

    return sorted_titles

#10. 관리자 사용자 삭제
@user_router.delete("/users/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(
    user_id: int,
    current_user: User = Depends(authenticate),  # 현재 인증된 사용자
    session=Depends(get_session),
):
    # 관리자 권한 확인
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다."
        )
    
    # 삭제할 사용자 조회
    user_to_delete = session.query(User).filter(User.id == user_id).first()
    if not user_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="삭제하려는 사용자가 존재하지 않습니다."
        )

    # 관리자 자신은 삭제할 수 없도록 방지
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="관리자는 자신을 삭제할 수 없습니다."
        )
    
    session.delete(user_to_delete)
    session.commit()
    return {"message": f"사용자 {user_id}가 성공적으로 삭제되었습니다."}

#관리자 또는 페이지 소유자 페이지 삭제
@user_router.delete("/pages/{page_id}")
def delete_page(
    page_id: str,
    session=Depends(get_session),
    current_user: User = Depends(authenticate)  # 인증된 사용자
):
    # 삭제할 페이지 조회
    page = session.query(Page).filter(Page.id == page_id).first()
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")

    # 페이지 소유자가 아니고 관리자가 아닐 경우 접근 불가
    if page.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=403, detail="You do not have permission to delete this page."
        )

    # 페이지 삭제
    session.delete(page)
    session.commit()
    return {"message": f"Page {page_id} has been deleted."}