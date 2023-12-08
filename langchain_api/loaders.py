from langchain.document_loaders import JSONLoader
from langchain.document_loaders import SRTLoader


from pysrt import open as open_srt
from pprint import pprint


def load_video_subtitles(video_id):
    subs_file_path = f"tmp/youtube/{video_id}/subs.srt"

    subs = open_srt(subs_file_path)

    raw_data = []
    for sub in subs:
        record = {
            "page_content": sub.text,
            "start": sub.start.ordinal,
            "end": sub.end.ordinal,
        }

        metadata = subtitles_metadata_func(record, video_id)
        raw_data.append(metadata)

    return raw_data


def subtitles_metadata_func(record: dict, video_id: str) -> dict:
    metadata = {
        "page_content": record.get("page_content"),
        "start": record.get("start"),
        "end": record.get("end"),
        "video_id": video_id,
        "type": "transcript",
    }
    return metadata


def load_openai_transcript(filename):
    # used for an OpenAI transcript dumped into a json

    file_path = f"tmp/youtube/text/{filename}.json"
    loader = JSONLoader(
        file_path=file_path,
        jq_schema=".",
        content_key="text",
        metadata_func=metadata_func,
    )

    raw_data = loader.load()

    # print(raw_data)

    return raw_data


def metadata_func(record: dict, metadata: dict) -> dict:
    # metadata["source_id"] = record.get("document_id")

    return metadata


def default_load_video_subtitles(video_id):
    # this concats everything into 1 big document
    # TODO use this for global context
    # ! this is currently unused

    file_path = f"tmp/youtube/{video_id}/subs.srt"

    srt_loader = SRTLoader(file_path)

    documents = srt_loader.load()

    pprint(documents)

    return documents
