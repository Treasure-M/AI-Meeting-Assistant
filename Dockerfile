# Use official Python base image
FROM python:3.9-slim-buster

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    ffmpeg \
    python3-dev \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Explicitly set FFmpeg path for pydub
ENV PATH="/usr/bin/ffmpeg:${PATH}"

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]
