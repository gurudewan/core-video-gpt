from fastapi import APIRouter


stripe_app = APIRouter(prefix="/stripe", tags=["stripe"])

from apis.stripe_apps.stripe_sessions import stripe_sessions_app
from apis.stripe_apps.stripe_webhooks import stripe_webhooks_app

stripe_app.include_router(stripe_sessions_app)
stripe_app.include_router(stripe_webhooks_app)
