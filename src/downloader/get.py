from abc import ABC, abstractmethod

from typing import AsyncIterator, List, Optional, Type
from types import TracebackType

import requests
import aiohttp
from contextlib import asynccontextmanager


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
    """похоже это не совсем правильно, сессия создается для каждого запроса и закрывается"""

    def __init__(self) -> None:
        self._client = aiohttp.ClientSession(raise_for_status=True)

    async def close(self) -> None:
        return await self._client.close()

    async def __aenter__(self) -> "AsyncGet":
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> Optional[bool]:
        await self.close()
        return None

    async def get_json(self, url: str) -> List[dict]:
        async with self._client.get(url) as resp:
            return await resp.json()

    async def get_bytes(self, url: str) -> bytes:
        async with self._client.get(url) as resp:
            return await resp.read()


@asynccontextmanager
async def client() -> AsyncIterator[AsyncGet]:
    """асинхронный контекст

        чтобы не было ошибки Asnycio - RuntimeError: Timeout context manager should be used inside a task Unclosed client session
        и сессия закрывалась после каждого запроса


        как бы вот этот контекст пробрасываю выше
        async def main():
        async with aiohttp.ClientSession() as session:
            async with session.get('http://httpbin.org/get') as resp:
                print(resp.status)
                print(await resp.text())

    asyncio.run(main())"""
    client = AsyncGet()
    try:
        yield client
    finally:
        await client.close()
