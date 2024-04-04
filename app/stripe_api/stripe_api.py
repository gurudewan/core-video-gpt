import stripe

from app.consts import consts

from app.database import humans_db


stripe.api_key = consts().STRIPE_API_KEY


def get_or_create_customer(email: str):
    customers = stripe.Customer.list(email=email).data

    if customers:
        return customers[0]
    else:
        return create_customer(email)


def create_customer(email: str):

    customer = stripe.Customer.create(
        email=email,
    )

    return customer


def create_customer_session(stripe_customer_id):
    customer_session = stripe.CustomerSession.create(
        customer=stripe_customer_id,
        components={"pricing_table": {"enabled": True}},
    )

    return customer_session.client_secret


def create_checkout_session(price_id: str, customer_id: str, customer_email: str):

    RETURN_URL = consts().STRIPE_CHECKOUT_RETURN_URL

    session = stripe.checkout.Session.create(
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        ui_mode="embedded",
        return_url=RETURN_URL,
        customer=customer_id,
        customer_email=customer_email,
        customer_creation="always",
    )

    return session


def get_checkout_session(session_id: str):
    session = stripe.checkout.Session.retrieve(session_id)
    return session


def get_customer(customer_id: str):
    customer = stripe.Customer.retrieve(customer_id)
    return customer


async def construct_event(request: any, signature: any, webhook_secret: str):

    event = stripe.Webhook.construct_event(
        payload=await request.body(),
        sig_header=signature,
        secret=webhook_secret,
    )

    return event
