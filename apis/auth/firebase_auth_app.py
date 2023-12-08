from fastapi import FastAPI, Depends

from firebase_admin import auth
import firebase_admin

from firebase_header import firebase_auth_header

app = FastAPI()


from fastapi import Depends


@app.get("/custom-token")
async def get_custom_token(firebase_user_id: str = Depends(firebase_auth_header)):
    # Initialize the app with a service account, granting admin privileges
    firebase_admin.initialize_app()  # Uncomment this if the app is not initialized elsewhere

    custom_token = auth.create_custom_token(firebase_user_id)

    return {"token": custom_token}
