from pydantic import BaseModel

from fastapi import APIRouter, HTTPException, Depends
from apis.auth.firebase_header import auth_header

from database import humans_db

import stripe

from stripe_api import stripe_api

stripe_sessions_app = APIRouter()


class CheckoutSessionRequest(BaseModel):
    price_id: str


@stripe_sessions_app.post("/create_checkout_session")
async def create_checkout_session(
    request: CheckoutSessionRequest, human_id: str = Depends(auth_header)
):

    customer_email = humans_db.find_human_by_id(human_id)["email"]

    stripe_customer = stripe_api.get_or_create_customer(customer_email)

    session = stripe_api.create_checkout_session(request.price_id, customer_email)

    print(session)

    return session


class SessionStatusRequest(BaseModel):
    session_id: str


@stripe_sessions_app.get("/check_checkout_session_status")
async def get_session_status(
    request: SessionStatusRequest, human_id: str = Depends(auth_header)
):
    try:

        session = stripe_api.get_checkout_session(request.session_id)

        customer = stripe_api.get_customer(session.customer)

    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "status": session.status,
        "payment_status": session.payment_status,
        "customer_email": customer.email,
    }


@stripe_sessions_app.post("/create_customer_session")
async def create_customer_session(human_id: str = Depends(auth_header)):

    human = humans_db.find_human_by_id(human_id)

    stripe_customer_id = human["stripe_customer_id"]

    print(human)
    print(human_id)
    print(stripe_customer_id)

    if stripe_customer_id is None:
        print("CREATING A CUDTOMER FOR A SESSION")
        stripe_customer = stripe_api.create_customer(human["email"])
        stripe_customer_id = stripe_customer["id"]

    client_secret = stripe_api.create_customer_session(stripe_customer_id)

    print("client secret is")
    print(client_secret)

    return client_secret
