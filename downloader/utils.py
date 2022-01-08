import functools
import time
from typing import Any, List, Mapping, Type

import requests
from pydantic import BaseModel, parse_obj_as


class Get:
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


class Serializer:
    def __init__(self, model: Type[BaseModel]) -> None:
        self.model = model

    def serialize(self, data: Mapping, many=False) -> Any:
        """сериализация

        Args:
            data ([dict]): словарь json
            many ([bool]), default=False: работа со списком

        Raises:
            [ValidationError]: ошибка валидации pydantic
        """
        if many:
            return parse_obj_as(list[self.model], data)
        else:
            return self.model(**data)


class Timer:
    def __init__(self) -> None:
        self.t_start = time.monotonic()

    def stop(self) -> float:
        return time.monotonic() - self.t_start

    @classmethod
    def start(cls) -> "Timer":
        return cls()


def logger_wraps(logger):
    def wrapper(func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            logger.opt(depth=1)
            logger.debug(f"Загрузка url {args[1]} началась")
            t = Timer.start()
            result = func(*args, **kwargs)
            time_delta = t.stop()
            logger.debug(f"Загрузка url {args[1]} закончилась за {time_delta}")
            return result

        return wrapped

    return wrapper
