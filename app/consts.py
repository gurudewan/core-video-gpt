# for loading .env
import os
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class consts(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    # env
    APP_ENV: str = "PROD"
    # os.getenv("APP_ENV") if os.getenv("APP_ENV") is not None else "DEV"
    # | "DEV" || "PROD"

    # ================== YOUTUBE CONSTS ==================
    MAX_VIDEO_DURATION: int = 1500

    # ================== LANGCHAIN CONSTS ==================
    MAX_NUM_SENTENCES: int = 100  # not used anymore
    MAX_NUM_TOKENS: int = 300
    CHUNK_OVERLAP: int = 50

    # ================== GCLOUD ==================
    PROD_BUCKET_NAME: str = "video-gpt-prod-files"
    DEV_BUCKET_NAME: str = "video-chat-files"
    # BUCKET_NAME=DEV_BUCKET_NAME if APP_ENV == "DEV" else PROD_BUCKET_NAME
    BUCKET_NAME: str = PROD_BUCKET_NAME  # if APP_ENV == "PROD" else DEV_BUCKET_NAME

    DEV_STORAGE_KEYS: str = "keys/storage-manager-keys-dev.json"
    PROD_STORAGE_KEYS: str = "keys/storage-manager-keys-prod.json"
    GOOGLE_APPLICATION_CREDENTIALS: str = "keys/storage-manager-keys-prod.json"

    STORAGE_KEYS: str = PROD_STORAGE_KEYS

    # ================== FIREBASE ==================
    FIREBASE_CREDENTIALS: str = "keys/firebase-keys-prod.json"

    # ================== EMAIL ==================

    EMAIL_ADDRESS: str = "flowmushin@gmail.com"

    # ================== OPENAI CONSTS ==================
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = "gpt-3.5-turbo"  # gpt-4-1106-preview
    OPENAI_MODEL_FOR_SUMMARIES: str = "gpt-3.5-turbo-16k"
    MAX_TOKENS_FOR_SUMMARIES_OUTPUT: int = 300
    MAX_TOKENS_FOR_DESCRIPTIONS_OUTPUT: int = 300
    BATCH_SIZE_FOR_BATCHED_SUMMARIES_INPUT: int = 3000

    DO_FAKE_GPT_CALLS: str = os.getenv("DO_FAKE_GPT_CALLS") == "True"

    # ================== PROMPTS ==================

    SUMMARISE_SYSTEM_PROMPT: str = (
        "I'll give you a description about a video, and then you have to summarise the video. "
        "The data will include: the transcript file, some related metadata, and some text descriptions "
        "of some of the video's keyframes. Summarise accurately and concisely, but also try to capture "
        "the essence, tone, emotion, and personality of the video. I'll give all of the data to you in one big blob of text."
    )
    GRAND_SUMMARY_SYSTEM_PROMPT: str = (
        "I'll give you two summaries: a summary of the transcript of my video, and then a summary of the key frames "
        "of my video. You need to merge the two summaries into one, without losing any of the content of either descriptions. "
        "No nonsense. Just give me the direct summary."
    )
    CLEANUP_DESCRIPTION_SYSTEM_PROMPT: str = (
        "I'll provide you with a YouTube description, taken directly from the video. You need to clean up all the extraneous "
        "information, which wouldn't be relevant to someone who wants to understand the video. Please give me only the relevant "
        "details I need to understand the actual content of the video, the speaker, or anything else that might be relevant. "
        "Please provide verbatim the bits of text you think are important, and nothing else."
    )
    QA_SYSTEM_PROMPT: str = (
        "You are videoGPT. I'll ask you a question, and then give you the relevant parts of the transcript of a video, the title "
        "of the video, a summary and description of the video. Your job is to answer my questions about the video in a way that is "
        "concise and accurate. Your source of truth is the info I give you about the video, rather than what may actually be true in "
        "the real world. When I ask you a question, it's directed at the video, not at you. Try to extract identities of relevant people, "
        "names and things. Pay close attention to the title or description to contextualise the video. Be brief. Be concise. Maintain the "
        "tone & essence of the video. Answer my questions directly. Don't say things like 'Based on the provided information' or 'Based on "
        "the sources'. Instead, refer to it as the video and just say what you want to say directly."
    )

    # ================== MONGO DB ==================


    DB_CONN_STRING: str = (
        PROD_DB_CONN_STRING if APP_ENV == "PROD" else DEV_DB_CONN_STRING
    )

    if DB_CONN_STRING is None:
        print("DB_CONN_STRING is not configured in the .env")

    # DB_CONN_STRING = os.getenv("PROD_DB_CONN_STRING")

    # ================== ARCHIVE ==================
    AZURE_ACCOUNT_ID: str = "a6fdeb9c-a185-40a2-a4b1-bb400d7f1b7a"

    # ================== APP URL (AUTH) ==================
    DEV_VIDEOGPT_APP_URL: str = "http://localhost:19006"
    PROD_VIDEOGPT_APP_URL: str = "https://videogpt.pro"

    VIDEOGPT_APP_URL: str = (
        PROD_VIDEOGPT_APP_URL if APP_ENV == "PROD" else DEV_VIDEOGPT_APP_URL
    )

    # ================== PORT ==================

    PORT: int = 8080

    # ================== STRIPE ==================

    # API KEY


    STRIPE_API_KEY: str = DEV_STRIPE_API_KEY

    # WEBHOOK SECRET

    PROD_STRIPE_WEBHOOK_SECRET: str = ""

    STRIPE_WEBHOOK_SECRET: str = DEV_STRIPE_WEBHOOK_SECRET

    # RETURN URL

    STRIPE_CHECKOUT_RETURN_URL: str = (
        VIDEOGPT_APP_URL + "/stripe-checkout-complete?session_id={CHECKOUT_SESSION_ID}"
    )
