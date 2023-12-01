import asyncio

from tools.google_search import GoogleSearchTool
import os
import dotenv

dotenv.load_dotenv()

tool = GoogleSearchTool(
    key=os.getenv("GOOGLE_CUSTOM_SEARCH_API_KEY"),
    search_engine_id=os.getenv("GOOGLE_CUSTOM_SEARCH_ENGINE_ID")
)


async def main():
    result = await tool.run(query="How to make a cup of coffee", limit=2)

    print(result)


asyncio.run(main())
