import asyncio
import replicate
import aiohttp

semaphore = asyncio.Semaphore(10)  # 10 requests per second


async def caption_image(image):
    async with semaphore:
        try:
            output = replicate.run(
                "yorickvp/llava-13b:2cfef05a8e8e648f6e92ddb53fa21a81c04ab2c4f1390a6528cc4e331d608df8",
                input={
                    "image": image["image_url"],
                    "prompt": "Describe this image in full. Extract any text from it exactly.",
                },
            )
            print("-----")
            print(image["image_url"])
            print(output)
            print("======")
        except Exception as e:
            print(f"Error occurred while processing {image['image_url']}: {e}")

        result = {
            "group_id": image["group_id"],
            "image_url": image["image_url"],
            "caption": output,
            "periods": image["periods"],
        }
        return result


async def async_batch_caption_images(images):
    async with aiohttp.ClientSession() as session:
        tasks = [caption_image(image) for image in images]
        results = await asyncio.gather(*tasks)
        return results


async def warm_up_ai():
    dummy_image = {
        "group_id": "dummy_group",
        "image_url": "https://pbxt.replicate.delivery/JfvBi04QfleIeJ3ASiBEMbJvhTQKWKLjKaajEbuhO1Y0wPHd/view.jpg",
        "periods": [],
    }
    await caption_image(dummy_image)
