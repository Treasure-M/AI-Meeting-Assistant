# Use current Debian stable
FROM python:3.11-bookworm

# Install system dependencies with retry logic
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Set explicit FFmpeg path
ENV PATH="/usr/bin/ffmpeg:${PATH}"

# Run the app
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]
