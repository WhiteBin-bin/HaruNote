from fastapi import APIRouter, HTTPException, status, Body, Depends
from typing import List
from models.events import Event, EventUpdate
from database.connection import get_session
from sqlmodel import select
from auth.authenticate import authenticate

event_router = APIRouter()


@event_router.get("/", response_model=List[Event])
def retrive_all_events(session=Depends(get_session)) -> List[Event]:
    statement = select(Event)
    events = session.exec(statement)
    return events


@event_router.get("/{id}", response_model=Event)
def retrive_event(id: int, session=Depends(get_session)) -> Event:
    event = session.get(Event, id)
    if event:
        return event

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="일치하는 이벤트가 존재하지 않습니다.",
    )


@event_router.post("/", status_code=status.HTTP_201_CREATED)
def create_event(data: Event = Body(...), user_id=Depends(authenticate), session=Depends(get_session)) -> dict:
    data.user_id = user_id

    session.add(data)
    session.commit()
    session.refresh(data)
    return {"message": "이벤트가 정상적으로 등록되었습니다."}


@event_router.delete("/{id}")
def delete_event(id: int, session=Depends(get_session)) -> dict:
    event = session.get(Event, id)
    if event:
        session.delete(event)
        session.commit()
        return {"message": "이벤트가 정상적으로 삭제되었습니다."}

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="일치하는 이벤트가 존재하지 않습니다.",
    )


@event_router.delete("/")
def delete_all_events(session=Depends(get_session)) -> dict:
    statement = select(Event)
    events = session.exec(statement)

    for event in events:
        session.delete(event)

    session.commit()

    return {"message": "모든 이벤트가 정상적으로 삭제되었습니다."}


@event_router.put("/{id}", response_model=Event)
def update_event(id: int, data: EventUpdate, session=Depends(get_session)) -> Event:
    event = session.get(Event, id)
    if event:
        event_data = data.dict(exclude_unset=True)
        for key, value in event_data.items():
            setattr(event, key, value)

        session.add(event)
        session.commit()
        session.refresh(event)

        return event

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="일치하는 이벤트가 존재하지 않습니다.",
    )
