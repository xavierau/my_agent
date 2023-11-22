import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

import pytz
from pydantic import BaseModel

import config


class ToolCallResult(BaseModel):
    result: str
    timestamp: datetime = datetime.now(pytz.timezone(config.time_zone)).isoformat()
    # this is anything might be useful for the frontend
    frontend: Optional[str] = None

    def to_response(self) -> str:
        return json.dumps({"result": self.result, "timestamp": self.timestamp})


class Tool(BaseModel, ABC):
    name: str
    description: str

    @abstractmethod
    async def run(self, **args) -> ToolCallResult:
        raise NotImplementedError

    @property
    @abstractmethod
    def schema(self) -> dict:
        raise NotImplementedError
