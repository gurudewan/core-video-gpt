from openai import OpenAI
import app.helpers.tokenizer as tokenizer
from app.consts import consts


client = OpenAI(api_key=consts().OPENAI_API_KEY)


def chat(conversation, docs, video_metadata):
    sources = [doc.page_content for doc in docs]

    # print(sources)

    messages = []

    if conversation[0].role != "system":
        messages = [
            {"role": "system", "content": consts().QA_SYSTEM_PROMPT},
        ]

    for message in conversation[:-1]:  # Add all but the last message
        messages.append(message.dict())

    # Format the last message to include the relevant sources
    last_message = conversation[-1]

    video_message = []
    video_message.append(last_message.content)
    video_message.append(f"The title of the video is {video_metadata['title']}. ")

    if len(sources) == 0:
        video_message.append(f"A summary of the video is {video_metadata['summary']}")
    else:
        video_message.append(
            "The relevant parts of the video are: " + " ".join(sources)
        )

    messages.append({"role": "user", "content": " ".join(video_message)})

    response = client.chat.completions.create(
        model=consts().OPENAI_MODEL, messages=messages
    )

    answer = response.choices[0].message.content

    return answer


def grand_summarise(key_frames_summary, transcript_summary):
    messages = [
        {"role": "system", "content": consts().GRAND_SUMMARY_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"The summary of the transcript is: {transcript_summary} and the summary of the key frames is {key_frames_summary}.",
        },
    ]
    response = client.chat.completions.create(
        model=consts().OPENAI_MODEL,
        messages=messages,
        max_tokens=consts().MAX_TOKENS_FOR_SUMMARIES_OUTPUT,
    )
    return response.choices[0].message.content


def summarise(text, info):
    token_count = tokenizer.count_tokens(text)
    if token_count <= consts().BATCH_SIZE_FOR_BATCHED_SUMMARIES_INPUT:
        messages = [
            {"role": "system", "content": consts().SUMMARISE_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Use this info in your summary to contextualise. The title is {info['title']}. The description is {info['description']}. The uploader of the video is {info['author_name']}. The tags are {', '.join(info['tags'])}",
            },
            {
                "role": "assistant",
                "content": f"Next give me the text to summarise, and I'll give you the summary directly.",
            },
            {"role": "user", "content": f"{text}"},
        ]
        response = client.chat.completions.create(
            model=consts().OPENAI_MODEL,
            messages=messages,
            max_tokens=consts().MAX_TOKENS_FOR_SUMMARIES_OUTPUT,
        )
        return response.choices[0].message.content
    else:
        batches = batch_text(text)
        summaries = []
        for batch in batches:
            print(f"batch has size {tokenizer.count_tokens(batch)}")
            messages = [
                {"role": "system", "content": consts().SUMMARISE_SYSTEM_PROMPT},
                {"role": "user", "content": f"{batch}"},
            ]
            response = client.chat.completions.create(
                model=consts().OPENAI_MODEL,
                messages=messages,
                max_tokens=consts().MAX_TOKENS_FOR_SUMMARIES_OUTPUT
                - 50,  # smaller max tokens for this version
            )
            summaries.append(response.choices[0].message.content)

        # Summarize the list of summaries
        summaries_text = " ".join(summaries)
        messages = [
            {"role": "system", "content": consts().SUMMARISE_SYSTEM_PROMPT},
            {"role": "user", "content": summaries_text},
        ]
        response = client.chat.completions.create(
            model=consts().OPENAI_MODEL,
            messages=messages,
            max_tokens=consts().MAX_TOKENS_FOR_SUMMARIES_OUTPUT,
        )
        return response.choices[0].message.content


def clean_up_description(text):
    token_count = tokenizer.count_tokens(text)
    if token_count <= consts().BATCH_SIZE_FOR_BATCHED_SUMMARIES_INPUT:
        messages = [
            {"role": "system", "content": consts().CLEANUP_DESCRIPTION_SYSTEM_PROMPT},
            {"role": "user", "content": f"{text}"},
        ]
        response = client.chat.completions.create(
            model=consts().OPENAI_MODEL,
            messages=messages,
            max_tokens=consts().MAX_TOKENS_FOR_DESCRIPTIONS_OUTPUT,
        )
        return response.choices[0].message.content
    else:
        batches = batch_text(text)
        descs = []
        for batch in batches:
            messages = [
                {
                    "role": "system",
                    "content": consts().CLEANUP_DESCRIPTION_SYSTEM_PROMPT,
                },
                {"role": "user", "content": f"{batch}"},
            ]
            response = client.chat.completions.create(
                model=consts().OPENAI_MODEL,
                messages=messages,
                max_tokens=consts().MAX_TOKENS_FOR_DESCRIPTIONS_OUTPUT
                - 50,  # smaller max tokens for this version
            )
            descs.append(response.choices[0].message.content)

        # Summarize the list of summaries
        descriptions_text = " ".join(descs)
        messages = [
            {"role": "system", "content": consts().CLEANUP_DESCRIPTION_SYSTEM_PROMPT},
            {"role": "user", "content": descriptions_text},
        ]
        response = client.chat.completions.create(
            model=consts().OPENAI_MODEL,
            messages=messages,
            max_tokens=consts().MAX_TOKENS_FOR_DESCRIPTIONS_OUTPUT,
        )
        return response.choices[0].message.content


def batch_text(text, max_tokens=consts().BATCH_SIZE_FOR_BATCHED_SUMMARIES_INPUT):
    words = text.split()
    batches = []
    current_batch = []
    current_count = 0

    for word in words:
        word_count = tokenizer.count_tokens(
            word, model=consts().OPENAI_MODEL_FOR_SUMMARIES
        )
        if current_count + word_count > max_tokens:
            batches.append(" ".join(current_batch))
            current_batch = [word]
            current_count = word_count
        else:
            current_batch.append(word)
            current_count += word_count

    if current_batch:
        batches.append(" ".join(current_batch))

    return batches


if __name__ == "__main__":
    import test_data.test_text as test_text

    # text = test_text.pg_long_essay_66K_chars_16K_tokens
    text = test_text.SADHGURU_TRANSCRIPT
    summary = summarise(text)
    print(summary)
