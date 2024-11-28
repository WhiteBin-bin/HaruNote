from pydantic import BaseModel, EmailStr
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

# 순환 참조 방지
if TYPE_CHECKING:
    from models.events import Event

class User(SQLModel, table=True):
    #사용자 테이블 모델
    id: int = Field(default=None, primary_key=True)  # 기본 키
    email: EmailStr  # 이메일 (고유)
    password: str  # 암호
    username: str  # 사용자 이름
    is_admin: bool = Field(default=False)  # 관리자 여부
    pages: List["Page"] = Relationship(back_populates="owner")  # 사용자와 연결된 페이지들

class UserSignUp(SQLModel):
    #사용자 회원가입 요청 모델
    email: EmailStr
    password: str
    username: str

class UserSignIn(SQLModel):
    #사용자 로그인 요청 모델
    email: EmailStr
    password: str

class Page(SQLModel, table=True):
    #페이지 테이블 모델
    id: str = Field(default=None, primary_key=True)  # 페이지 기본 키
    title: str  # 제목
    content: str  # 내용
    public: bool = Field(default=True)  # 공개 여부
    created_at: datetime = Field(default_factory=datetime.now)  # 생성 시간
    updated_at: datetime = Field(default_factory=datetime.now)  # 수정 시간
    scheduled_at: Optional[datetime] = None  # 일정 날짜
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")  # 페이지 소유자의 ID
    owner: Optional[User] = Relationship(back_populates="pages")  # 페이지 소유자와의 관계
