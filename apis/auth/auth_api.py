from fastapi import APIRouter, Request, HTTPException

from apis.auth import tokeniser, postman
from apis.auth import auth_types

from database import humans_db

auth_api = APIRouter(prefix="/auth")

# ------------------------------------------MAGIC-----------------------------------------------#


@auth_api.post("/get-magic-email")
async def get_magic_email(email: auth_types.Email):
    """
    Accepts an email address.
    Creates a magic_token, and sends the magic link to the email address.
    """
    email_addr = email.email
    response = {}
    _id = None
    data = {}

    # Add new user or get existing user
    _id = humans_db.add_new_or_get_human(email_addr, "lifetime", 100, 100)

    if _id is None:
        raise HTTPException(status_code=501, detail="Error adding or retrieving user")

    data = {"_id": str(_id), "user_scope": "complete"}

    magic_token = tokeniser.create_token(data, "magic")
    sent_email = postman.send_magic_link(email_addr, magic_token)

    if sent_email is False:
        raise HTTPException(status_code=501, detail="Error sending email")

    response["content"] = "sent-email"

    return response


@auth_api.post("/swap-magic-token")
async def swap_magic_token(request: Request):
    """
    Accepts a magic_token, as sent by the client when the user opens the magic link
    The magic_token can be login or signup.
    Returns an auth_token (which will be either complete = login or partial = signup).
    This is also used to check if the user is authed?
    """

    magic_token = request.headers.get("token")

    auth_token = None
    response = {}

    if not tokeniser.validate_token(magic_token, "magic"):
        response["content"] = "invalid-magic-token"
        raise HTTPException(status_code=401, detail=response)

    data = tokeniser.decode_token(magic_token, "magic")
    auth_token = tokeniser.create_token(data, "auth")

    print("The scope of the magic_token was: ")
    print(data["user_scope"])
    # note: data['user_scope'] encodes whether it is partial auth or complete auth
    # so this state is preserved from magic to auth token

    response["content"] = {"auth_token": auth_token}
    return response


# ------------------------------------------CHECK AUTH-----------------------------------------------#


@auth_api.get("/swap-auth-token")
async def check_auth(request: Request):
    """
    Accepts an auth_token (complete | partial).
    Checks the validity of the auth_token.
    Responds with the authorisation state (authorised | partially-authorised | unauthorised)
    """
    auth_token = request.headers["token"]

    response = {}

    if not tokeniser.validate_token(auth_token, "auth"):
        response["content"] = {"auth_status": "unauthed"}
        raise HTTPException(status_code=401, detail=response)

    data = tokeniser.decode_token(auth_token, "auth")
    human_id = data["_id"]
    human = humans_db.find_human_by_id(human_id)
    human_email = human.email if human else None

    access_token = tokeniser.create_token(data, "access")
    refresh_token = tokeniser.create_token(data, "refresh")
    auth_token = tokeniser.create_token(data, "auth")

    tokens = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "auth_token": auth_token,
    }

    response["content"] = {
        "auth_status": "authed",
        "tokens": tokens,
        "email": human_email,
    }

    return response


# ------------------------------------------TOKENS SERVING-----------------------------------------------#


@auth_api.get("/swap-refresh-token")
def refresh_tokens(request: Request):
    """
    Accepts a refresh_token.
    If it is valid, serves new tokens = {access, auth, refresh}
    """

    refresh_token = request.headers.get("token")

    response = {}

    if not tokeniser.validate_token(refresh_token, "refresh"):
        response["content"] = "invalid-refresh-token"
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    data = tokeniser.decode_token(refresh_token, "refresh")

    auth_token = tokeniser.create_token(data, "auth")
    access_token = tokeniser.create_token(data, "access")
    refresh_token = tokeniser.create_token(data, "refresh")

    tokens = {
        "auth_token": auth_token,
        "access_token": access_token,
        "refresh_token": refresh_token,
    }

    response["content"] = tokens

    return response
