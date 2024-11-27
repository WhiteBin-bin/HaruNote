from pydantic import BaseModel, EmailStr
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import Column, JSON
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
# 순환 참조 방지 
if TYPE_CHECKING:
    from models.events import Event



class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)  # 기본 키
    email: EmailStr  # 이메일 (고유)
    password: str  # 암호
    username: str  # 사용자 이름
    pages: List["Page"] = Relationship(back_populates="owner")  # 사용자와 연결된 페이지들


class UserSignUp(SQLModel):
    email: EmailStr
    password: str
    username: str


class UserSignIn(SQLModel):
    email: EmailStr
    password: str


class Page(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True)  # Page의 기본 키
    title: str  # 제목
    content: str  # 내용
    public: bool = Field(default=True)  # 공개 여부 (기본값: True)
    created_at: datetime = Field(default_factory=datetime.now)  # 생성 시간
    updated_at: Optional[datetime] = None  # 수정 시간
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")  # 페이지 소유자의 ID
    owner: Optional[User] = Relationship( back_populates="pages") # 페이지 소유자와의 관계