# Use Python 3.9 with full Debian packages
FROM python:3.9-bullseye

# Install system dependencies with clean up in one RUN layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    python3-dev \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# First copy only requirements to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set explicit paths for audio processing
ENV PATH="/usr/bin/ffmpeg:${PATH}"
ENV PYTHONPATH="/app:${PYTHONPATH}"

# Health check (optional but recommended)
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:10000/health || exit 1

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "--workers", "4", "app:app"]
