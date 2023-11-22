import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from tkinter import Image
from typing import List

import pytz
from fastapi import UploadFile
from openai import OpenAI

from services import Memory, Message, SystemPromptBuilder
from tools.code_writer import CodeWriter
from tools.common import Tool, ToolCallResult
from tools.dalle import DallE3
from tools.email_writer import EmailWriter
from tools.google_calender import GetGoogleCalendarTool, CreateGoogleCalendarTool, ModifyGoogleCalendarTool, \
    DeleteGoogleCalendarTool
from tools.google_search import GoogleSearchTool
from tools.note import WriteToMyNoteTool, ReadFromMyNoteTool
from tools.tweet_writer import SimpleTweetWriter
from tools.yoov_work_checkin import YoovWorkCheckin
from utils.llm import get_response_message_from_gpt

my_tools: List[Tool] = [
    GoogleSearchTool(
        key=os.getenv("GOOGLE_CUSTOM_SEARCH_API_KEY"),
        search_engine_id=os.getenv("GOOGLE_CUSTOM_SEARCH_ENGINE_ID")
    ),
    WriteToMyNoteTool(),
    ReadFromMyNoteTool(),
    EmailWriter(),
    SimpleTweetWriter(),
    YoovWorkCheckin(),
    GetGoogleCalendarTool(),
    CreateGoogleCalendarTool(),
    ModifyGoogleCalendarTool(),
    DeleteGoogleCalendarTool(),
    DallE3(),
    CodeWriter()
]


def get_available_tools():
    return my_tools or None


def get_client():
    return OpenAI()


async def get_response(memory, model_name="gpt-3.5-turbo-1106"):
    try:
        response_message = await get_llm_response(memory=memory, model_name=model_name)

        print("response_message ", response_message)

        tool_calls = response_message.tool_calls

        if tool_calls:
            response = await get_function_response(memory, tool_calls)
            return response
        else:
            return response_message.content
    except Exception as e:
        # Handle exceptions that might occur during the await calls
        print(f"An error occurred: {e}")
        # Return a suitable error message or re-raise the exception as needed
        return "An error occurred while processing the response"


def get_system_message(memory):
    agent_setting = """You are a helpful, cheerful personal assistant. Your name is John.
    Following is the user information that is very helpful for you to answer user's question.
    Using this information, provide a personalized response that aligns with their behavioral preferences. 
    Ensure your response is respectful, helpful, and tailored to the customer's individual needs. Try to list the source of the information if possible."""

    now = datetime.now(tz=pytz.timezone("Asia/Hong_Kong")).strftime("%d %B %Y %H:%M:%S, %A")

    user_setting = f"""User Information:
    Current Date and time: {now}
    Location: Hong Kong
    Name: Xavier Au (male)
    Birthday: 5th August 1982 (41 yrs old)
    Contact Info: 66281556, xavier.au@gmail.com (personal), xavierau@yoov.com (work)
    Home Address: Unit 715, 7/F, Block G, Kornhill Garden, 43-45 Hong Shing Street, Quarry Bay, Eastern District, Hong Kong Island
    Occupation: Software System Analyst
    Company: YOOV Internet Technology (HK) Limited
    Company Address: 19/F, Rykadan Capital Tower, 135 Hoi Bun Road, KT, KLN, HK
    Education: Graduate from Hong Kong University of Science and Technology (2005). Major in Physics and minor in Math
    Spouse Name and telephone: Adriane Ma (female, 39 yrs), 97408847
    Children: Katherine Au (female, 8 yrs, nickname: Kate), Venus Au (female, 2 yrs, nickname: Pui Pui)

    User behavioral traits and communication preferences:
    1. Direct and Task-Oriented: The customer is focused on specific information and quick solutions.
    2. Preference for Written Communication: The customer prefers written communication.
    3. Interest in Event Planning: The customer shows an interest in activities and events.
    4. Seeking Quick Solutions: The customer is seeking immediate solutions."""

    system_content = SystemPromptBuilder() \
        .set_agent_setting(agent_setting=agent_setting) \
        .set_user_setting(user_setting=user_setting) \
        .build()

    return {
        "role": "system",
        "content": [
            {"type": "text", "text": system_content}
        ]
    }


def get_available_functions():
    result = {}
    for tool in my_tools:
        result[tool.name] = tool.run
    return result


def get_overall_messages(memory: Memory):
    messages = memory.to_list()

    messages.insert(0, get_system_message(memory))

    return messages


async def get_llm_response(memory: Memory, model_name="gpt-3.5-turbo-1106"):
    config = {"model_name": model_name}

    tools = get_available_tools()

    if tools:
        config['tools'] = [t.schema for t in tools]
        config['tool_choice'] = "auto"

    return await get_response_message_from_gpt(messages=get_overall_messages(memory), **config)


async def get_function_response(memory, tool_calls):
    available_functions = get_available_functions()
    memory.add(Message(
        role="assistant",
        content="",
        tool_calls=[{
            "id": call.id,
            "function": call.function.__dict__,
            "type": call.type
        } for call in tool_calls]
    ))

    for tool_call in tool_calls:
        function_name = tool_call.function.name
        function_to_call = available_functions[function_name]
        function_args = json.loads(tool_call.function.arguments)

        function_call_result = await function_to_call(**function_args)

        print("function_call_result", function_call_result)

        function_call_reply_message = Message(
            tool_call_id=tool_call.id,
            role='tool',
            name=function_name,
            content=function_call_result.to_response(),
            frontend_render=function_call_result.frontend
        )

        memory.add(function_call_reply_message)

    return await get_response(memory)


def add_user_message(image_url, memory, message):
    user_message = Message(role='user',
                           content=[{"type": "text", "text": message}]) if image_url is None else Message(
        role='user',
        content=[
            {"type": "text", "text": message},
            {"type": "image_url", "image_url": {"url": image_url}}
        ]
    )
    memory.add(user_message)


def add_assistant_message(memory, reply_message):
    memory.add(Message(role='assistant', content=reply_message))


def get_audio(id: str, message: str):
    speech_file_path = f"./audio_files/{id}.mp3"
    get_client().audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=message
    ).stream_to_file(speech_file_path)

    return speech_file_path


def get_transcript(audio_file_path):
    path = Path(audio_file_path)
    file = open(path, "rb")
    transcript = get_client().audio.transcriptions.create(
        model="whisper-1",
        file=file
    )
    return transcript.text


async def ask(message: str, memory: Memory, image_url=None) -> Message:
    add_user_message(image_url, memory, message)

    reply_message = await get_response(memory, model_name="gpt-4-1106-preview")

    print("reply_message", reply_message)
    add_assistant_message(memory, reply_message)

    return memory.get_latest_message()
