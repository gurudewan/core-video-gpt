from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import stripe
import json

stripe_app = APIRouter()


@stripe_app.post("/webhook")
async def webhook_received(request: Request):
    webhook_secret = "whsec_12345"
    request_data = await request.json()

    if webhook_secret:
        signature = request.headers.get("stripe-signature")
        try:
            event = stripe.Webhook.construct_event(
                payload=await request.body(),
                sig_header=signature,
                secret=webhook_secret,
            )
            data = event["data"]
        except Exception as e:
            return JSONResponse(content={"detail": str(e)}, status_code=400)
        event_type = event["type"]
    else:
        data = request_data["data"]
        event_type = request_data["type"]
    data_object = data["object"]

    print("event " + event_type)

    if event_type == "checkout.session.completed":
        print("🔔 Payment succeeded!")
    elif event_type == "customer.subscription.trial_will_end":
        print("Subscription trial will end")
    elif event_type == "customer.subscription.created":
        print(f'Subscription created {event["id"]}')
    elif event_type == "customer.subscription.updated":
        print(f'Subscription updated {event["id"]}')
    elif event_type == "customer.subscription.deleted":
        print(f'Subscription canceled: {event["id"]}')

    return JSONResponse(content={"status": "success"})
