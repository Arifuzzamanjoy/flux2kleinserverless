# Use RunPod base image with CUDA support
FROM runpod/base:0.6.3-cuda12.1.0

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV HF_HOME=/runpod-volume/.cache/huggingface
ENV TRANSFORMERS_CACHE=/runpod-volume/.cache/huggingface
ENV TORCH_HOME=/runpod-volume/.cache/torch

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip for Python 3.11
RUN python3.11 -m pip install --upgrade pip

# Copy and install Python dependencies
COPY requirements.txt /requirements.txt
RUN python3.11 -m pip install --no-cache-dir -r /requirements.txt && \
    python3.11 -m pip install --no-cache-dir git+https://github.com/huggingface/diffusers.git

# Copy handler
COPY handler.py /handler.py

# Pre-download the model (optional - comment out if using network volumes)
# This bakes the model into the image for faster cold starts
# RUN python3.11 -c "from diffusers import Flux2KleinPipeline; Flux2KleinPipeline.from_pretrained('black-forest-labs/FLUX.2-klein-4B')"

# Start the handler
CMD ["python3.11", "-u", "/handler.py"]
