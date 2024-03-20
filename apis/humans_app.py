from fastapi import APIRouter, Depends, FastAPI
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


from database import humans_db
from apis.auth.firebase_header import auth_header

from api_types import HumanResponse, Subscription

humans_app = APIRouter()


@humans_app.post("/get-human", response_model=HumanResponse)
def get_human(human_id: str = Depends(auth_header)):
    human = humans_db.find_human_by_id(human_id)
    if human:
        print(human.subscription)

        # subscription = Subscription(**human.subscription)
        subscription_dict = jsonable_encoder(human.subscription)

        # Create an instance of HumanResponse
        human_response = HumanResponse(
            id=str(human.id),  # Convert ObjectId to string
            email=human.email,
            firebase_id=human.firebase_id,
            stripe_customer_id=human.stripe_customer_id,
            subscription=subscription_dict,  # TODO subscription
            tokens_left=human.tokens_left,
            tokens_allowed=human.tokens_allowed,
            sign_up_date=human.sign_up_date,
            # Add other fields as necessary
        )
        return human_response
    return JSONResponse(status_code=404, content={"message": "Human not found"})
