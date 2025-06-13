FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY . /app

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright Browsers (VERY IMPORTANT)
RUN playwright install --with-deps

CMD ["python", "main.py"]
