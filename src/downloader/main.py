"""Main"""
import asyncio
from itertools import chain
from pathlib import Path
from typing import List, Dict

import aiofiles
import aiohttp
from aiofiles import os
from aiohttp import ClientSession
from loguru import logger
from pydantic import parse_obj_as

from downloader.models import Album, Photo, PhotoTask

ALBUM_URL = "https://jsonplaceholder.typicode.com/albums/"
PHOTOS_URL = "https://jsonplaceholder.typicode.com/photos/"
PHOTO_EXT = ".png"
WORKERS = 100


async def fetch_json(url: str, session: ClientSession) -> str:
    """Download by url

    Args:
        url: str
        session: Aiohttp ClientSession

    Returns:
        json

    """
    async with session.get(url) as response:
        return await response.json()


async def fetch_raw(url: str, session: ClientSession) -> bytes:
    """Download by url

    Args:
        url: str
        session: Aiohttp ClientSession

    Returns:
        bytes

    """

    async with session.get(url) as response:
        return await response.read()


async def create_folder(path: Path):
    """Create folder

    Args:
        path: str

    """
    try:
        await os.mkdir(path)
    except FileExistsError:
        pass


async def save_file(path: Path, raw: bytes):
    """Save file

    Args:
        path: Path file
        raw: bytes

    """
    async with aiofiles.open(path, mode="wb") as file:
        await file.write(raw)


async def get_albums(url: str, session: ClientSession) -> Dict[int, Album]:
    """Download albums

    Args:
        url: str
        session: Aiohttp ClientSession

    Returns:
        key - Album.id, value - Album

    """
    data = await fetch_json(url, session)
    albums = {}

    album: Album
    for album in parse_obj_as(List[Album], data):
        albums[album.id_] = album

    logger.debug("загружено albums_json")
    return albums


async def get_photos(url: str, session: ClientSession) -> List[Photo]:
    """Download photos

    Args:
        url: str
        session: Aiohttp ClientSession

    Returns:
        List Photo

    """
    data = await fetch_json(url, session)
    logger.debug("загружено photos_json")
    return parse_obj_as(List[Photo], data)


async def get_photo(session: ClientSession, tasks: asyncio.Queue, res: asyncio.Queue):
    """Worker get photo raw

    Args:
        session: Aiohttp ClientSession
        tasks: Queue PhotoTask
        res: Queue PhotoTask(with raw photo)

    """
    while True:
        photo: PhotoTask = await tasks.get()

        data = await fetch_raw(photo.url, session)
        await res.put(photo._replace(raw=data))

        logger.debug(f"загружено {photo.url}")
        tasks.task_done()


async def save_photo(tasks: asyncio.Queue):
    """Worker save photo

    Args:
        tasks: Queue PhotoTask(with raw photo)

    """
    while True:
        photo: PhotoTask = await tasks.get()
        album_path = photo.path / photo.album_title
        file_name = album_path.joinpath(photo.title).with_suffix(PHOTO_EXT)

        await create_folder(album_path)
        if photo.raw:
            await save_file(file_name, photo.raw)
        else:
            raise Exception("Incorrect Photo Task")

        logger.debug(f"записано {file_name}")
        tasks.task_done()


async def load_photos(session: ClientSession, get_photo_queue: asyncio.Queue, save_photo_queue: asyncio.Queue):
    """Create workers

    Args:
        session: Aiohttp ClientSession
        get_photo_queue: Queue PhotoTask
        save_photo_queue: Queue PhotoTask(with raw photo)

    Returns:

    """
    tasks_get_photo = []
    for _ in range(WORKERS):
        task = asyncio.create_task(get_photo(session, get_photo_queue, save_photo_queue))
        tasks_get_photo.append(task)
    return tasks_get_photo


async def save_photos(save_photo_queue: asyncio.Queue):
    """Create workers

    Args:
        save_photo_queue: Queue PhotoTask(with raw photo)

    """
    tasks_save_photo = []
    for _ in range(WORKERS):
        task = asyncio.create_task(save_photo(save_photo_queue))
        tasks_save_photo.append(task)
    return tasks_save_photo


async def download(folder: str):  # pylint: disable=missing-function-docstring
    logger.info("Запуск")
    folder_path = Path(folder)
    await create_folder(folder_path)

    # очереди
    get_photo_queue = asyncio.Queue()
    save_photo_queue = asyncio.Queue()

    async with aiohttp.ClientSession() as session:
        albums = await get_albums(ALBUM_URL, session)
        photos = await get_photos(PHOTOS_URL, session)

        photo: Photo
        for photo in photos:
            await get_photo_queue.put(PhotoTask(
                url=photo.url,
                album_title=albums[photo.albumId].title,
                title=photo.title,
                path=folder_path,
            ))

        task1 = asyncio.create_task(
            load_photos(session, get_photo_queue, save_photo_queue)
        )
        task2 = asyncio.create_task(save_photos(save_photo_queue))

        tasks_get_photo = await task1
        tasks_save_photo = await task2

        await get_photo_queue.join()
        await save_photo_queue.join()

    for task in chain(tasks_get_photo, tasks_save_photo):
        task.cancel()

    await asyncio.gather(*tasks_get_photo, return_exceptions=True)
    await asyncio.gather(*tasks_get_photo, return_exceptions=True)
    logger.info("Загружено")


def main():  # pylint: disable=missing-function-docstring
    asyncio.run(download())
