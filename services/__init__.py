from services.common import Message, Memory, SystemPromptBuilder
from services.core import get_llm_response, add_user_message, get_function_response, add_assistant_message


def ask(message: str, memory: Memory, image_url=None)->Message:
    add_user_message(image_url, memory, message)

    response_message = get_llm_response(memory=memory)

    tool_calls = response_message.tool_calls

    if tool_calls:
        reply_message = get_function_response(memory, tool_calls)
    else:
        reply_message = response_message.content

    add_assistant_message(memory, reply_message)

    return memory.get_latest_message()
