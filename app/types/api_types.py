from typing import List
from enum import Enum

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

from app.database.objectid import DBModelMixin, PyObjectId


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


class MonthlyUsage(BaseModel):
    num_videos_processed: int
    duration_videos_processed_hours: float


class SubscriptionPlan(Enum):
    FREE = "FREE"
    BASIC = "BASIC"
    PLUS = "PLUS"
    PRO = "PRO"


class SubscriptionStatus(Enum):
    ACTIVE = "ACTIVE"
    DELETED = "DELETED"
    PAUSED = "PAUSED"
    CANCELED = "CANCELED"


class StripeSubscriptionStatus(Enum):
    ACTIVE = "ACTIVE"
    DELETED = "DELETED"
    PAUSED = "PAUSED"
    CANCELED = "CANCELED"

    TRIALING = "TRIALING"
    INCOMPLETE = "INCOMPLETE"
    INCOMPLETE_EXPIRED = "INCOMPLETE_EXPIRED"
    PAST_DUE = "PAST_DUE"
    UNPAID = "UNPAID"


class SubscriptionCycle(Enum):
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"


class Subscription(BaseModel):
    plan: SubscriptionPlan
    status: SubscriptionStatus
    start_date: datetime | None = None
    end_date: datetime | None = None
    cycle: SubscriptionCycle | None = None
    stripe_subscription_id: str | None = None
    stripe_subscription_status: StripeSubscriptionStatus | None = None


class HumanResponse(DBModelMixin):
    _id: PyObjectId
    email: EmailStr
    firebase_id: str
    stripe_customer_id: str | None
    subscription: Subscription | None
    sign_up_date: datetime
