import asyncio
from os import environ

from downloader.main import download

FOLDER = environ.get("FOLDER")

asyncio.run(download(FOLDER))
