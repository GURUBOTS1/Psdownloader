FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

# Set environment
ENV PYTHONUNBUFFERED=1

# Install FFmpeg (for video merging)
RUN apt-get update && apt-get install -y ffmpeg

# Set work directory
WORKDIR /app

# Copy all project files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run your bot
CMD ["python", "main.py"]
