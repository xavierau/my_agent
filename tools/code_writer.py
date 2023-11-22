import json
import os
import re
from os import path

from tools.common import Tool, ToolCallResult
from utils.helpers import get_random_string
from utils.llm import get_response_message_from_gpt
from utils.logger import Logger
import subprocess

separator = "\n`````\n"


class CodeWriter(Tool):
    name: str = "code_writer"
    description: str = "This tool is used to compute or plot graph by creating a python script."

    _directory: str = "./coding"
    _environment: str = "python 3.10"
    _model_name = "gpt-4-1106-preview"

    _session_identifier: str = get_random_string(8)

    async def run(self, problem: str, conditions: str) -> ToolCallResult:
        Logger.info(f"tool:{self.name}")
        directories = [f"{self._directory}/{self._session_identifier}",
                       f"{self._directory}/{self._session_identifier}/output"]

        for directory in directories:
            os.mkdir(directory)

        response = await self._generate_script(problem, conditions)

        self._extract_python_code(response)

        output = self._run_script()
        if output is not None:
            print("Docker command output:")
            print(output)

        result = self._get_result()

        return ToolCallResult(result=json.dumps({
            "status": "success",
            "result": result,
            "session_identifier": self._session_identifier,
        }))

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
                        "problem": {
                            "type": "string",
                            "description": "The problem you need to solve by running a script.",
                        },
                        "conditions": {
                            "type": "string",
                            "description": "The conditions of the problem.",
                            "default": ""
                        },
                    },
                    "required": ["problem"]
                },

            }
        }

    async def _generate_script(self, problem: str, conditions: str) -> str:
        messages = [
            {
                "role": "system",
                "content": f"""You are a software engineer. You are given a requirement and you need to write a python script to solve it.
                If you need to plot a graph, you can use matplotlib and save the graph in ./output directory. 
                The Python version: {self._environment}
                Extra packages: matplotlib, pandas, numpy, yfinance, mplfinance, scikit-learn, pyppeteer, bs4"""
            },
            {
                "role": "user",
                "content": f"Please write a python script to solve the following problem:\n{problem}\n{separator}Conditions:\n{conditions}\n{separator}"
            }]
        message = await get_response_message_from_gpt(messages=messages, model_name=self._model_name)

        print(message.content)

        return message.content

    def _extract_python_code(self, markdown_content):
        """
        Extracts Python code blocks from Markdown content.

        Args:
        markdown_content (str): A string containing Markdown content.

        Returns:
        list: A list of strings, each representing a Python code block.
        """
        pattern = r"```python\n(.*?)\n```"
        code = re.findall(pattern, markdown_content, re.DOTALL)

        file_path = f"{self._directory}/{self._session_identifier}/code.py"

        with open(file_path, "w") as f:
            f.write(code[0])

    def _run_script(self):

        command = f""" docker run --rm -v "$(pwd)/{self._directory}/{self._session_identifier}:/app" -v "$(pwd)/{self._directory}/{self._session_identifier}/output:/app/output" python_runtime python code.py > output/result.log 2>&1"""
        try:
            result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    text=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Error occurred: {e.stderr}")
            return None

    def _get_result(self) -> str:
        file_path = f"./output/result.log"
        with open(file_path, "r") as f:
            return f.read()
