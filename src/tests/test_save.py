import pytest
from downloader.main import save_file

CONTENT = b'\xd1\x82\xd0\xb5\xd1\x81\xd1\x82'

@pytest.mark.anyio
async def test_create_file(tmp_path):
    path = tmp_path / "test.bin"
    await save_file(path, CONTENT)
    data = path.read_bytes()
    assert data.decode("utf-8") == "тест"

