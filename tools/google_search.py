# import os
import json
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

dotenv.load_dotenv()

from tools.common import Tool


class GoogleSearchTool(Tool):
    """Search from Google"""
    name = "google_search"
    description = "It is helpful when you need to search information from internet"
    summary_model = "gpt-3.5-turbo"

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
                            "description": "The query you want to search.",
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

    def run(self, query: str, limit=5) -> str:

        Logger.info(f"tool:{self.name} query: {query}, limit: {limit}")

        print('search query: ', query)

        if query is None:
            raise Exception

        url = f"https://customsearch.googleapis.com/customsearch/v1?cx={self.search_engine_id}&q={query}&key={self.key}&num={limit}"

        response_dict = requests.get(url).json()

        items = response_dict.get('items')

        summarized_websites = [self._to_structure(query, data) for data in items]

        result = []

        for website in summarized_websites:
            if website.get('summary', None):
                result.append(website)

        print(result)

        return json.dumps(result)

    def _to_structure(self, question: str, data: dict):
        return {
            "title": data.get("title"),
            "link": data.get("link"),
            "summary": self._summary_site(question, data.get("link"))
        }

    def _summary_site(self, question: str, url: str) -> str | None:

        try:
            # Send a GET request to the URL
            response = requests.get(url)

            # Check if the request was successful
            if response.status_code == 200:
                # Parse the content of the request with BeautifulSoup
                soup = BeautifulSoup(response.content, 'html.parser')

                # Extract data
                # For example, this will print all the text in the body of the HTML
                content = soup.get_text()

                context = content

                encoder = tiktoken.encoding_for_model("gpt-3.5-turbo")
                number_of_tokens = len(encoder.encode(context))

                if number_of_tokens < 2048:
                    return self._simple_summarize(query=question, text=context)
                else:
                    return self._reduce_summarize(query=question, text=context)

            else:
                print("Failed to retrieve the webpage")
                return None

        except:
            print("Something wrong about fetching the url")
            return None

    def _simple_summarize(self, query: str, text: str) -> str:
        suggestion = f"""Base on the following context, answer user's question.
                    Context:
                    {text}
                    `````
                    User Question:
                    {query}
                    `````

                    Answer:"""

        messages = [{"role": "user", "content": suggestion}]

        return get_response_content_from_gpt(messages, self.summary_model)

    def _summarize_chunk(self, query: str, chunk):
        suggestion = f"""Base on the following context, answer user's question.
                           Context:
                           {chunk}
                           `````
                           User Question:
                           {query}
                           `````

                           Answer:"""

        messages = [{"role": "user", "content": suggestion}]

        return get_response_content_from_gpt(messages, self.summary_model)

    def _group_summarized_chunk(self, query: str, chunks: List[str]):

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

        return get_response_content_from_gpt(messages, self.summary_model)

    def _reduce_summarize(self, query: str, text: str):
        text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=2048, chunk_overlap=100
        )
        texts = text_splitter.split_text(text)

        summaries = []
        for t in texts:
            summaries.append(self._simple_summarize(query=query, text=t))

        return self._group_summarized_chunk(query=query, chunks=summaries)
