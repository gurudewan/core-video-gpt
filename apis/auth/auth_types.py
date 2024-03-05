from pydantic import BaseModel


class MagicInput(BaseModel):
    email: str
    doChromeAuth: bool = False
