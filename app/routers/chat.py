from typing import Annotated
from fastapi import APIRouter
from fastapi.params import Depends
from openai import BaseModel

from app import config
from app.internal.openai.client import OpenAIClient

router = APIRouter(prefix="/chat")

class ChatRequest(BaseModel):
    prompt: str

# TODO: should use dependency injection for openai client
@router.post("/", tags=["chat"])
async def chat(request: ChatRequest, settings: Annotated[config.Settings, Depends(config.get_settings)]):
    openai_client = OpenAIClient(api_key=settings.openai_api_key)
    return openai_client.get_completion(request.prompt)


