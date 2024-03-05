# core-video-chat/Dockerfile

# ====================== INITIALISE

FROM python:3.11
#FROM hdgigante/python-opencv:4.8.1-debian	

# ====================== DOWNLOAD REQUIREMENTS

WORKDIR /usr/src/app

COPY requirements.txt ./

#RUN pip install --no-cache-dir -r requirements.txt

RUN pip install -r requirements.txt && rm -rf /root/.cache/pip

# ====================== DOWNLOAD FFMPEG

RUN apt-get update && apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Ensure ffmpeg is in the PATH
ENV PATH="/usr/bin:${PATH}"

# Debugging commands
#RUN yt-dlp --verbose
#RUN ffmpeg --version
RUN whereis ffmpeg
#RUN whereis libgl1

# set the place for clip / torch cache to be stored
# ENV TORCH_HOME=/usr/src/app/torch_cache
#RUN python -c "import clip; model, preprocess = clip.load('ViT-B/32', download_root='/usr/src/app/torch_cache')"
#RUN ls -la /usr/src/app/torch_cache && find /usr/src/app/torch_cache -name 'ViT-B/32'

# ====================== DEBUG: DOUBLE DOWNLOAD opency-python-headless
# TODO delete this
#RUN python -m pip install opencv-python-headless

#RUN python -c "import cv2; print(cv2.__version__)"

# ====================== COPY OVER APP

COPY . .

# Print the contents of the keys directory
#RUN echo "Listing directory contents:" && ls -la
#3RUN ls -la /usr/src/app/keys
#RUN cat /usr/src/app/keys/storage-manager-keys-prod.json
#RUN echo "Full path to the file:" && pwd && echo "/usr/src/app/keys/storage-manager-keys-prod.json"
#RUN find / -name storage-manager-keys-prod.json
# Print the contents of the storage-manager-keys.json file
#RUN cat /usr/src/app/keys/storage-manager-keys.json


ENV GOOGLE_APPLICATION_CREDENTIALS="keys/storage-manager-keys-prod.json"
ENV FIREBASE_CREDENTIALS="keys/firebase-keys-prod.json"

# ====================== FINISH

ENTRYPOINT uvicorn main:app --host 0.0.0.0 --port $PORT