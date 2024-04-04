from fastapi import Request, APIRouter, Header
from fastapi.responses import JSONResponse

from app.apis.stripe_apps.stripe_app import stripe_app

import app.database.subs_db as subs_db

import stripe

from app.consts import consts

from pprint import pprint

stripe_webhooks_app = APIRouter()

# ============================= WEBHOOK =============================


@stripe_webhooks_app.post("/webhooks")
async def process_webhook(request: Request, stripe_signature: str = Header(None)):

    data = await request.body()
    try:
        event = stripe.Webhook.construct_event(
            payload=data,
            sig_header=stripe_signature,
            secret=consts().STRIPE_WEBHOOK_SECRET,
        )
        event_data = event["data"]
    except ValueError as e:
        # Invalid payload
        print("an error occured while decoding stripe webhook - value error")
        raise e
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise e
    except Exception as e:
        return JSONResponse(content={"detail": str(e)}, status_code=400)

    data = event["data"]

    event_type = event["type"]

    data_object = data["object"]

    if event_type == "checkout.session.completed":
        print(f"event {event}")
        print("-------")
        print(f"event type {event_type}")
        print("-------")
        # print(f"event data {data_object}")
        print("-------")
        # Sent when a customer clicks the Pay or Subscribe button in Checkout, informing you of a new purchase.

        # provision the subscription (for the first time)

        # call subs_db
        # add a new subscription
        # set all other ones to False

        # humans_db.change_subscription_plan()
        print(data)
    elif event_type == "invoice.paid":
        # Sent each billing interval when a payment succeeds.

        # Continue to provision the subscription as payments continue to be made.
        # Store the status in your database and check when a user accesses your service.
        print(data)
    elif event_type == "invoice.payment_failed":

        # Sent each billing interval if there is an issue with your customer’s payment method.

        # Notify your customer and send them to the customer portal to update their payment information.

        print(data)

    elif event_type == "customer.subscription.deleted":
        # set all subscriptions in subs_db to INACTIVE or DELETED

        print(f'Subscription canceled: {event["id"]}')
    elif event_type == "customer.subscription.trial_will_end":
        print("Subscription trial will end")
    elif event_type == "customer.subscription.created":
        print(f'Subscription created {event["id"]}')
    elif event_type == "customer.subscription.updated":
        print(f'Subscription updated {event["id"]}')

    return JSONResponse(content={"status": "success"})
