import os
from threading import Timer

import asyncio
import openai
import requests
from openai import OpenAI
import dotenv

dotenv.load_dotenv()

config = {
    "api_key": os.environ.get("OPENAI_KEY"),
    "organization": 'org-3lUywfXiayYoXfXMfTshFEo5',
}


def get_assistant_id() -> str:
    return "asst_ZuOTsqGPx3RvmZADkfokoJeS"


def get_threads_by_assistant_id(assistant_id) -> str:
    return "asst_ZuOTsqGPx3RvmZADkfokoJeS"


def create_message(thread_id: str, message: str) -> str:
    return openai.beta.threads.messages.create(thread_id=thread_id, content=message, role="user")


# create / get assistant
assistant_id = get_assistant_id()

# create / get thread with assistant id
thread_id = "thread_wZuBTVYaD0miY7TDVf8dyzlP"
# create / get message with thread id

message = create_message(thread_id,
                         "Thank you, but your output doesn't seem fit the shift definition. Please rewrite it.")

# execute a run
run = openai.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant_id)

# print(run)
# when run completed, retrieve the messages from the thread
completed = False


def wait_for_run(run_id: str, thread_id: str):
    run = openai.beta.threads.runs.retrieve(run_id=run_id, thread_id=thread_id)
    if run.status == "completed":
        return True
    else:
        return False


async def do_something_async(run_id, thread_id):
    await asyncio.sleep(0.5)
    return wait_for_run(run_id, thread_id)


while completed is False:
    completed = asyncio.run(do_something_async(run.id, thread_id))

messages = openai.beta.threads.messages.list(thread_id=thread_id)
print(messages.data[0].content[0].text)
