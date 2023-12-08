import logging
from time import time

logging.getLogger().setLevel(logging.INFO)
import jwt
from datetime import datetime, timedelta

import consts

"""
    Handles creation and verification of JWT tokens.
    Used for authorisation of the app when making requests to the core.
"""

SECRETS = {
    "secret": "flowgauravD1flow",
    "auth": "flowgauravD1flow",
    "magic": "flowgauravD1flow",
    "access": "flowgauravD1flow",
    "refresh": "flowgauravD1flow",
}

ENV = consts.APP_ENV


def create_token(data, jwtype):
    # returns a string token
    # accepts params specifying data & the type of token

    data["iss"] = "flow-core"
    data["iat"] = datetime.now()  # - timedelta(hours=1)
    data["type"] = jwtype
    data["env"] = ENV

    if jwtype == "auth":
        data["exp"] = datetime.now() + timedelta(days=6)  # timedelta(hours = 1)
    elif jwtype == "magic":
        data["exp"] = datetime.now() + timedelta(hours=1)  # timedelta(days=6)
    elif jwtype == "access":
        data["exp"] = datetime.now() + timedelta(days=24)
    elif jwtype == "refresh":
        data["exp"] = datetime.now() + timedelta(days=7)  # 2 days
        # ?does or does not expire?

    jwtoken = jwt.encode(data, SECRETS[jwtype], algorithm="HS256")

    # token = jwtoken.decode("utf-8")  # convert from byte string to utf-8 string

    return jwtoken


def decode_token(jwtoken, jwtype):
    if isinstance(jwtoken, str):
        # if the token is in string form we convert it to bytes form
        jwtoken = jwtoken.encode("utf-8")

    decoded_token = jwt.decode(
        jwtoken, SECRETS[jwtype], leeway=10, algorithms=["HS256"]
    )

    return decoded_token


def validate_token(jwtoken, jwtype):
    """
    Accepts a token, and the expected type = "auth" | "magic" | "access" | "refresh".
    Returns is token valid boolean True | False.
    """
    try:
        decode_token(jwtoken, jwtype)
        return True
    except Exception as e:
        logging.error(e)
    except jwt.exceptions.ExpiredSignatureError:
        logging.info("Signature expired. Please provide a new token.")
        return False
    except jwt.exceptions.InvalidSignatureError:
        logging.info("Invalid signature. Please provide a new token")
        return False
    except jwt.exceptions.DecodeError:
        logging.info("Decode Error. Please provide a new token")
        return False
    # according to realpython.com, only InvalidTokenError and ExpiredSignatureError need to be checked
    # except jwt.exceptions.InvalidTokenError:
    #   logging.info( 'Invalid token. Please log in again.')
    #  return False


if __name__ == "__main__":
    # create a chaii pot dash token
    data = {"sub": "5f36646d874d5b2b5d3dbb59"}
    access_token = create_token(data, "access")
    auth_token = create_token(data, "auth")

    print(access_token)
    print(auth_token)

    test_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI2NTYxY2Q1OTFlNjdkYTM1MGQ3MmU1OGMiLCJ1c2VyX3Njb3BlIjoiY29tcGxldGUiLCJpc3MiOiJmbG93LWNvcmUiLCJpYXQiOjE3MDExMTQ3NjUsInR5cGUiOiJhY2Nlc3MiLCJlbnYiOiJQUk9EIiwiZXhwIjoxNzAzMTg4MzY1fQ.f2DCGRFAsWKRkW_1boh14ENkAPGK64XZas3vdyuiKjw"
    # print(validate_token(test_token, "access"))
