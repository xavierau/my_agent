# import os
import json
import os
from dataclasses import Field
from typing import List

import requests
import tiktoken
from bs4 import BeautifulSoup
from langchain.text_splitter import CharacterTextSplitter
from openai import OpenAI
import dotenv

from utils.llm import get_response_content_from_gpt
from utils.logger import Logger
from googleapiclient.discovery import build
import asyncio
from pyppeteer import launch
from bs4 import BeautifulSoup

dotenv.load_dotenv()

from tools.common import Tool, ToolCallResult


class GoogleSearchTool(Tool):
    """Search from Google"""
    name: str = "google_search"
    description: str = "It is helpful when you need to search information from internet"
    summary_model: str = "gpt-3.5-turbo"

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
                            "description": "The query you want to search. Take into account about the user preferences.",
                        },
                        "limit": {
                            "type": "number",
                            "description": "Number of top result return. It must between 1 and 10. Without special reason, always set it to 3.",
                            "default": 3
                        }
                    },
                    "required": ["query", "limit"]
                }
            }
        }

    key: str
    search_engine_id: str

    async def run(self, query: str, limit=5) -> ToolCallResult:

        Logger.info(f"tool:{self.name} query: {query}, limit: {limit}")

        print('search query: ', query)

        if query is None:
            raise Exception

        # url = f"https://customsearch.googleapis.com/customsearch/v1?cx={self.search_engine_id}&q={query}&key={self.key}&num={limit}"
        #
        # response_dict = requests.get(url).json()
        #
        # print("custom search response: ", response_dict)

        service = build(
            "customsearch", "v1", developerKey=os.getenv("GOOGLE_CUSTOM_SEARCH_API_KEY")
        )

        res = (
            service.cse()
            .list(
                q=query,
                cx=os.getenv("GOOGLE_CUSTOM_SEARCH_ENGINE_ID")
            )
            .execute()
        )

        items = res.get('items', [])

        if len(items) > limit:
            items = items[:limit]

        tasks = []

        for item in items:
            tasks.append(self._to_structure(query, item))

        summarized_websites = await asyncio.gather(*tuple(tasks))

        print("summarized_websites", summarized_websites)

        return ToolCallResult(result=json.dumps(summarized_websites))

    async def _to_structure(self, question: str, data: dict):
        return {
            "title": data.get("title"),
            "link": data.get("link"),
            "summary": await self._summarize_site(question, data.get("link"))
        }

    async def _summarize_site(self, question: str, url: str) -> str | None:

        try:
            # # Send a GET request to the URL
            # response = requests.get(url)
            #
            # # Check if the request was successful
            # if response.status_code == 200:
            #     # Parse the content of the request with BeautifulSoup
            #     soup = BeautifulSoup(response.content, 'html.parser')
            #
            #     # Extract data
            #     # For example, this will print all the text in the body of the HTML
            #     content = soup.get_text()
            #
            #     context = content
            #
            #     encoder = tiktoken.encoding_for_model("gpt-3.5-turbo")
            #     number_of_tokens = len(encoder.encode(context))
            #
            #     if number_of_tokens < 2048:
            #         return self._simple_summarize(query=question, text=context)
            #     else:
            #         return self._reduce_summarize(query=question, text=context)
            #
            # else:
            #     print("Failed to retrieve the webpage")
            #     return None

            # To run the async function

            context = await self.fetch_page_content(url)

            if context is None:
                return "No content found."

            encoder = tiktoken.encoding_for_model("gpt-3.5-turbo")
            number_of_tokens = len(encoder.encode(context))

            print("token count: ", number_of_tokens, url)

            if number_of_tokens < 2048:
                return await self._simple_summarize(query=question, text=context)
            else:
                return await self._reduce_summarize(query=question, text=context)

        except Exception as e:
            print("Something wrong about fetching the url")
            print(e)
            return None

    async def _simple_summarize(self, query: str, text: str) -> str:
        suggestion = f"""Base on the following context, answer user's question.
                        Context:
                        {text}
                        `````
                        User Question:
                        {query}
                        `````
    
                        Answer:"""

        messages = [{"role": "user", "content": suggestion}]

        return await get_response_content_from_gpt(messages, self.summary_model)

    async def _summarize_chunk(self, query: str, chunk):
        suggestion = f"""Base on the following context, answer user's question.
                               Context:
                               {chunk}
                               `````
                               User Question:
                               {query}
                               `````
    
                               Answer:"""

        messages = [{"role": "user", "content": suggestion}]

        return await get_response_content_from_gpt(messages, self.summary_model)

    async def _group_summarized_chunk(self, query: str, chunks: List[str]):
        summaries = '\n'.join(chunks)

        suggestion = f"""Base on the following summaries, answer user's question.
                                       Summaries:
                                       {summaries}
                                       `````
                                       User Question:
                                       {query}
                                       `````
    
                                       Answer:"""

        messages = [{"role": "user", "content": suggestion}]

        return await get_response_content_from_gpt(messages, self.summary_model)

    async def _reduce_summarize(self, query: str, text: str):
        text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=2048, chunk_overlap=100
        )
        texts = text_splitter.split_text(text)
        tasks = tuple([self._simple_summarize(query=query, text=t) for t in texts])

        summaries: List[str] = await asyncio.gather(*tasks)

        return await self._group_summarized_chunk(query=query, chunks=summaries)

    async def fetch_page_content(self, url):
        print("try url: ", url)
        try:
            # Launch the browser
            browser = await launch()
            print("browser launched")
            page = await browser.newPage()

            # Navigate to the URL
            await page.goto(url)
            print("visiting url", url)

            # Wait for the page to load (you can customize this)
            await asyncio.sleep(2)  # Waits for 2 seconds

            print("finished waiting", url)

            # Get page content after JavaScript is loaded
            content = await page.content()

            print("get content", url)

            # Use BeautifulSoup to parse the content
            soup = BeautifulSoup(content, 'html.parser')

            # Extract data
            page_text = soup.get_text()

            print("parsed content", url)

            # Here you can continue with your logic for summarizing text
            # ...

            await browser.close()
            return page_text

        except Exception as e:
            print(f"Something went wrong: {e}", url)
            return None
