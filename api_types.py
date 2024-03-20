from typing import List
from enum import Enum

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

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


class SubscriptionPlan(Enum):
    FREE = "FREE"
    HOBBY = "HOBBY"
    PLUS = "PLUS"
    PRO = "PRO"


class Subscription(BaseModel):
    plan: SubscriptionPlan
    start_date: datetime
    end_date: datetime | None
    is_active: bool
    stripe_subscription_id: str | None


class HumanResponse(DBModelMixin):
    _id: PyObjectId
    email: EmailStr
    firebase_id: str
    stripe_customer_id: str | None
    subscription: Subscription
    tokens_left: int
    tokens_allowed: int
    sign_up_date: datetime
