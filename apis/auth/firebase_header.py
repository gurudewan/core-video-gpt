from fastapi import Depends, HTTPException, Header, Request
from firebase_admin import auth, initialize_app, credentials
from firebase_admin.auth import InvalidIdTokenError

from database import humans_db
from consts import FIREBASE_CREDENTIALS

cred = credentials.Certificate(FIREBASE_CREDENTIALS)

# initialize Firebase
default_app = initialize_app(credential=cred)


async def auth_header(request: Request):
    """
    auth header that wraps around MongoDB human_id
    """
    token = request.headers.get("token", None)

    if not token:
        raise HTTPException(status_code=401, detail="Missing access token")

    try:
        decoded_token = auth.verify_id_token(token)
        firebase_id = decoded_token["uid"]
    except InvalidIdTokenError:
        raise HTTPException(status_code=401, detail="Invalid access token")

    email = decoded_token.get("email")

    if email is None:
        email = f"{firebase_id}@videogpt.pro"

    human_id = humans_db.add_new_or_get_human(firebase_id, email)

    return human_id


async def firebase_auth_header(request: Request):
    """
    auth header that returns the firebase_id
    """
    token = request.headers.get("token", None)

    if not token:
        raise HTTPException(status_code=401, detail="Missing access token")

    try:
        decoded_token = auth.verify_id_token(token)
        firebase_id = decoded_token["uid"]
    except InvalidIdTokenError:
        raise HTTPException(status_code=401, detail="Invalid access token")

    return firebase_id
