FROM python:3.12-slim AS base

RUN apt-get update && apt-get install -y \
    xvfb \
    wget \
    curl \
    fonts-liberation \
    libnss3 \
    libatk-bridge2.0-0 \
    libxss1 \
    libasound2 \
    libxshmfence-dev \
    libx11-xcb1 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

FROM base AS dependencies

COPY requirements.txt .

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

RUN --mount=type=cache,target=/root/.cache/ms-playwright \
    playwright install --with-deps

FROM dependencies AS application

WORKDIR /app

COPY . .

RUN mkdir -p /app/data/iptv/original /app/data/iptv/processed /app/logs

EXPOSE 5000

CMD xvfb-run --auto-servernum --server-args='-screen 0 1280x720x24' \
    uvicorn main:app --host 0.0.0.0 --port 5000