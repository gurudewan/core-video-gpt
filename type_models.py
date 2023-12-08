from pydantic import BaseModel
from typing import List, Tuple

Period = Tuple[float, float]


class ViewedImage(BaseModel):
    group_id: int
    image_url: str
    caption: str
    short_caption: str
    periods: List[Period]

    def model_dump(self, **kwargs):
        return {
            "group_id": self.group_id,
            "image_url": self.image_url,
            "caption": self.caption,
            "short_caption": self.short_caption,
            "periods": [list(period) for period in self.periods],
        }

    def __getitem__(self, item):
        return getattr(self, item)


class ViewedVideo(BaseModel):
    viewed_images: List[ViewedImage]

    def model_dump(self, **kwargs):
        return {
            "viewed_images": [image.model_dump() for image in self.viewed_images],
        }

    def __getitem__(self, item):
        return getattr(self, item)
