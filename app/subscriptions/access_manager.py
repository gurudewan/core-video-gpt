from app.database import humans_db, subs_db
from app.types.api_types import SubscriptionPlan

from fastapi import HTTPException

from app.consts import consts


def check_if_human_can(human_id, duration, subs_available):
    """
    Checks if human can:
        - watch a video: given duration, and whether a transcript is needed.
    Raises HTTP errors directly if not.
    """

    if duration > consts().MAX_VIDEO_DURATION or duration is None:
        raise HTTPException(status_code=422, detail="video-too-big-duration")

    human = humans_db.find_human_by_id(human_id=human_id)

    subscription = subs_db.get_sub_by_human_id(human["_id"])

    plan = subscription.plan

    if plan in [SubscriptionPlan.PLUS, SubscriptionPlan.PRO]:
        return

    elif plan == SubscriptionPlan.FREE:
        if duration > consts().MAX_VIDEO_DURATION:
            raise HTTPException(status_code=422, detail="sub-too-low-duration")
        if not subs_available:
            raise HTTPException(status_code=422, detail="sub-too-low-transcript")

    elif plan == SubscriptionPlan.BASIC:
        if duration > consts().MAX_VIDEO_DURATION + 500:
            raise HTTPException(status_code=422, detail="sub-too-low-duration")
