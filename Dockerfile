# Use official Python base image
FROM python:3.10-slim

# Install FFmpeg and system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    git \
    && apt-get clean

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port used by the bot (Koyeb)
EXPOSE 8080

# Start the bot with webhook
CMD ["python", "main.py"]
