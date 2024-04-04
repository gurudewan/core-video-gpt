import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# from apis.auth.auth_api import auth_api

# from apis.chats_app import chats_app
import app.apis.humans_app as humans_app
import app.apis.chats_app as chats_app
import app.apis.stripe_apps.stripe_app as stripe_app
import app.apis.auth_app.firebase_auth_app as auth_app
import app.apis.video_app as video_app

app = FastAPI()


# app.include_router(auth_api)
app.include_router(video_app.video_app)
app.include_router(chats_app.chats_app)
app.include_router(humans_app.humans_app)
app.include_router(auth_app.auth_app)
app.include_router(stripe_app.stripe_app)


@app.get("/")
def health_check():
    return {"status": 200, "message": "videoGPT's hard-core is online"}


# CORS config
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, workers=10)
