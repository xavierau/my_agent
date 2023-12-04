import os

import asyncio
import dotenv

from tools.google_search import GoogleSearchTool

dotenv.load_dotenv()


async def main():
    tool = GoogleSearchTool(
        key=os.getenv("GOOGLE_CUSTOM_SEARCH_API_KEY"),
        search_engine_id=os.getenv("GOOGLE_CUSTOM_SEARCH_ENGINE_ID")
    )

    return await tool.run("How to make cream brulee", limit=2)


print(asyncio.run(main()))
