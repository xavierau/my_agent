import json
import os
from datetime import datetime
from typing import List

import pytz
from openai import OpenAI

from services import Memory, Message, SystemPromptBuilder
from tools.common import Tool
from tools.email_writer import EmailWriter
from tools.google_search import GoogleSearchTool
from tools.note import WriteToMyNoteTool, ReadFromMyNoteTool
from tools.tweet_writer import TweetWriter
from utils.llm import get_response_message_from_gpt, get_response_content_from_gpt

my_tools: List[Tool] = [
    GoogleSearchTool(
        key=os.getenv("GOOGLE_CUSTOM_SEARCH_API_KEY"),
        search_engine_id=os.getenv("GOOGLE_CUSTOM_SEARCH_ENGINE_ID")
    ),
    WriteToMyNoteTool(),
    ReadFromMyNoteTool(),
    EmailWriter(),
    TweetWriter()
]


def get_available_tools():
    return my_tools or None


def get_client():
    return OpenAI()


def get_system_message(memory):
    agent_setting = """You are a helpful, cheerful personal assistant. Your name is John.
    Following is the user information that is very helpful for you to answer user's question.
    Using this information, provide a personalized response that aligns with their behavioral preferences. 
    Ensure your response is respectful, helpful, and tailored to the customer's individual needs."""

    now = datetime.now(tz=pytz.timezone("Asia/Hong_Kong")).strftime("%d %M %Y %H:%M:%S, %A")

    user_setting = f"""User Information:
    Current Date and time: {now}
    Location: Hong Kong
    Name: Xavier Au (male, 41 yrs)
    Birthday: 5th August 1982
    Contact Info: 66281556, xavier.au@gmail.com (personal), xavierau@yoov.com (work)
    Home Address: Unit 715, 7/F, Block G, Kornhill Garden, 43-45 Hong Shing Street, Quarry Bay, Eastern District, Hong Kong Island
    Occupation: Software System Analyst
    Company: YOOV Internet Technology (HK) Limited
    Company Address: 19/F, Rykadan Capital Tower, 135 Hoi Bun Road, KT, KLN, HK
    Education: Graduate from Hong Kong University of Science and Technology (2005). Major in Physics and minor in Math
    Spouse Name and telephone: Adriane Ma (female, 39 yrs), 97408847
    Children: Katherine Au (female, 8 yrs), Venus Au (female, 2 yrs)

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


def get_llm_response(memory: Memory):
    config = {}

    tools = get_available_tools()

    if tools:
        config['tools'] = [t.schema for t in tools]
        config['tool_choice'] = "auto"

    response_message = get_response_message_from_gpt(messages=get_overall_messages(memory), **config)

    return response_message


def get_function_response(memory, tool_calls):
    available_functions = get_available_functions()
    memory.add(Message(
        role="assistant",
        content="",
        tool_calls=[{"id": call.id, "function": call.function.__dict__, "type": call.type} for call in
                    tool_calls]
    ))
    for tool_call in tool_calls:
        function_name = tool_call.function.name
        function_to_call = available_functions[function_name]
        function_args = json.loads(tool_call.function.arguments)

        function_response = function_to_call(**function_args)

        memory.add(Message(
            tool_call_id=tool_call.id,
            role='tool',
            name=function_name,
            content=function_response
        ))

    return get_response_content_from_gpt(messages=memory.to_list())


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
    transcript = get_client().audio.transcriptions.create(
        model="whisper-1",
        file=open(audio_file_path, "rb")
    )
    return transcript.text
