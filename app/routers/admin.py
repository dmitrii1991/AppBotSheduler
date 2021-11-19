from typing import List, Optional

from fastapi import APIRouter, Depends, status, HTTPException
from tortoise.contrib.fastapi import HTTPNotFoundError

from dependencies import get_admin_user
from app.models import UserTortModel
from app.pymodels import Status, UserGlobal, UserMinimum


router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_admin_user)],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/users",
    response_model=List[UserGlobal],
    status_code=status.HTTP_200_OK)
async def get_users(limit: Optional[int] = 100):
    return await UserGlobal.from_queryset(UserTortModel.all().limit(limit))


@router.get(
    "/users/{user_id}",
    response_model=UserGlobal,
    responses={404: {"model": HTTPNotFoundError}},
    status_code=status.HTTP_200_OK)
async def get_user(user_id):
    user = UserTortModel.get(id=user_id)
    return await UserGlobal.from_queryset_single(user)


@router.get(
    "/teleg_user/{teleg_id}",
    response_model=UserMinimum,
    responses={404: {"model": HTTPNotFoundError}},
    status_code=status.HTTP_200_OK)
async def get_teleg_user(teleg_id):
    user = UserTortModel.get(teleg_id=teleg_id)
    return await UserMinimum.from_queryset_single(user)


@router.post(
    "/users",
    response_model=UserGlobal,
    status_code=status.HTTP_201_CREATED)
async def create_user(user: UserGlobal):
    user_obj = await UserTortModel.create(**user.dict(exclude_unset=True))
    return await UserGlobal.from_tortoise_orm(user_obj)


@router.put(
    "/users/{user_id}",
    response_model=UserGlobal,
    responses={404: {"model": HTTPNotFoundError}},
    status_code=status.HTTP_201_CREATED)
async def update_user(user_id: int, user: UserGlobal):
    await UserTortModel.filter(id=user_id).update(**user.dict(exclude_unset=True))
    return await UserGlobal.from_queryset_single(UserTortModel.get(id=user_id))


@router.delete(
    "/users/{user_id}",
    response_model=Status,
    responses={404: {"model": HTTPNotFoundError}},
    status_code=status.HTTP_200_OK)
async def delete_user(user_id: int):
    deleted_count = await UserTortModel.filter(id=user_id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f"UserTortModel {user_id} not found")
    return Status(message=f"Deleted UserTortModel {user_id}")
