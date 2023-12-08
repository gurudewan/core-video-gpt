from .schemas import Human
from datetime import datetime


def add_new_or_get_human(
    firebase_id, email, subscription_type="free", tokens_left=1000, tokens_allowed=1000
):
    existing_human = Human.objects(firebase_id=firebase_id).first()
    if existing_human:
        return existing_human.id

    new_human = Human(
        firebase_id=firebase_id,
        email=email,
        subscription_type=subscription_type,
        tokens_left=tokens_left,
        tokens_allowed=tokens_allowed,
        sign_up_date=datetime.now(),
    )
    new_human.save()

    return new_human.id


def find_human_by_id(human_id):
    return Human.objects(id=human_id).first()


def find_human_by_firebase_id(firebase_id):
    return Human.objects(firebase_id=firebase_id).first()


def update_human(human_id, metadata):
    Human.objects(id=human_id).update(**metadata)


if __name__ == "__main__":
    id = add_new_or_get_human("gauravdewan@live.com", "lifetime", 100, 100)
    print(id)
