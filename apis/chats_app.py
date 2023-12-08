from fastapi import APIRouter, Depends

from api_types import ChatResponse

chats_app = APIRouter()

from apis.auth.firebase_header import auth_header

import langchain_api.langchainer as langchainer

import chatgpt

from helpers.gcs_helper import gcs
from helpers.highlights_helper import extract_highlights

from pprint import pprint

from api_types import RootChatInput

from database import chats_db


def create_chat(human_id: str, video_info):
    title = video_info["title"]  # video_info[""]  # generate from AI? or rules based?

    chat_id = chats_db.create_new_chat(human_id, video_info, title)

    return chat_id


@chats_app.get("/chat/{chat_id}")
def get_chat(chat_id: str, human_id: str = Depends(auth_header)):
    return fetch_chat(chat_id, human_id)


def fetch_chat(chat_id: str, human_id: str):
    # get some video metadata as required
    # e.g. summary, view etc.

    # return the new chat

    chat = chats_db.find_chat_by_id(chat_id, human_id)
    print("the chat im returning is ")

    pprint(chat.to_mongo().to_dict())

    return ChatResponse(**chat.to_mongo().to_dict())


@chats_app.post("/chat")
def ask_question(chat_input: RootChatInput, human_id: str = Depends(auth_header)):
    print(chat_input)

    # take out the chat_id
    # find the chat in the db
    # append the user message
    # append the AI message

    # chat_id = None
    # chats_db.update_chat(chat_id, {})

    conversation = chat_input.messages
    user_question = next(
        (
            message.content
            for message in reversed(conversation)
            if message.role == "user"
        ),
        None,
    )

    video_id = chat_input.videoID

    docs = langchainer.do_vector_search(user_question, video_id)

    info = gcs.read_json(f"/tmp/youtube/{video_id}/info.json")

    answer = chatgpt.chat(conversation, docs, info)

    highlights = extract_highlights(docs)

    user_message = {"role": "user", "content": user_question}

    assistant_message = {
        "role": "assistant",
        "content": answer,
        "highlights": highlights,
    }

    chats_db.add_2_new_msgs(chat_input.chatID, user_message, assistant_message)

    return assistant_message


@chats_app.get("/chats")
def get_all_chats(human_id: str = Depends(auth_header)):
    """
    returns all the chats of a user
    """
    all_chats = chats_db.get_chats_by_human_id(human_id)

    return all_chats


@chats_app.delete("/chat/{chat_id}")
def delete_chat(chat_id: str, human_id: str = Depends(auth_header)):
    chats_db.delete_chat_by_id(chat_id, human_id)
    return
