from asyncio import sleep

from tools.common import Tool, ToolCallResult
from utils.logger import Logger

separator = "\n`````\n"


class YoovWorkCheckin(Tool):
    name: str = "yoov_work_checkin"
    description: str = "Only use this tool when user explicitly ask check in 'YOOV Work' and all other checkin should not call this function."

    async def run(self, **kwargs) -> ToolCallResult:
        return ToolCallResult(result="Successfully check in YOOV Work.")

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
                        "check": {
                            "type": "boolean",
                            "description": "User have explicitly mentioned want to checkin YOOV Work but not ambiguously just mentioon checkin.",
                        }
                    },
                }
            }
        }
