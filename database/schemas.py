from mongoengine import (
    Document,
    StringField,
    IntField,
    DateTimeField,
    EmbeddedDocument,
    StringField,
    ListField,
    Document,
    StringField,
    URLField,
    ListField,
    DictField,
    ObjectIdField,
    DateTimeField,
    EmbeddedDocumentField,
    DynamicField,
)

from mongoengine import connect

from consts import DB_CONN_STRING

if DB_CONN_STRING is None:
    print("ERROR: set the DB_CONN_STRING as an env var")


connect(host=DB_CONN_STRING)


class Human(Document):
    email = StringField(required=True)

    firebase_id = StringField(required=True)

    subscription_type = StringField(
        required=True, choices=("free", "student", "hobby", "pro", "lifetime")
    )
    tokens_left = IntField(required=True)
    tokens_allowed = IntField(required=True)

    sign_up_date = DateTimeField(required=True)
    last_login = DateTimeField()
    plan_refresh_date = DateTimeField()

    stripe_customer_id = StringField()


# ============ CHAT ============


class Message(EmbeddedDocument):
    role = StringField(required=True)
    content = StringField(required=True)
    highlights = DynamicField()


class VideoInfo(EmbeddedDocument):
    platform_id = StringField(choices=("youtube",), required=True)
    platform_video_id = StringField(required=True)
    platform_video_url = URLField(required=True)
    title = StringField(required=True)
    description = StringField(required=True)
    author_name = StringField(required=True)
    summary = StringField()
    tags = ListField(StringField())
    duration = IntField(required=True)
    view = DynamicField()  # TODO make this a type?
    all_info = DynamicField()


class Timestamps(EmbeddedDocument):
    created = DateTimeField(required=True)
    accessed = DateTimeField(required=True)


class Chat(Document):
    chat_id = ObjectIdField()
    human_id = ObjectIdField()
    video_info = EmbeddedDocumentField(VideoInfo, required=True)
    title = StringField(required=True)
    messages = ListField(EmbeddedDocumentField(Message))
    timestamps = EmbeddedDocumentField(Timestamps)
