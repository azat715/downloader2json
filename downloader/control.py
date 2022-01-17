import asyncio
import concurrent.futures
from itertools import repeat
from pathlib import Path
from typing import List, Dict
from aiofile import async_open

from loguru import logger

from .base import DownloadCenter
from .async_1 import AlbumJson, PhotoJson, PhotoBinary
from .async_2 import AsyncAlbumJson, AsyncPhotoJson, AsyncPhotoBinary
from .models import Album, Photo, PhotoTask
from .utils import logger_wraps


class Control:
    STRATEGY = {
        "albums": DownloadCenter(AlbumJson()),
        "photos": DownloadCenter(PhotoJson()),
        "photo_binary": DownloadCenter(PhotoBinary()),
        "async_albums": DownloadCenter(AsyncAlbumJson()),
        "async_photos": DownloadCenter(AsyncPhotoJson()),
        "async_photo_binary": DownloadCenter(AsyncPhotoBinary()),
    }

    def __init__(self, albums_url: str, photos_url: str, folder: str) -> None:
        self.albums_url = albums_url
        self.photos_url = photos_url
        self.folder = Path(folder)

    def create_folder(self):
        self.folder.mkdir(exist_ok=True)

    @logger_wraps(logger)
    def download(self, url: str, worker: DownloadCenter):
        return worker.download(url)

    async def async_download(self, url: str, worker: DownloadCenter, queue=None):
        """в воркер передаю очередь"""
        res = await worker.download(url)
        if queue:
            queue.task_done()  #  передаю сигнал завершения таски
        return res

    def run(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            albums_future = executor.submit(
                self.download, self.albums_url, self.STRATEGY["albums"]
            )
            photos_future = executor.submit(
                self.download, self.photos_url, self.STRATEGY["photos"]
            )

            albums_json: Dict[int, Album] = albums_future.result()
            logger.debug("загружено albums_json")
            photos_json: List[Photo] = photos_future.result()
            logger.debug("загружено photos_json")

            photos_url: List[str] = [i.url for i in photos_json]
            result = executor.map(
                self.download, photos_url, repeat(self.STRATEGY["photo_binary"])
            )
        logger.debug("загружены фотки")

        self.create_folder()

        file: bytes
        for photo, file in zip(photos_json, result):
            album = albums_json[photo.albumId]
            album_path = self.folder / album.title
            album_path.mkdir(exist_ok=True)

            # folder/<album.title>/<photo.title>.png
            path = (album_path / photo.title).with_suffix(".png")
            path.write_bytes(file)

    async def worker(self, queue):
        while True:
            try:
                # Wait for 1 hour
                # Get a "work item" out of the queue.
                task: PhotoTask = await queue.get()
                photo: Photo = task.photo
                album: Album = task.album

                file: bytes = await self.async_download(
                    photo.url, self.STRATEGY["async_photo_binary"]
                )
                logger.debug(f"загружено {photo.url}")
                album_path = self.folder / album.title
                album_path.mkdir(exist_ok=True)

                # folder/<album.title>/<photo.title>.png
                path = (album_path / photo.title).with_suffix(".png")
                async with async_open(path, "wb") as f:
                    await f.write(file)
                logger.debug(f"Сохранено {path}")
                queue.task_done()

            except asyncio.CancelledError:
                break

    async def async_run(self):
        self.create_folder()
        albums_json: Dict[int, Album] = await self.async_download(
            self.albums_url, self.STRATEGY["async_albums"]
        )
        logger.debug("загружено albums_json")
        photos_json: List[Photo] = await self.async_download(
            self.photos_url, self.STRATEGY["async_photos"]
        )
        logger.debug("загружено photos_json")
        queue = asyncio.Queue()

        for photo in photos_json:
            album = albums_json[photo.albumId]
            task = PhotoTask(photo=photo, album=album)
            await queue.put(task)

        workers = []
        for i in range(100):
            worker = asyncio.create_task(self.worker(queue))
            workers.append(worker)

        await queue.join()

        # останавливаю воркеров
        for worker in workers:
            worker.cancel()

        result = await asyncio.gather(*workers, return_exceptions=True)
        logger.debug("загружены фотки")

        for res in result:
            if isinstance(res, Exception):
                print(f"Unexpected exception: {result}")
                raise Exception("Error")
