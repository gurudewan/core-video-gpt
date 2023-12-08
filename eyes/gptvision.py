import asyncio
from openai import OpenAI
import random

from type_models import ViewedImage

# import fake_captions
import eyes.fake_captions as fake_captions

semaphore = asyncio.Semaphore(10)  # 10 requests per second
client = OpenAI()

import consts


async def caption_image(image, info):
    output = None
    async with semaphore:
        try:
            # TODO do some prompt engineering here
            # add a system prompt
            # get the title, description and the transcript summary from the video
            response = client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that describes videos. I will give you the video's title a summary of the transcript, and attach a key scene from the video. You give me a description of the key scene. Describe the image in full detail, and use the title and summaries to contextualise the image, e.g. find people or things mentioned in the summary that are likely in this key scene. Be concise and direct in your explanations, and try to capture everything.",
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"The key scene is attached. The video is titled '{info['title']}' and the author is '{info['author_name']}'. The summary of the transcript is: {info['summary']}. ",
                            },
                            {"type": "image_url", "image_url": image["image_url"]},
                        ],
                    },
                ],
                max_tokens=300,
            )
            output = response.choices[0].message.content
            print("-----")
            print(image["image_url"])
            print(output)
            print("======")
        except Exception as e:
            if "rate_limit_exceeded" in str(e):
                print(f"Rate limit exceeded while processing {image['image_url']}: {e}")
                wait_time = 60  # wait for 60 seconds
                await asyncio.sleep(wait_time)
            print(f"Error occurred while processing {image['image_url']}: {e}")

    result = {
        "group_id": image["group_id"],
        "image_url": image["image_url"],
        "caption": output,
        "periods": image["periods"],
    }
    return result


async def async_batch_caption_images(images, info):
    if consts.DO_FAKE_GPT_CALLS:
        results = [
            ViewedImage(
                group_id=image["group_id"],
                image_url=image["image_url"],
                caption=random.choice(fake_captions.long),
                short_caption=random.choice(fake_captions.short),
                periods=image["periods"],
            )
            for image in images
        ]

    tasks = [caption_image(image, info) for image in images]
    results = await asyncio.gather(*tasks)
    return results


async def test():
    url = "https://storage.googleapis.com/video-gpt-prod-files//tmp/youtube/xyrZjl1bL6I/key_frames/10.jpg"

    images = {"image_url": url, "group_id": "test", "periods": ""}

    await caption_image(images, fake_captions.info)


async def test_batch():
    url = "https://storage.googleapis.com/video-gpt-prod-files//tmp/youtube/xyrZjl1bL6I/key_frames/10.jpg"

    base_url = "https://storage.googleapis.com/video-gpt-prod-files//tmp/youtube/xyrZjl1bL6I/key_frames/"
    group_id = "test"
    periods = ""

    images = [
        {"image_url": f"{base_url}{i}.jpg", "group_id": group_id, "periods": periods}
        for i in range(1, 15)
    ]

    await async_batch_caption_images(images)


if __name__ == "__main__":
    asyncio.run(test_batch())
