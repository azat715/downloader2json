import concurrent.futures
from concurrent.futures import wait
from abc import ABC, abstractmethod
from itertools import repeat
from pathlib import Path
from typing import Any, Dict, List

from loguru import logger

from .models import Album, Photo, PhotoTask
from .utils import Get, Serializer, Timer, logger_wraps

ALBUM_URL = "https://jsonplaceholder.typicode.com/albums/"
PHOTOS_URL = "https://jsonplaceholder.typicode.com/photos/"
FOLDER = Path("albums")


class BaseDownloader(ABC):
    """абстрактный класс стратегии загрузки"""

    downloader = Get()
    serializer: Serializer

    def serialize(self, data: List[dict], many=False):
        return self.serializer.serialize(data, many=many)

    @abstractmethod
    def get_result(self, url: str) -> Any:
        pass


class AlbumJson(BaseDownloader):
    serializer = Serializer(Album)

    def get_result(self, url: str) -> Dict[int, Album]:
        res = {}
        for i in self.downloader.get_json(url):
            album: Album = self.serialize(i)
            if album.id_ in res:
                raise Exception("Альбом с id {album.id_} уже существует")
            res[album.id_] = album
        return res


class PhotoJson(BaseDownloader):
    serializer = Serializer(Photo)

    def get_result(self, url: str) -> List[Photo]:
        data = self.downloader.get_json(url)
        return self.serialize(data, many=True)


class PhotoBinary(BaseDownloader):
    def get_result(self, url: str) -> bytes:
        return self.downloader.get_bytes(url)


class DownloadCenter:
    def __init__(self, downloader: BaseDownloader) -> None:
        """ """
        self._downloader = downloader

    @property
    def downloader(self) -> BaseDownloader:
        return self._downloader

    @downloader.setter
    def downloader(self, downloader: BaseDownloader) -> None:
        self._downloader = downloader

    def download(self, url):
        return self.downloader.get_result(url)


class Control:
    STRATEGY = {
        "albums": DownloadCenter(AlbumJson()),
        "photos": DownloadCenter(PhotoJson()),
        "photo_binary": DownloadCenter(PhotoBinary()),
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

    def processing_photo(self, task: PhotoTask):
        photo: Photo = task.photo
        album: Album = task.album
        file: bytes = self.download(photo.url,  self.STRATEGY["photo_binary"])
        album_path = self.folder / album.title
        album_path.mkdir(exist_ok=True)

        # folder/<album.title>/<photo.title>.png
        path = (album_path / photo.title).with_suffix(".png")
        path.write_bytes(file)


    def run(self):
        self.create_folder()
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

            tasks = []
            for photo in photos_json:
                album = albums_json[photo.albumId]
                tasks.append(PhotoTask(photo=photo, album=album))

            executor.map(self.processing_photo, tasks)
        logger.debug("загружены фотки")

        



def main():
    t = Timer.start()
    logger.info("Запуск")
    downloader = Control(albums_url=ALBUM_URL, photos_url=PHOTOS_URL, folder=FOLDER)
    downloader.run()
    time_delta = t.stop()
    logger.info(f"Загрузка завершена за {time_delta}")


if __name__ == "__main__":
    main()
