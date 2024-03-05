from fastapi import APIRouter, Depends, HTTPException

from firebase_admin import auth

from apis.auth.firebase_header import firebase_auth_header

from apis.auth import postman

from apis.auth.auth_types import MagicInput
from urllib.parse import urlencode

auth_app = APIRouter()

from consts import VIDEOGPT_APP_URL


@auth_app.post("/custom-token")
async def get_custom_token(firebase_user_id: str = Depends(firebase_auth_header)):
    custom_token = auth.create_custom_token(firebase_user_id)

    return {"token": custom_token}


@auth_app.post("/magic-link")
async def get_magic_link(magic_input: MagicInput):
    try:
        email = magic_input.email

        continue_url = (
            VIDEOGPT_APP_URL
            + "?"
            + urlencode({"email": email, "doChromeAuth": magic_input.doChromeAuth})
        )

        action_code_settings = auth.ActionCodeSettings(
            url=continue_url,
            handle_code_in_app=True,
        )

        magic_link = auth.generate_sign_in_with_email_link(email, action_code_settings)

        postman.send_magic_link(email, magic_link)

        return {"status": "success", "code": 200}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
