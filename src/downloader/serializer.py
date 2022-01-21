from abc import ABC, abstractmethod
from typing import Any, Mapping, Type
from pydantic import BaseModel, parse_obj_as


class BaseSerializer(ABC):
    @abstractmethod
    def serialize(self, data: Mapping, many=False) -> Any:
        pass


class Serializer(BaseSerializer):
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
