from typing import List, Dict

from .base import BaseDownloader
from .get import client
from .serializer import Serializer
from .models import Album, Photo


class AsyncAlbumJson(BaseDownloader):
    serializer = Serializer(Album)

    async def get_result(self, url: str) -> Dict[int, Album]:
        async with client() as downloader:
            res = {}
            for i in await downloader.get_json(url):
                album: Album = self.serialize(i)
                if album.id_ in res:
                    raise Exception("Альбом с id {album.id_} уже существует")
                res[album.id_] = album
            return res


class AsyncPhotoJson(BaseDownloader):
    serializer = Serializer(Photo)

    async def get_result(self, url: str) -> List[Photo]:
        async with client() as downloader:
            data = await downloader.get_json(url)
            return self.serialize(data, many=True)


class AsyncPhotoBinary(BaseDownloader):
    async def get_result(self, url: str) -> bytes:
        async with client() as downloader:
            return await downloader.get_bytes(url)
