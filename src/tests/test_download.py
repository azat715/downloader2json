"""Tests"""

from unittest.mock import MagicMock

import aiohttp
import pytest

from downloader.main import get_albums, get_photos, save_file, fetch_raw

CONTENT = b'\xd1\x82\xd0\xb5\xd1\x81\xd1\x82'  # "тест"

ALBUM = {
    "userId": 1,
    "id": 1,
    "title": "quidem molestiae enim"
}

PHOTO = {
    "albumId": 1,
    "id": 1,
    "title": "accusamus beatae ad facilis cum similique qui sunt",
    "url": "https://via.placeholder.com/600/92c952",
    "thumbnailUrl": "https://via.placeholder.com/150/92c952"
}


def create_mock(data: dict):
    """Create mock aiohttp response

    Args:
        data: Dict response

    Returns:

    """
    mock = aiohttp.ClientSession
    mock.get = MagicMock()  # type: ignore
    mock.get.return_value.__aenter__.return_value.status = 200
    mock.get.return_value.__aenter__.return_value.json.return_value = [data]


@pytest.fixture
def mock_album_response():
    """Mock album response
    """
    create_mock(ALBUM)


@pytest.fixture
def mock_photo_response():
    """Mock photos response
    """
    create_mock(PHOTO)


@pytest.fixture
def mock_raw_response():
    """Mock bytes response
    """
    mock = aiohttp.ClientSession
    mock.get = MagicMock()
    mock.get.return_value.__aenter__.return_value.status = 200
    mock.get.return_value.__aenter__.return_value.read.return_value = CONTENT


@pytest.mark.asyncio
async def test_fetch_raw(mock_raw_response):
    """Test fetch raw"""
    async with aiohttp.ClientSession() as session:
        res = await fetch_raw("http:/test.com", session)
        assert res == CONTENT


@pytest.mark.asyncio
async def test_save_file(tmp_path):
    """Test save file"""
    path = tmp_path / "test.bin"
    await save_file(path, CONTENT)
    data = path.read_bytes()
    assert data.decode("utf-8") == "тест"


@pytest.mark.asyncio
async def test_get_albums(mock_album_response):
    """Test get album json"""
    async with aiohttp.ClientSession() as session:
        res = await get_albums("http:/test.com", session)
        assert res[1].dict(by_alias=True) == ALBUM


@pytest.mark.asyncio
async def test_get_photos(mock_photo_response):
    """Test get photo json"""
    async with aiohttp.ClientSession() as session:
        res = await get_photos("http:/test.com", session)
        assert res[0].dict(by_alias=True) == PHOTO
