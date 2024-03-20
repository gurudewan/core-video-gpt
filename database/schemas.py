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
    EmbeddedDocumentField,
    BooleanField,
)

from mongoengine import connect

from consts import Consts

consts = Consts()

if consts.DB_CONN_STRING is None:
    print("ERROR: set the DB_CONN_STRING as an env var")


connect(host=consts.DB_CONN_STRING)


class Subscription(EmbeddedDocument):
    plan = StringField(required=True)
    start_date = DateTimeField()
    end_date = DateTimeField()
    is_active = BooleanField(required=True)
    stripe_subscription_id = StringField()


class Human(Document):
    email = StringField(required=True)
    firebase_id = StringField(required=True)
    subscription = EmbeddedDocumentField(Subscription)
    tokens_left = IntField(required=True)
    tokens_allowed = IntField(required=True)
    sign_up_date = DateTimeField(required=True)

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
    key_frames_summary = StringField()
    transcript_summary = StringField()
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
    meta = {
        "indexes": [
            "timestamps.created",
        ]
    }
