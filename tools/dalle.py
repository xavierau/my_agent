import json
from typing import Literal

from tools.common import Tool, ToolCallResult
from utils.logger import Logger
from openai import OpenAI


class DallE3(Tool):
    name: str = "dall_e_3"
    description: str = "This is very helpful if you need to create a image"

    async def run(self,
            requirement: str,
            quality: Literal["standard", "hd"] = "standard",
            number_of_image=1) -> ToolCallResult:
        Logger.info(f"tool:{self.name}")

        response = OpenAI().images.generate(
            model="dall-e-3",
            prompt=requirement,
            size="1024x1024",
            quality=quality,
            n=number_of_image,
        )

        images = response.data

        print("images: ", images)

        return ToolCallResult(result=json.dumps({"status": "completed", "image_urls": [i.url for i in images]}))

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
                        "requirement": {
                            "type": "string",
                            "description": "The requirement of the image you want to generate.",
                        },
                        "quality": {
                            "type": "string",
                            "enum": ["standard", "hd"],
                            "description": "The quality of the image you want to generate.",
                            "default": "standard"
                        },
                        "number_of_image": {
                            "type": "number",
                            "description": "Number of images you want to generate. It must between 1 and 3",
                            "default": 1
                        },
                    },
                    "required": ["requirement"]
                },
            }
        }
