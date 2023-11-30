import json
from typing import List
import dotenv

from utils.llm import get_response_message_from_gpt
from utils.logger import Logger

dotenv.load_dotenv()

from tools.common import Tool, ToolCallResult


class GPT4V(Tool):
    """Search from Google"""
    name: str = "get_4_vision"
    description: str = "It is helpful when you need to ask a question about vision."

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
                        "query": {
                            "type": "string",
                            "description": "The query you want to ask about the image.",
                        },
                        "image_url": {
                            "type": "string",
                            "description": "The image url you want to ask about.",
                        },
                    },
                    "required": ["query", "image_url"]
                }
            }
        }

    async def run(self, query: str, image_url: str) -> ToolCallResult:
        Logger.info(f"tool:{self.name}")

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": query
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url,
                            "detail": "high"
                        }
                    }
                ]
            }
        ]

        response_message = await get_response_message_from_gpt(messages=messages,
                                                               model_name="gpt-4-vision-preview",
                                                               max_tokens=1000)
        reply_message = response_message.content

        return ToolCallResult(result=json.dumps({
            "reply_message": reply_message,
            "image_url": image_url
        }))
