import asyncio
from pathlib import Path

from loguru import logger

from .control import Control
from downloader.utils import Timer

ALBUM_URL = "https://jsonplaceholder.typicode.com/albums/"
PHOTOS_URL = "https://jsonplaceholder.typicode.com/photos/"
FOLDER = Path("albums")


# def main():
#     t = Timer.start()
#     logger.info("Запуск async_1")
#     downloader = Control(albums_url=ALBUM_URL, photos_url=PHOTOS_URL, folder=FOLDER)
#     downloader.run()
#     time_delta = t.stop()
#     logger.info(f"Загрузка завершена за {time_delta}")


async def main():
    t = Timer.start()
    logger.info("Запуск async_2")
    downloader = Control(albums_url=ALBUM_URL, photos_url=PHOTOS_URL, folder=FOLDER)
    await downloader.async_run()
    time_delta = t.stop()
    logger.info(f"Загрузка завершена за {time_delta}")


# if __name__ == "__main__":=
# main()
asyncio.run(main())
