from abc import ABC, abstractmethod

from typing import Any, List
from .get import BaseGet
from .serializer import BaseSerializer


class BaseDownloader(ABC):
    """абстрактный класс стратегии загрузки"""

    downloader: BaseGet
    serializer: BaseSerializer

    def serialize(self, data: List[dict], many=False):
        return self.serializer.serialize(data, many=many)

    @abstractmethod
    def get_result(self, url: str) -> Any:
        pass


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

    async def async_download(self, url, queue):
        return await self.downloader.get_result(url)
