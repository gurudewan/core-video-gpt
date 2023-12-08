from typing import List
from pydantic import BaseModel
from database.objectid import DBModelMixin, PyObjectId


class Model(BaseModel):
    id: str
    name: str
    maxLength: int
    tokenLimit: int


class Message(BaseModel):
    role: str
    content: str


class RootChatInput(BaseModel):
    chatID: str
    messages: List[Message]
    videoID: str

    # user: str
    # model: Model
    # key: str
    # prompt: str
    # temperature: float


class VideoInput(BaseModel):
    video_url: str

    # should actually take an ID
    # and a type which is "youtube" or etc.?


class ChatResponse(DBModelMixin):
    # Define your fields here
    _id: PyObjectId
    human_id: PyObjectId

    # TODO DO THIS SCHEMA PROPERLY
    class Config:
        extra = "allow"
