from fastapi import APIRouter, Depends

from dependencies import get_current_active_user

router = APIRouter(
    prefix="/bot",
    tags=["bot"],
    dependencies=[Depends(get_current_active_user)],
    responses={404: {"description": "Not found"}},
)

