from typing import List, Dict

from .base import BaseDownloader
from .get import AsyncGet
from .serializer import Serializer
from .models import Album, Photo


class AsyncAlbumJson(BaseDownloader):
    downloader = AsyncGet()
    serializer = Serializer(Album)

    async def get_result(self, url: str) -> Dict[int, Album]:
        res = {}
        for i in await self.downloader.get_json(url):
            album: Album = self.serialize(i)
            if album.id_ in res:
                raise Exception("Альбом с id {album.id_} уже существует")
            res[album.id_] = album
        return res


class AsyncPhotoJson(BaseDownloader):
    downloader = AsyncGet()
    serializer = Serializer(Photo)

    async def get_result(self, url: str) -> List[Photo]:
        data = await self.downloader.get_json(url)
        return self.serialize(data, many=True)


class AsyncPhotoBinary(BaseDownloader):
    downloader = AsyncGet()

    async def get_result(self, url: str) -> bytes:
        return self.downloader.get_bytes(url)
