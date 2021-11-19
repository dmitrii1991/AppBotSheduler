from typing import List

from fastapi import APIRouter, Depends, status, HTTPException
from tortoise.contrib.fastapi import HTTPNotFoundError

from dependencies import get_current_active_user
from app.pymodels import UserGlobal, EventCreate, EventInfo, Status, UserUpdate, UserMe
from app.models import EventTortModel, UserTortModel
from settings import MAX_FREE_EVENTS, MAX_PAY_EVENTS


router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(get_current_active_user)],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/me/",
    response_model=UserMe,
    status_code=status.HTTP_200_OK)
async def get_user_me(current_user=Depends(get_current_active_user)):
    return await UserMe.from_tortoise_orm(await UserTortModel.get(id=current_user.id))


@router.put(
    "/me/",
    response_model=UserGlobal,
    status_code=status.HTTP_200_OK)
async def update_user_me(user_data: UserUpdate, current_user=Depends(get_current_active_user)):
    return await UserGlobal.from_queryset_single(UserTortModel.get(id=await current_user.update_self(user_data)))


@router.post(
    "/event/",
    response_model=EventInfo,
    status_code=status.HTTP_201_CREATED)
async def create_event(data: EventCreate, current_user=Depends(get_current_active_user)):
    events_bd = await EventTortModel.all().filter(user=current_user)
    if not current_user.subscription:
        if len(events_bd) >= MAX_FREE_EVENTS:
            raise HTTPException(status_code=400, detail=f"The limit for free events has been reached {MAX_FREE_EVENTS}")
    else:
        if len(events_bd) >= MAX_PAY_EVENTS:
            raise HTTPException(status_code=400, detail=f"The limit for pay events has been reached {MAX_PAY_EVENTS}")
    try:
        event = await EventTortModel.create(
            name=data.name, type_event=data.type_event, date=data.date, days_reminder=data.days_reminder, user=current_user)
    except Exception as error:
        raise HTTPException(status_code=400, detail=f"{error}")
    return event


@router.get(
    "/event/",
    response_model=List[EventInfo],
    status_code=status.HTTP_200_OK)
async def get_all_events(current_user=Depends(get_current_active_user)):
    return await EventInfo.from_queryset(EventTortModel.all().filter(user=current_user))


@router.put(
    "/event/{event_id}",
    response_model=EventInfo,
    responses={404: {"model": HTTPNotFoundError}},
    status_code=status.HTTP_200_OK)
async def update_event(event_id: int, event_data: EventCreate, current_user=Depends(get_current_active_user)):
    event = await EventTortModel.get(id=event_id, user=current_user)
    try:
        await event.update_self(event_id, data=event_data)
    except Exception as error:
        raise HTTPException(status_code=400, detail=f"{error}")

    return await EventInfo.from_queryset_single(EventTortModel.get(id=event_id))


@router.delete(
    "/event/{event_id}",
    response_model=Status,
    status_code=status.HTTP_200_OK,
    responses={404: {"model": HTTPNotFoundError}},)
async def delete_event(event_id: int, current_user=Depends(get_current_active_user)):
    deleted = await EventTortModel.filter(id=event_id, user=current_user).delete()
    if not deleted:
        raise HTTPException(status_code=404, detail=f"EventTortModel {event_id} not found")
    return Status(message=f"Deleted event {event_id}")


@router.delete(
    "/event/",
    response_model=Status,
    status_code=status.HTTP_200_OK,
    responses={404: {"model": HTTPNotFoundError}},)
async def delete_all_events(current_user=Depends(get_current_active_user)):
    deleted = await EventTortModel.filter(user=current_user).delete()
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Events not found")
    return Status(message=f"Deleted all events")
