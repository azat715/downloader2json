import asyncio
from pathlib import Path
from typing import List, Any
from itertools import chain

import aiofiles
import aiohttp
import fire
from aiofiles import os
from aiohttp import ClientSession
from loguru import logger
from pydantic import parse_obj_as

from downloader.models import Album, Photo, PhotoTask

ALBUM_URL = "https://jsonplaceholder.typicode.com/albums/"
PHOTOS_URL = "https://jsonplaceholder.typicode.com/photos/"
FOLDER = Path("albums")
PHOTO_EXT = ".png"
WORKERS = 100

async def fetch_json(session: ClientSession, url: str):
    async with session.get(url) as response:
        return await response.json()

async def fetch_raw(session: ClientSession, url: str):
    async with session.get(url) as response:
        return await response.read()

def parser(model, data: str) -> List[Any]:
    return parse_obj_as(List[model], data)

async def create_folder(path: Path):
    try:
        await os.mkdir(path)
    except FileExistsError:
        pass

async def save_file(path: Path, raw: bytes):
    async with aiofiles.open(path, mode="wb") as f:
        await f.write(raw)

async def get_albums(session: ClientSession):
    data = await fetch_json(session, ALBUM_URL)
    res = {}
    i: Album
    for i in parser(Album, data):
        res[i.id_] = i
    logger.debug("загружено albums_json")
    return res

async def get_photos(session: ClientSession):
    data = await fetch_json(session, PHOTOS_URL)
    logger.debug("загружено photos_json")
    return parser(Photo, data)

### воркеры

async def get_photo(session: ClientSession, photos: asyncio.Queue, res: asyncio.Queue):
    while True:
        photo: PhotoTask = await photos.get()
        data = await fetch_raw(session, photo.url)
        photo = photo._replace(raw=data)
        await res.put(photo)
        logger.debug(f"загружено {photo.url}")
        photos.task_done()

async def save_photo(photos: asyncio.Queue):
    while True:
        photo: PhotoTask = await photos.get()
        album_path = FOLDER / photo.album_title
        await create_folder(album_path)
        file_name = album_path.joinpath(photo.title).with_suffix(PHOTO_EXT)
        await save_file(file_name, photo.raw)
        logger.debug(f"записано {file_name}")
        photos.task_done()

###
### запуск воркеров

async def load_photos(albums, photos, session, get_photo_queue, save_photo_queue):
    photo: Photo
    for photo in photos:
        problem = PhotoTask(
            url=photo.url,
            album_title=albums[photo.albumId].title,
            title=photo.title
        )
        await get_photo_queue.put(problem)

    tasks_get_photo = []
    for _ in range(WORKERS):
        task = asyncio.create_task(get_photo(session, get_photo_queue, save_photo_queue))
        tasks_get_photo.append(task)
    return tasks_get_photo

async def save_photos(save_photo_queue):
    tasks_save_photo = []
    for _ in range(WORKERS):
        task = asyncio.create_task(save_photo(save_photo_queue))
        tasks_save_photo.append(task)
    return tasks_save_photo

###

async def run():
    logger.info("Запуск")
    await create_folder(FOLDER)

    # очереди
    get_photo_queue = asyncio.Queue()
    save_photo_queue = asyncio.Queue()

    async with aiohttp.ClientSession() as session:
        albums = await get_albums(session)
        photos = await get_photos(session)
        task1 = asyncio.create_task(
            load_photos(albums, photos, session, get_photo_queue, save_photo_queue)
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

def main():
    fire.Fire(asyncio.run(run()))

