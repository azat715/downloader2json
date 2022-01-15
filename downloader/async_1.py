from typing import List, Dict

from .base import BaseDownloader
from .get import Get
from .serializer import Serializer
from .models import Album, Photo


class AlbumJson(BaseDownloader):
    downloader = Get()
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
    downloader = Get()
    serializer = Serializer(Photo)

    def get_result(self, url: str) -> List[Photo]:
        data = self.downloader.get_json(url)
        return self.serialize(data, many=True)


class PhotoBinary(BaseDownloader):
    downloader = Get()

    def get_result(self, url: str) -> bytes:
        return self.downloader.get_bytes(url)
