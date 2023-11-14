from abc import ABC, abstractmethod
from dataclasses import Field

from pydantic import BaseModel


class Tool(BaseModel, ABC):
    name: str
    description: str

    @abstractmethod
    def run(self, **args) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def schema(self) -> dict:
        raise NotImplementedError
