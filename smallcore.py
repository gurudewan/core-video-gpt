import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apis.auth.firebase_header import auth_header
import apis.chats_app as chats_app
from pprint import pprint

app = FastAPI()
# app.include_router(auth_api)
app.include_router(chats_app.chats_app)

# CORS config
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(chats_app.chats_app)


@app.get("/")
def health_check():
    return {"status": 200, "message": "videoGPT's small-core is online"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
