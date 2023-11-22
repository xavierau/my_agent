import asyncio

from tools.common import Tool, ToolCallResult
from utils.logger import Logger

separator = "\n`````\n"


class WriteToMyNoteTool(Tool):
    name: str = "write_to_my_note"
    description: str = "This is very helpful if you need to write down something into the notebook"

    file_name: str = "./my_note.txt"

    async def run(self, content: str) -> ToolCallResult:
        Logger.info(f"tool:{self.name}")

        file = open(self.file_name, "a")  # append mode
        file.write(content + separator)
        file.close()
        return ToolCallResult(result="Successfully written to notebook.")

    @property
    def schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "The content you want to write down.",
                        },
                    },
                    "required": ["content"]
                },

            }
        }


class ReadFromMyNoteTool(Tool):
    name: str = "read_from_my_note"
    description: str = "This is very helpful if you need to read something from the notebook"

    file_name: str = "./my_note.txt"

    async def run(self, content: str) -> ToolCallResult:
        Logger.info(f"tool:{self.name}")
        print('here')
        with open(self.file_name, "r") as f:  # append mode
            return asyncio.Future().set_result(ToolCallResult(result=f.read()))

    @property
    def schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "The content you read look for.",
                        }
                    },
                    "required": ["content"]
                }
            }
        }
