# syntax = docker/dockerfile:1.3
FROM python:3.9.7-alpine

RUN apk update 

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV LOGURU_LEVEL INFO
ENV PYTHONPATH="/code/downloader:$PYTHONPATH"
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN --mount=type=cache,target=/root/.cache \
    python3 -m pip install -r requirements.txt --no-cache-dir
COPY . /code/
CMD ["python3", "-m", "downloader"]