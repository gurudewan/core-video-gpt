import cv2
import numpy as np
import torch
import clip

# Load the clip model
model, preprocess = clip.load("ViT-B/32")


def get_image_embeddings(frame):
    # Convert the image from BGR to RGB
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Normalize the image to [0,1]
    frame = frame / 255.0

    # Resize the image to the size expected by the clip model
    frame = cv2.resize(frame, (224, 224))

    # Convert the image to a PyTorch tensor and add a batch dimension
    frame = torch.from_numpy(frame).permute(2, 0, 1).unsqueeze(0).float()

    # Preprocess the image
    frame = preprocess(frame)

    # Calculate the embeddings
    with torch.no_grad():
        embeddings = model.encode_image(frame)

    return embeddings
