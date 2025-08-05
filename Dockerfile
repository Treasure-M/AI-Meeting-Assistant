# Use current stable Debian version
FROM python:3.9-bookworm

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Alternative audio backend (no portaudio needed)
RUN pip install soundfile>=0.12.1

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Configure pydub
ENV PATH="/usr/bin/ffmpeg:${PATH}"

CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]
