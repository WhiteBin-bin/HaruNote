from typing import List,  Optional
from fastapi import APIRouter, HTTPException, status, Depends, Query, File, UploadFile, Form, Response
from auth.authenticate import authenticate
from auth.jwt_handler import create_tokens, refresh_access_token
from models.users import Page, User, UserSignIn, UserSignUp, FileModel
from models.utils import generate_verification_code, send_email_verification
from database.connection import get_session
from sqlmodel import select
from auth.hash_password import HashPassword
from uuid import uuid4
from datetime import datetime, timedelta
from sqlalchemy.orm import Session, joinedload
import os
import re



user_router = APIRouter()
hash_password = HashPassword()
UPLOAD_DIR = "uploads/"
verification_codes = {} # 이메일과 코드 저장
signup_data = {}


#1.사용자 등록-이메일 보내기
@user_router.post("/signup/request-code", status_code=status.HTTP_200_OK)
async def request_signup_code(data: UserSignUp, session=Depends(get_session)) -> dict:
    # 중복 이메일 확인
    statement = select(User).where(User.email == data.email)
    existing_user = session.exec(statement).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="이미 사용 중인 이메일입니다."
        )

    # 인증 코드 생성
    code = generate_verification_code()
    verification_codes[data.email] = code  # 이메일과 인증 코드 매핑
    signup_data[data.email] = data.dict()  # 회원가입 데이터를 임시 저장

    # 이메일 전송
    send_email_verification(data.email, code)

    return {"message": "인증 코드가 이메일로 전송되었습니다."}

#2.사용자 등록-숫자 랜덤으로 날라온거 입력
@user_router.post("/signup/verify-code", status_code=status.HTTP_201_CREATED)
async def verify_signup_code(code: str, session=Depends(get_session)):
    # 인증 코드 확인
    email = next((key for key, value in verification_codes.items() if value == code), None)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="잘못된 인증 코드입니다."
        )

    # 회원가입 데이터 확인
    if email not in signup_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="회원가입 데이터가 없습니다."
        )

    # 데이터베이스에 사용자 저장
    user_data = signup_data[email]
    new_user = User(
        email=email,
        password=hash_password.hash_password(user_data["password"]),
        username=user_data["username"]
    )
    session.add(new_user)
    session.commit()

    # 인증 완료 후 데이터 삭제
    del verification_codes[email]
    del signup_data[email]

    return {"message": "회원가입이 완료되었습니다."}

#3.로그인 처리
@user_router.post("/signin")
def sign_in(data: UserSignIn, session=Depends(get_session)) -> dict:
    # 이메일 형식 검증
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="올바르지 않은 이메일 형식입니다."
        )

    # 사용자 검색
    statement = select(User).where(User.email == data.email)
    user = session.exec(statement).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="일치하는 사용자가 존재하지 않습니다.",
        )

    # 패스워드 검증
    if not hash_password.verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="패스워드가 일치하지 않습니다.",
        )

    # Access Token과 Refresh Token 생성
    tokens = create_tokens(email=user.email, user_id=user.id)

    # 로그인 성공 응답
    return {
        "message": "로그인에 성공했습니다.",
        "user_id": user.id,
        "email": user.email,
        "is_admin": user.is_admin,
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"]
    }

#3-1.토큰 갱신
@user_router.post("/refresh-token")
async def refresh_token(
        refresh_token: str = Form(...),
        session: Session = Depends(get_session)
) -> dict:
    try:
        # Refresh 토큰으로 새 Access 토큰 발급
        new_access_token = refresh_access_token(refresh_token)

        return {
            "message": "토큰이 갱신되었습니다.",
            "access_token": new_access_token
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰 갱신에 실패했습니다."
        )

