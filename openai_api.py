import openai
import json


OPENAI_API_KEY="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"


def transcribe(audio_path, openai_api_key=OPENAI_API_KEY):
    openai.api_key = openai_api_key

    audio_file= open(audio_path, "rb")

    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    
    filename = audio_path.split("/")[-1].split(".")[0]
    
    transcript["filename"] = filename

    with open(f'/tmp/youtube/text/{filename}.json', 'w') as json_file:
        json.dump(transcript, json_file)

    return transcript

