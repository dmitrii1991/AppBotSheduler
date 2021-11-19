import datetime

import uvicorn
from fastapi import FastAPI, HTTPException, Depends

from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from tortoise.contrib.fastapi import register_tortoise

from settings import POSTGRESQL_URL
from routers import users, admin, bot
from app.utils import Secret, JWT
from app.models import UserTortModel


tags_metadata = [
    {
        "name": "users",
        "description": "Operations with users.",
    },
    {
        "name": "admin",
        "description": "admin functioanal",
    },
    {
        "name": "default",
        "description": "General functionality",
    }
]

app = FastAPI(
    title="BotRuller",
    description="Управление",
    version="0.1.0",
    contact={
        "name": "BotRuller",
        "email": "kulinich.dima@yandex.ru",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    openapi_tags=tags_metadata,
    openapi_url="/openapi.json"
)

app.include_router(users.router)
app.include_router(admin.router)
app.include_router(bot.router)

register_tortoise(
    app,
    db_url=POSTGRESQL_URL,
    modules={"models": ["app.models"]},
    generate_schemas=False,
    add_exception_handlers=True,

)


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await UserTortModel.get_or_none(username=form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    if user.deactivate:
        return JSONResponse(
            status_code=403,
            content={"message": "the user is deactivated"},
        )
    if not Secret.checkpw(form_data.password.encode(), user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = JWT.create_access_token({"sub": user.username})
    await user.update_from_dict({
        'token_hash': access_token,
        'token_created_at': datetime.datetime.now()
    })
    await user.save()
    return {"access_token": access_token, "token_type": "bearer"}


@app.on_event("startup")
async def startup_event():
    ...

@app.on_event("shutdown")
def shutdown_event():
    ...


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