#4.페이지 생성
@user_router.post("/pages")
async def create_page_with_file(
    title: str = Form(...),
    content: str = Form(...),
    public: bool = Form(...),
    scheduled_at: datetime = Form(None),
    files: Optional[List[UploadFile]] = File(None),
    session: Session = Depends(get_session),
    current_user: User = Depends(authenticate)
):
    # 새 페이지 생성
    new_page = Page(
        id=str(uuid4()),
        title=title,
        content=content,
        public=public,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        scheduled_at=scheduled_at or datetime.now(),
        owner_id=current_user.id,
    )
    session.add(new_page)
    session.commit()
    session.refresh(new_page)

    # 파일이 있으면 업로드 처리
    file_data_list = []
    if files:
        for file in files:
            try:
                # 파일 저장
                file_path = os.path.join(UPLOAD_DIR, file.filename)
                with open(file_path, "wb") as f:
                    f.write(await file.read())

                file_data = FileModel(
                    fileurl=file_path,
                    filename=file.filename,
                    content_type=file.content_type,
                    size=os.path.getsize(file_path),
                    created_at=datetime.now(),
                    page_id=new_page.id
                )

                session.add(file_data)
                session.commit()
                session.refresh(file_data)

                file_data_list.append(file_data)
            except Exception as e:
                session.rollback()
                raise HTTPException(status_code=500, detail=f"파일 업로드 중 오류 발생: {str(e)}")

    # 새 페이지와 업로드된 파일들을 함께 반환
    return {
        "id": new_page.id,
        "title": new_page.title,
        "content": new_page.content,
        "public": new_page.public,
        "created_at": new_page.created_at,
        "updated_at": new_page.updated_at,
        "scheduled_at": new_page.scheduled_at,
        "owner_id": new_page.owner_id,
        "uploaded_files": [
            {"filename": file.filename, "content_type": file.content_type, "size": file.size, "fileurl": file.fileurl}
            for file in file_data_list
        ]
    }

#5.공개된 페이지 조회 (public이 True인 경우만)
@user_router.get("/pages", response_model=List[Page])
def get_public_pages(session=Depends(get_session)):
    # 공개된 페이지만 조회
    public_pages = session.query(Page).filter(Page.public == True).all()
    return public_pages


#6.특정 페이지 조회
@user_router.get("/pages/")
async def get_pages_by_title(
        title: str = Query(..., description="조회할 페이지의 제목"),
        session: Session = Depends(get_session),
        current_user: User = Depends(authenticate),
):
    try:
        # 쿼리 수정
        pages = (
            session.query(Page)
            .options(joinedload(Page.files))
            .filter(Page.title == title)
            .all()
        )

        print(
            f"SQL Query executed: {str(session.query(Page).options(joinedload(Page.files)).filter(Page.title == title))}")
        print(f"Found pages: {pages}")

        if not pages:
            raise HTTPException(status_code=404, detail="페이지를 찾을 수 없습니다")

        # 비공개 페이지 접근 권한 확인
        filtered_pages = [page for page in pages if page.public or page.owner_id == current_user.id]

        if not filtered_pages:
            raise HTTPException(
                status_code=403,
                detail="페이지에 접근할 권한이 없습니다"
            )

        response_data = []
        for page in filtered_pages:
            page_data = {
                "id": page.id,
                "title": page.title,
                "content": page.content,
                "public": page.public,
                "created_at": page.created_at,
                "updated_at": page.updated_at,
                "scheduled_at": page.scheduled_at,
                "owner_id": page.owner_id,
                "file_names": [file.filename for file in (page.files or [])],
                "fileurl": [file.fileurl for file in (page.files or [])]  # file_url을 fileurl로 수정
            }
            response_data.append(page_data)

        return response_data

    except Exception as e:
        print(f"Error occurred: {str(e)}")  # 디버깅을 위한 에러 로그
        raise HTTPException(status_code=500, detail=f"서버 오류가 발생했습니다: {str(e)}")

#7.날짜별로 그룹화
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
        .filter(Page.scheduled_at.between(start_date, end_date))  # 날짜 범위 필터링
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
        date_key = page.scheduled_at.date()  # 날짜만 추출
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


