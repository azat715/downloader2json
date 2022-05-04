# syntax = docker/dockerfile:1.3
FROM python:3.9.7-alpine

RUN apk update 

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV LOGURU_LEVEL INFO
RUN mkdir /code
WORKDIR /code
COPY dist/downloader-0.2.0.tar.gz /code/
RUN --mount=type=cache,target=/root/.cache \
    python3 -m pip install -U downloader-0.2.0.tar.gz --no-cache-dir
ENTRYPOINT ["downloader"] 