import fire
import asyncio
from pathlib import Path

from loguru import logger

from .control import Control
from downloader.utils import Timer

ALBUM_URL = "https://jsonplaceholder.typicode.com/albums/"
PHOTOS_URL = "https://jsonplaceholder.typicode.com/photos/"
FOLDER = Path("albums")


def async_1():
    """run multithreading download"""
    t = Timer.start()
    logger.info("Запуск async_1")
    downloader = Control(albums_url=ALBUM_URL, photos_url=PHOTOS_URL, folder=FOLDER)
    downloader.run()
    time_delta = t.stop()
    logger.info(f"Загрузка завершена за {time_delta}")


async def async_2():
    t = Timer.start()
    logger.info("Запуск async_2")
    downloader = Control(albums_url=ALBUM_URL, photos_url=PHOTOS_URL, folder=FOLDER)
    await downloader.async_run()
    time_delta = t.stop()
    logger.info(f"Загрузка завершена за {time_delta}")


def run_async_2():
    """run async download"""
    asyncio.run(async_2())

def main():
    fire.Fire({
        'async_1': async_1,
        'async_2': run_async_2,
    })
