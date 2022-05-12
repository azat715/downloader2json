from unittest.mock import MagicMock

import aiohttp
import pytest

from downloader.main import get_albums, get_photos, save_file, fetch_raw

CONTENT = b'\xd1\x82\xd0\xb5\xd1\x81\xd1\x82'


@pytest.mark.asyncio
async def test_get_file():
    mock = aiohttp.ClientSession
    mock.get = MagicMock()
    mock.get.return_value.__aenter__.return_value.status = 200
    mock.get.return_value.__aenter__.return_value.read.return_value = CONTENT
    async with aiohttp.ClientSession() as session:
        res = await fetch_raw("http:/test.com", session)
        assert res == CONTENT

@pytest.mark.asyncio
async def test_create_file(tmp_path):
    path = tmp_path / "test.bin"
    await save_file(path, CONTENT)
    data = path.read_bytes()
    assert data.decode("utf-8") == "тест"

def create_mock(data: dict):
    mock = aiohttp.ClientSession
    mock.get = MagicMock()
    mock.get.return_value.__aenter__.return_value.status = 200
    mock.get.return_value.__aenter__.return_value.json.return_value = [data]

@pytest.mark.asyncio
async def test_get_albums():
    data = {
            "userId": 1,
            "id": 1,
            "title": "quidem molestiae enim"
    }
    create_mock(data)
    async with aiohttp.ClientSession() as session:
        res = await get_albums("http:/test.com", session)
        assert res[1].dict(by_alias=True) == data

@pytest.mark.asyncio
async def test_get_photos():
    data = {
        "albumId": 1,
        "id": 1,
        "title": "accusamus beatae ad facilis cum similique qui sunt",
        "url": "https://via.placeholder.com/600/92c952",
        "thumbnailUrl": "https://via.placeholder.com/150/92c952"
    }
    create_mock(data)
    async with aiohttp.ClientSession() as session:
        res = await get_photos("http:/test.com", session)
        assert res[0].dict(by_alias=True) == data