#8.페이지 수정
@user_router.put("/pages/{page_id}")
async def update_page(
    page_id: str,
    title: str = Form(...),
    content: str = Form(...),
    public: bool = Form(...),
    files: Optional[List[UploadFile]] = File(None),
    delete_files: bool = Form(False),  # 파일 삭제 여부
    session: Session = Depends(get_session),
    current_user: User = Depends(authenticate)
):
    try:
        # 페이지 존재 여부 확인
        page = session.query(Page).filter(Page.id == page_id).first()
        if not page:
            raise HTTPException(status_code=404, detail="페이지를 찾을 수 없습니다.")

        # 페이지 소유자만 수정 가능
        if page.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="자신의 페이지만 수정할 수 있습니다.")

        # 페이지 정보 업데이트
        page.title = title
        page.content = content
        page.public = public
        page.updated_at = datetime.now()

        file_data_list = []

        # 파일 삭제 요청이 있는 경우
        if delete_files:
            for existing_file in page.files:
                if os.path.exists(existing_file.fileurl):
                    os.remove(existing_file.fileurl)
                session.delete(existing_file)
            session.commit()

        # 새 파일 업로드 요청이 있는 경우
        elif files:
            # 기존 파일 삭제
            for existing_file in page.files:
                if os.path.exists(existing_file.fileurl):
                    os.remove(existing_file.fileurl)
                session.delete(existing_file)
            session.commit()

            # 새 파일 업로드
            for file in files:
                try:
                    # 파일 저장
                    file_path = os.path.join(UPLOAD_DIR, file.filename)
                    with open(file_path, "wb") as f:
                        f.write(await file.read())

                    file_data = FileModel(
                        fileurl=file_path,
                        filename=file.filename,
                        content_type=file.content_type,
                        size=os.path.getsize(file_path),
                        created_at=datetime.now(),
                        page_id=page.id
                    )

                    session.add(file_data)
                    session.commit()
                    session.refresh(file_data)

                    file_data_list.append(file_data)
                except Exception as e:
                    session.rollback()
                    raise HTTPException(status_code=500, detail=f"파일 업로드 중 오류 발생: {str(e)}")
        else:
            # 파일 변경이 없는 경우 기존 파일 정보 유지
            file_data_list = page.files

        session.commit()
        session.refresh(page)

        # 업데이트된 페이지와 파일 정보 반환
        return {
            "message": "페이지가 성공적으로 수정되었습니다.",
            "page": {
                "id": page.id,
                "title": page.title,
                "content": page.content,
                "public": page.public,
                "created_at": page.created_at,
                "updated_at": page.updated_at,
                "scheduled_at": page.scheduled_at,
                "owner_id": page.owner_id,
            },
            "files": [
                {
                    "filename": file.filename,
                    "content_type": file.content_type,
                    "size": file.size,
                    "fileurl": file.fileurl
                }
                for file in file_data_list
            ] if file_data_list else []
        }

    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"페이지 수정 중 오류가 발생했습니다: {str(e)}"
        )

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


#10.관리자가 사용자 삭제
@user_router.delete("/users/email/{email}", status_code=status.HTTP_200_OK)
def delete_user_by_email(
        email: str,
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
    user_to_delete = session.query(User).filter(User.email == email).first()
    if not user_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="삭제하려는 사용자가 존재하지 않습니다."
        )

    # 관리자 자신은 삭제할 수 없도록 방지
    if current_user.email == email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="관리자는 자신을 삭제할 수 없습니다."
        )

    session.delete(user_to_delete)
    session.commit()
    return {"message": f"{email} 유저가 성공적으로 삭제되었습니다."}


#11.관리자 또는 페이지 소유자 페이지 삭제
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
    return {"message": "Page  has been deleted."}

#12.owner_Id가 만든 페이지 출력
@user_router.get("/pages/by-owner/{owner_id}", response_model=List[Page])
def get_pages_by_owner(
    owner_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(authenticate)  # 인증된 사용자
):
    # owner_id에 해당하는 페이지를 조회
    pages = session.query(Page).filter(Page.owner_id == owner_id).all()

    # 페이지가 없을 경우 에러 반환
    if not pages:
        raise HTTPException(status_code=404, detail="해당 소유자가 만든 페이지가 없습니다.")

    # 비공개 페이지 접근 권한 확인
    if any(not page.public and page.owner_id != current_user.id for page in pages):
        raise HTTPException(
            status_code=403,
            detail="비공개 페이지는 소유자만 접근 가능합니다."
        )

    return pages

#13.User정보 username과 email로 list 정렬
@user_router.get("/users/details", response_model=List[dict])
def get_sorted_user_details(
    session: Session = Depends(get_session)
):
    # User 테이블에서 username, email 가져오기 (is_admin이 False인 사용자만)
    user_details = session.query(User.username, User.email).filter(User.is_admin == False).all()

    # 리스트로 변환
    user_details_list = [{"username": detail[0], "email": detail[1]} for detail in user_details]

    # 무조건 오름차순으로 정렬
    sorted_user_details = sorted(user_details_list, key=lambda x: x["username"])

    return sorted_user_details




