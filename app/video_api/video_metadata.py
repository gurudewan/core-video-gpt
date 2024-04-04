import json

from app.types.type_models import ViewedVideo, ViewedImage

from pprint import pprint


def format_video_metadata(info_path):
    with open(info_path, "r") as json_file:
        info = json.load(json_file)
    # pprint(info)
    # print("============ is the info -------")

    formatted_info = {
        "platform_video_id": info["id"],
        "platform_id": "youtube",
        "platform_video_url": f"https://www.youtube.com/watch?v={info['id']}",
        "title": info["title"],
        "author_name": info["uploader"],
        "description": info["description"],
        "summary": None,
        "tags": info["tags"],
        "duration": info["duration"],
        "view": None,
        "all_info": info,
    }

    update_info(info_path, formatted_info)

    return formatted_info


def update_info(info_path, new_info):
    with open(info_path, "w") as json_file:

        def handle_viewed_image(obj):
            if isinstance(obj, (ViewedImage, ViewedVideo)):
                return obj.model_dump()
            elif isinstance(obj, list):
                return [handle_viewed_image(item) for item in obj]
            elif isinstance(obj, dict):
                return {k: handle_viewed_image(v) for k, v in obj.items()}
            else:
                return obj

        new_info = handle_viewed_image(new_info)

        json.dump(new_info, json_file, indent=4)
