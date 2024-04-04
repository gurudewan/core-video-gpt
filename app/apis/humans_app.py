from fastapi import APIRouter, Depends, FastAPI
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


from app.database import humans_db, subs_db
from app.apis.auth.firebase_header import auth_header

from app.types.api_types import (
    HumanResponse,
    Subscription,
    SubscriptionPlan,
    SubscriptionStatus,
    SubscriptionCycle,
)

humans_app = APIRouter(tags=["human"])


@humans_app.post("/get-human")
def get_human(human_id: str = Depends(auth_header)):
    human = humans_db.find_human_by_id(human_id)
    if human:

        subscription = subs_db.get_sub_by_human_id(human_id)

        if subscription is not None:
            subscription = Subscription(
                plan=subscription.plan,
                status=subscription.status,
                start_date=subscription.start_date,
                end_date=subscription.end_date,
                stripe_subscription_id=subscription.stripe_subscription_id,
                stripe_subscription_status=subscription.stripe_subscription_status,
                cycle=subscription.cycle,
            )

        else:
            subscription = Subscription(
                plan=SubscriptionPlan.FREE,
                status=SubscriptionStatus.ACTIVE,
            )

        # Create an instance of HumanResponse
        human_response = HumanResponse(
            id=str(human.id),
            email=human.email,
            firebase_id=human.firebase_id,
            stripe_customer_id=human.stripe_customer_id,
            subscription=subscription,
            sign_up_date=human.sign_up_date,
        )
        return human_response
    return JSONResponse(status_code=404, content={"message": "Human not found"})
