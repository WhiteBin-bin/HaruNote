# from pydantic import BaseModel
# from typing import List, Optional, TYPE_CHECKING
# from sqlmodel import SQLModel, Field, Column, JSON, Relationship
# if TYPE_CHECKING:
#     from models.users import User
#
# class Event(SQLModel, table=True):
#     id: int = Field(default=None, primary_key=True)
#     title: str
#     image: str
#     description: str
#     tags: List[str] = Field(sa_column=Column(JSON))
#     location: str
#     user_id: Optional[int] = Field(default=None, foreign_key="user.id")
#     user: Optional["User"] = Relationship(back_populates="events")
#
#
# # 이벤트 수정 시 전달되는 데이터 모델을 정의
# class EventUpdate(SQLModel):
#     title: Optional[str] = None
#     image: Optional[str] = None
#     description: Optional[str] = None
#     tags: Optional[List[str]] = None
#     location: Optional[str] = None
