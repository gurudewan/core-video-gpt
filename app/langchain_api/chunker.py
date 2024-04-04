import app.helpers.tokenizer as tokenizer
from app.consts import consts


def chunkize(
    raw_data,
    MAX_NUM_SENTENCES=consts().MAX_NUM_SENTENCES,
    MAX_NUM_TOKENS=consts().MAX_NUM_TOKENS,
    CHUNK_OVERLAP=consts().CHUNK_OVERLAP,
):
    combined_data = []
    current_sentence = ""
    current_video_id = raw_data[0]["video_id"] if raw_data else None
    current_start = raw_data[0]["start"] if raw_data else None
    current_end = raw_data[0]["end"] if raw_data else None
    num_sentences = 0
    num_tokens = 0
    overlap_buffer = ""

    for record in raw_data:
        cleaned_content = record["page_content"].replace("\n", " ")
        token_count = tokenizer.count_tokens(cleaned_content)

        if num_tokens + token_count > MAX_NUM_TOKENS:
            combined_data.append(
                {
                    "page_content": current_sentence,
                    "start": current_start,
                    "end": current_end,
                    "video_id": current_video_id,
                }
            )
            current_sentence = overlap_buffer + cleaned_content
            current_start = record["start"]
            current_end = record["end"]
            current_video_id = record["video_id"]
            num_sentences = 1
            num_tokens = token_count
        else:
            current_sentence += " " + cleaned_content
            current_end = record["end"]
            num_sentences += 1
            num_tokens += token_count

        # Update overlap buffer
        overlap_buffer = " ".join(current_sentence.split()[-CHUNK_OVERLAP:])

    if current_sentence:
        combined_data.append(
            {
                "page_content": current_sentence,
                "start": current_start,
                "end": current_end,
                "video_id": current_video_id,
            }
        )

    return combined_data
