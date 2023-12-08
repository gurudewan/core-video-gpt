# for loading .env
import os

# env
APP_ENV = os.getenv("APP_ENV") if os.getenv("APP_ENV") is not None else "DEV"
# | "DEV" || "PROD"

# ================== LANGCHAIN CONSTS ==================
MAX_NUM_SENTENCES = 100  # not used anymore
MAX_NUM_TOKENS = 300
CHUNK_OVERLAP = 50

# ================== GCLOUD ==================
PROD_BUCKET_NAME = "video-gpt-prod-files"
DEV_BUCKET_NAME = "video-chat-files"
# BUCKET_NAME=DEV_BUCKET_NAME if APP_ENV == "DEV" else PROD_BUCKET_NAME
BUCKET_NAME = PROD_BUCKET_NAME

DEV_STORAGE_KEYS = "keys/storage-manager-keys-dev.json"
PROD_STORAGE_KEYS = "keys/storage-manager-keys-prod.json"
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

STORAGE_KEYS = PROD_STORAGE_KEYS

# ================== FIREBASE ==================
FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS")

# ================== OPENAI CONSTS ==================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-3.5-turbo"
OPENAI_MODEL_FOR_SUMMARIES = "gpt-3.5-turbo-16k"
MAX_TOKENS_FOR_SUMMARIES_OUTPUT = 300
MAX_TOKENS_FOR_DESCRIPTIONS_OUTPUT = 300
BATCH_SIZE_FOR_BATCHED_SUMMARIES_INPUT = 3000

DO_FAKE_GPT_CALLS = os.getenv("DO_FAKE_GPT_CALLS") == "True"

# ================== PROMPTS ==================

SUMMARISE_SYSTEM_PROMPT = "I'll give you data about a video, and then you have to summarise the video in text. The data will include: a subtitle (.srt) file, some related metadata, and some text descriptions of some of the video's keyframes. Summarise accurately and concisely, but also try to capture the essence, tone, emotion, and personality of the video. I'll give all of the data to you in one big blob of text."
CLEANUP_DESCRIPTION_SYSTEM_PROMPT = "I'll provide you with a YouTube description, taken directly from the video. You need to clean up all the extraneous information, which wouldn't be relevant to someone who wants to understand the video. Please give me only the relevant details I need to understand the actual content of the video, the speaker, or anything else that might be relevant. Please provide verbatim the bits of text you think are important, and nothing else."
QA_SYSTEM_PROMPT = "You are videoGPT. I'll ask you a question, and then give you the relevant parts of the transcript of a video, the title of the video, a summary and decription of the video. Your job is to answer my questions about the video in a way that is concise and accurate. Your source of truth is the info I give you about the video, rather than what may actually be true in the real world. When I ask you a question, it's directed at the video, not at you. Try to extract identities of relevant people, names and things. Pay close attention to the title or description to contextualise the video. Be brief. Be concise.  Maintain the tone & essence of the video. Answer my questions directly. Don't say things like 'Based on the provided information' or 'Based on the sources'. Instead, refer to it as the video and just say what you want to say directly."


# ================== MONGO DB ==================

DB_CONN_STRING = (
    os.getenv("PROD_DB_CONN_STRING")
    if APP_ENV == "PROD"
    else os.getenv("DEV_DB_CONN_STRING")
)
if DB_CONN_STRING is None:
    print("DB_CONN_STRING is not configured in the .env")

# ================== ARCHIVE ==================
AZURE_ACCOUNT_ID = "a6fdeb9c-a185-40a2-a4b1-bb400d7f1b7a"
AZURE_SUBSCRIPTION_KEY = "ce1cdca2743048bebb01c98a909f3128"


# ================== APP URL (AUTH) ==================
DEV_VIDEOGPT_APP_URL = "http://localhost:19006"
PROD_VIDEOGPT_APP_URL = "https://videogpt.pro"

VIDEOGPT_APP_URL = PROD_VIDEOGPT_APP_URL if APP_ENV == "PROD" else DEV_VIDEOGPT_APP_URL
