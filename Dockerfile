FROM python:3.10-slim

# Set environment
ENV PYTHONUNBUFFERED=1

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    ffmpeg \
    libnss3 \
    libatk-bridge2.0-0 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libgtk-3-0 \
    libasound2 \
    libxshmfence1 \
    libxss1 \
    libnss3-tools \
    libatk1.0-0 \
    libcups2 \
    libdrm2 \
    libxext6 \
    fonts-liberation \
    libappindicator3-1 \
    libjpeg-dev \
    git \
    build-essential

# Install pip packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright and its dependencies
RUN pip install playwright
RUN playwright install --with-deps

# Add code
COPY . /app
WORKDIR /app

# Set the startup command
CMD ["python", "main.py"]
