from pydantic import BaseModel, Field, HttpUrl
from typing import NamedTuple


class Album(BaseModel):
    """album json сериализация

    Example:
        {
            "userId": 1,
            "id": 1,
            "title": "quidem molestiae enim"
        }
    """

    userId: int
    id_: int = Field(alias="id")
    title: str


class Photo(BaseModel):
    """photo json сериализация

    Example:
        {
            "albumId": 1,
            "id": 1,
            "title": "accusamus beatae ad facilis cum similique qui sunt",
            "url": "https://via.placeholder.com/600/92c952",
            "thumbnailUrl": "https://via.placeholder.com/150/92c952"
        }
    """

    albumId: int
    id_: int = Field(alias="id")
    title: str
    url: HttpUrl
    thumbnailUrl: HttpUrl


class PhotoTask(NamedTuple):
    url: str
    album_title: str
    title: str
    raw: bytes = None