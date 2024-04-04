def extract_highlights(docs):
    transcript_highlights = extract_transcript_highlights(docs)

    image_highlights = extract_image_highlights(docs)

    return {
        "transcript_highlights": transcript_highlights,
        "image_highlights": image_highlights,
    }


def extract_transcript_highlights(docs):
    transcript_highlights = [
        (doc.metadata.get("start"), doc.metadata.get("end"))
        for doc in docs
        if doc.metadata.get("type") == "transcript"
        and doc.metadata.get("start") is not None
        and doc.metadata.get("end") is not None
    ]

    transcript_highlights.sort(key=lambda x: x[0])

    transcript_highlights = remove_smaller_intervals(transcript_highlights)

    return transcript_highlights


def extract_image_highlights(docs):
    # Extract image_url, periods, and group_id from docs where type is 'gpt-4V-captions'
    image_highlights = [
        {
            "image_url": doc.metadata.get("image_url"),
            "periods": doc.metadata.get("periods"),
            "group_id": doc.metadata.get("group_id"),
        }
        for doc in docs
        if doc.metadata.get("type") == "gpt-4V-captions"  # llava-captions
    ]

    return image_highlights


def remove_smaller_intervals(transcript_highlights):
    i = 0
    while i < len(transcript_highlights) - 1:
        if transcript_highlights[i][0] == transcript_highlights[i + 1][0]:
            if (transcript_highlights[i][1] - transcript_highlights[i][0]) < (
                transcript_highlights[i + 1][1] - transcript_highlights[i + 1][0]
            ):
                transcript_highlights.pop(i)
            else:
                transcript_highlights.pop(i + 1)
        else:
            i += 1
    return transcript_highlights
