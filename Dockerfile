FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY *.py ./
COPY chapter.txt ./

# Create directories
RUN mkdir -p models output examples

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Default command
CMD ["python", "main.py"]

# Usage:
# docker build -t manhwa-generator .
# docker run -v $(pwd)/models:/app/models -v $(pwd)/output:/app/output manhwa-generator
#
# For GPU support:
# docker run --gpus all -v $(pwd)/models:/app/models -v $(pwd)/output:/app/output manhwa-generator
