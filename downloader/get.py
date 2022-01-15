from abc import ABC, abstractmethod

from typing import List

import requests
import aiohttp


class BaseGet(ABC):
    @abstractmethod
    def get_json(self, url: str):
        pass

    @abstractmethod
    def get_bytes(self, url: str):
        pass


class Get(BaseGet):
    def get(self, url: str) -> requests.Response:
        """скачивание

        Returns:
            [requests.Response]

        Raises:
            [HTTPError]: ошибка скачивания
        """
        r = requests.get(url)
        r.raise_for_status()
        return r

    def get_json(self, url: str) -> List[dict]:
        """скачивание json

        Returns:
            [list[dict]] список словарей json

        """
        return self.get(url).json()

    def get_bytes(self, url: str) -> bytes:
        return self.get(url).content


class AsyncGet(BaseGet):
    def __init__(self) -> None:
        self._client = aiohttp.ClientSession(raise_for_status=True)

    async def close(self) -> None:
        return await self._client.close()

    async def get(self, url: str) -> aiohttp.ClientResponse:
        async with self._client.get(url) as resp:
            return resp

    async def get_json(self, url: str) -> List[dict]:
        return await (await self.get(url)).json()  # как бы избавиться от 2 await

    async def get_bytes(self, url: str) -> bytes:
        return await (await self.get(url)).read()
