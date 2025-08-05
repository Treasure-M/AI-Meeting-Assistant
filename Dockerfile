# Use Python with full Debian packages
FROM python:3.9-bullseye

# Install system dependencies with retry logic
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Alternative audio backend if portaudio fails
RUN pip install soundfile>=0.12.1

WORKDIR /app

# First copy only requirements to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Configure pydub to use installed ffmpeg
ENV PATH="/usr/bin/ffmpeg:${PATH}"

# Health check
HEALTHCHECK --interval=30s --timeout=30s \
    CMD python -c "import requests; requests.get('http://localhost:10000/health', timeout=5)" || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:10000", "--workers", "2", "app:app"]
