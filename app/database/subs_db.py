from .schemas import Subscription

from bson import ObjectId


from app.types.api_types import Subscription as SubscriptionAPI
from app.types.api_types import SubscriptionPlan
from app.types.api_types import SubscriptionStatus
from app.types.api_types import StripeSubscriptionStatus

from datetime import datetime


def get_sub_by_id(sub_id):
    return Subscription.objects(id=sub_id).first()


def get_sub_by_human_id(human_id):
    human_id = ObjectId(human_id)

    return Subscription.objects(human_id=human_id).first()


def add_new_sub(sub: SubscriptionAPI, human_id: str):

    new_sub = Subscription(
        human_id=ObjectId(human_id),
        plan=sub.plan,
        status=sub.status,
        start_date=sub.start_date,
        end_date=sub.end_date,
        stripe_subscription_id=sub.stripe_subscription_id,
        stripe_subscription_status=sub.stripe_subscription_status,
        cycle=sub.cycle,
    )
    new_sub.save()

    return new_sub
