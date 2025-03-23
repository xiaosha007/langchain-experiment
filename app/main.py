from typing import Annotated
from fastapi import Depends, FastAPI

from app import config



app = FastAPI()

@app.get("/")
async def root(settings: Annotated[config.Settings, Depends(config.get_settings)]):
    settings = config.get_settings()
    return {"message": "Hello World", "env": settings.env}
