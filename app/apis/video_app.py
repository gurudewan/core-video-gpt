import app.langchain_api.langchainer as langchainer

import app.openai_api.chatgpt as chatgpt
import app.openai_api.whisper as whisper
import app.video_api.video_converter as video_converter
import app.file_api.filer as filer
from app.eyes.eyes import see
from fastapi import APIRouter, HTTPException, Depends


from app.types.api_types import VideoInput

import app.helpers.srt_helper as srt_helper
from app.video_api.video_metadata import format_video_metadata, update_info
from app.helpers.gcs_helper import gcs
from app.helpers.highlights_helper import extract_highlights

from app.apis.auth_app.firebase_header import auth_header

import time
from pprint import pprint
from app.types.type_models import ViewedImage, ViewedVideo

import app.subscriptions.access_manager as access_manager

import app.apis.chats_app as chats_app

from app.consts import consts

video_app = APIRouter(tags=["video"])


@video_app.post("/video")
async def post_video(video: VideoInput, human_id: str = Depends(auth_header)):
    video_path = None
    try:
        video_url = video.video_url

        video_id = video_converter.quickly_get_youtube_video_id(video_url)

        if video_id is None:
            raise HTTPException(status_code=422, detail="Invalid YouTube URL")

        video_is_old = filer.video_exists(video_id)

        seen = gcs.check_if_seen(
            video_id
        )  # TODO check gcs file exists for the key frames

        heard = True  # TODO check transcipt file exists for the transcript

        # TODO check if video is processing here as well?

        if video_is_old:
            pprint(f"-------video old: ID | {video_id}-------")

            # read the stored info from gcs
            info = gcs.read_json(f"/tmp/youtube/{video_id}/info.json")
            pprint(f"video already processed. ID | {video_id}")

        elif not video_is_old:
            pprint(f"-------video is new: ID | {video_id}-------")

            start = time.time()

            duration = video_converter.get_youtube_video_duration(video_id)
            subs_available = video_converter.check_subtitles_available(video_url)
            print("got subs and duration")
            # check that video is processable (by human's current subscription plan)
            # access_manager.check_if_human_can(human_id, duration, subs_available)

            print("====downloading video====")

            files = video_converter.download_youtube_video(
                video_url
            )  # contains all the data for the docs

            print("====download complete====")

            info = format_video_metadata(files["info"])

            video_path = f"tmp/youtube/{video_id}"

            # print("====uploading to gcs====")
            # gcs.upload_folder_to_gcs(video_path, "/" + video_path)
            # TODO create an empty folder here instead > which means it is processing

            subs_text = srt_helper.load_subtitles_text_only(files["subs"])

            print("===doing chatgpt stuff===")

            info["description"] = chatgpt.clean_up_description(info["description"])

            transcript_summary = chatgpt.summarise(subs_text, info)
            info["transcript_summary"] = transcript_summary

            print("===viewing video===")

            view = await see(video_id, info)

            info["view"] = view

            key_frames_captions = "/////NEW SCENE//////".join(
                [str(item["caption"]) for item in view if item["caption"] is not None]
            )

            key_frames_summary = chatgpt.summarise(key_frames_captions, info)
            info["key_frames_summary"] = key_frames_summary

            overall_summary = chatgpt.grand_summarise(
                transcript_summary, key_frames_summary
            )

            info["summary"] = overall_summary

            update_info(files["info"], info)

            filer.stream_var_into_gcs(info, f"/tmp/youtube/{video_id}/info.json")

            print("===doing langchain===")

            langchainer.embed(video_id, info)

            print("====uploading to gcs====")
            gcs.upload_folder_to_gcs(video_path, "/" + video_path)

            filer.delete_folder(video_path)
            filer.delete_video_from_gcs(video_id)

            end = time.time()
            elapsed_time = end - start
            print(f"processed video: {video_id} in {elapsed_time} seconds")

        chat_id = chats_app.create_chat(human_id, info)

        print(f"successfully processed video {video_id}")
        return {"chat_id": str(chat_id)}
    except HTTPException as http_error:
        raise http_error
    except Exception as e:
        print(f"upload failed for {video_id}, cleaning up")
        print(f"exception: {e}")

        if video_path:
            filer.delete_folder(video_path)
            gcs.delete_folder("/" + video_path)
        raise HTTPException(status_code=500, detail=str(e))
