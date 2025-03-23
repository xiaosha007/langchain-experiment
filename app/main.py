from typing import Annotated
from fastapi import Depends, FastAPI

from app import config
from app.routers import chat, ctos


app = FastAPI()

app.include_router(chat.router)
app.include_router(ctos.router)

@app.get("/")
async def root(settings: Annotated[config.Settings, Depends(config.get_settings)]):
    settings = config.get_settings()
    return {"message": "Hello World", "env": settings.env}
