from fastapi import Depends, HTTPException, Header, Request
from typing import Optional

from ..auth import tokeniser

from bson import ObjectId


async def auth_header(request: Request):
    token = request.headers.get("token", None)

    if not token or not tokeniser.validate_token(token, "access"):
        raise HTTPException(status_code=401, detail="Invalid access token")

    print("is valid")
    data = tokeniser.decode_token(token, "access")
    human_id = ObjectId(data["_id"])
    return human_id
