import json
import os
from datetime import datetime
import enum
from typing import Optional, Any, List
import pytz

from openai import OpenAI
from playsound import playsound
from pydantic import BaseModel, Field

import dotenv

import config
from tools.common import Tool
from tools.email_writer import EmailWriter
from tools.google_search import GoogleSearchTool
from tools.note import WriteToMyNoteTool, ReadFromMyNoteTool

dotenv.load_dotenv()


class Message(BaseModel):
    id: Optional[str]
    role: str
    content: Optional[str] | Optional[List[Any]]
    tool_call_id: Optional[str]
    tool_calls: Optional[List[Any]]
    function: Optional[Any]
    name: Optional[str]
    function_response: Optional[Any]
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(pytz.timezone(os.getenv('TIMEZONE', "UTC"))).isoformat())

    def to_json(self):
        obj_dict = Message(role="user").__dict__
        keys = list(obj_dict.keys())
        temp = {}
        for key in keys:
            if self.__dict__.get(key) is not None:
                temp[key] = self.__dict__.get(key)

        return temp


class History(BaseModel):

    def get_messages(self) -> List[Message]:
        raise NotImplementedError

    def add_message(self, message: Message):
        raise NotImplementedError

    def to_openai_list(self, limit=20) -> List[Any]:
        temp_list = []
        obj_dict = Message(role="user").__dict__
        keys = list(obj_dict.keys())
        messages = self.get_messages()
        messages = messages[-limit:]

        for m in messages:
            temp = {}
            for key in keys:
                if m.__dict__.get(key) is not None:
                    temp[key] = m.__dict__.get(key)
            temp_list.append(temp)

        return temp_list


class FileBaseHistory(History):
    file_path: str

    def get_messages(self) -> List[Message]:
        with open(self.file_path, 'r') as fp:
            content = fp.read()
            try:
                json_data = json.loads(content)
                return [Message(**d) for d in json_data]
            except:
                return []

    def add_message(self, message: Message):
        messages = self.get_messages()
        messages.append(message)

        with open(self.file_path, 'w') as fp:
            json.dump([m.to_json() for m in messages], fp)


class SimpleHistory(History):
    messages = []

    def get_messages(self) -> List[Message]:
        return self.messages

    def add_message(self, message: Message):
        self.messages.append(message)
        return self


class Memory(BaseModel):
    history: History = Field(default_factory=SimpleHistory)

    def add(self, message: Message):
        self.history.add_message(message)
        return self

    def to_list(self):
        return self.history.to_openai_list()


class SystemPromptBuilder:
    memory: Optional[Memory] = None
    _agent_setting: Optional[str] = None
    _user_setting: Optional[str] = None
    _other_setting: Optional[str] = None

    def set_memory_setting(self, memory: Memory):
        self._memory = memory
        return self

    def set_agent_setting(self, agent_setting: str):
        self._agent_setting = agent_setting
        return self

    def set_user_setting(self, user_setting: str):
        self._user_setting = user_setting
        return self

    def set_other_setting(self, other_setting: str):
        self._other_setting = other_setting
        return self

    def build(self) -> str:
        return "\n\n".join(list(filter(lambda x: x, [
            self._agent_setting,
            self._user_setting,
            self._other_setting
        ])))
