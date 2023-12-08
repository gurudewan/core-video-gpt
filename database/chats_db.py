from .schemas import Chat, Message
from datetime import datetime
from bson import ObjectId


def create_new_chat(human_id, video_info, title):
    new_chat = Chat(
        human_id=human_id,
        video_info=video_info,
        title=title,
        timestamps={"created": datetime.now(), "accessed": datetime.now()},
    )
    new_chat.save()

    return new_chat.id


def find_chat_by_id(chat_id, human_id):
    return Chat.objects(id=ObjectId(chat_id), human_id=ObjectId(human_id)).first()


def add_2_new_msgs(chat_id, user_message, assistant_message):
    chat = Chat.objects.get(id=ObjectId(chat_id))
    user_msg = Message(content=user_message["content"], role="user")
    assistant_msg = Message(
        content=assistant_message["content"],
        role="assistant",
        highlights=assistant_message["highlights"],
    )
    chat.messages.append(user_msg)
    chat.messages.append(assistant_msg)
    chat.save()
    return


def update_chat(chat_id, metadata):
    metadata["timestamps.accessed"] = datetime.now()
    Chat.objects(chat_id=chat_id).update(**metadata)


def get_chats_by_human_id(human_id):
    chats = Chat.objects(human_id=human_id).order_by("-timestamps.created")
    return [
        {
            "chat_id": str(chat.id),
            "title": chat.title,
            "timestamps": chat.timestamps,
            "video_id": chat.video_info.platform_video_id,
        }
        for chat in chats
    ]


def delete_chat_by_id(chat_id, human_id):
    chat = Chat.objects(id=ObjectId(chat_id), human_id=ObjectId(human_id)).first()
    if not chat:
        return {"error": "Chat not found"}
    elif chat.human_id != human_id:
        return {"error": "Unauthorized"}
    else:
        chat.delete()
        return {"message": "Chat deleted successfully"}
