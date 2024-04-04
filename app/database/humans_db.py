from .schemas import Human
from app.types.api_types import Subscription
from app.types.api_types import SubscriptionPlan
from app.types.api_types import SubscriptionStatus
from app.types.api_types import StripeSubscriptionStatus

from datetime import datetime

import app.stripe_api.stripe_api as stripe_api


def add_new_or_get_human(firebase_id, email):
    existing_human = Human.objects(firebase_id=firebase_id).first()

    if existing_human:
        return existing_human

    subscription = Subscription(
        plan=SubscriptionPlan.FREE,
        status=SubscriptionStatus.ACTIVE,
        start_date=datetime.now(),
        end_date=datetime.now(),
        stripe_subscription_id=None,
        stripe_subscription_status=StripeSubscriptionStatus.ACTIVE,
    )

    stripe_customer_id = stripe_api.create_customer(email)

    new_human = Human(
        firebase_id=firebase_id,
        email=email,
        subscription=subscription,
        sign_up_date=datetime.now(),
        stripe_customer_id=stripe_customer_id,
    )
    new_human.save()

    return new_human


def find_human_by_id(human_id):
    return Human.objects(id=human_id).first()


def find_human_by_firebase_id(firebase_id):
    return Human.objects(firebase_id=firebase_id).first()


def update_human(human_id=None, stripe_customer_id=None, update={}):
    if human_id:
        Human.objects(id=human_id).update(**update)
    elif stripe_customer_id:
        Human.objects(stripe_customer_id=stripe_customer_id).update(**update)


def update_humans_subscription(human_id, new_subscription):

    subscription = Subscription(
        plan=new_subscription.plan,
        status=new_subscription.status,
        # start_date=datetime.now()
    )

    return


def change_subscription_plan(human_id, new_subscription_plan: SubscriptionPlan):
    subscription = Subscription(
        plan=new_subscription_plan,
        status=SubscriptionStatus.ACTIVE,
        start_date=datetime.now(),
        end_date=datetime.now(),
    )

    subscription_data = {"subscription": subscription.to_mongo().to_dict()}

    update_human(human_id=human_id, update=subscription_data)

    return


def cancel_or_pause_subscription_plan(stripe_customer_id):
    subscription = Subscription(
        plan=SubscriptionPlan.CANCELED,
        status=SubscriptionStatus.INACTIVE,
        start_date=datetime.now(),
        end_date=datetime.now(),
        stripe_subscription_status=StripeSubscriptionStatus.CANCELED,
    )

    update_data = {
        "subscription.status": SubscriptionStatus.PAUSED,
        "subscription.stripe_subscription_status": StripeSubscriptionStatus.DELETED,
    }

    update_human(stripe_customer_id=stripe_customer_id, update=update_data)


if __name__ == "__main__":
    id = add_new_or_get_human("gauravdewan@live.com")
    print(id)
