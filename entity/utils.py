from typing import List

from services import Message


def filter_targeted_message(messages: List[Message]) -> List[Message]:
    def conversation_filter_func(c: Message) -> bool:
        if c.role not in ['user', 'assistant']:
            return False

        if c.role == "assistant" and c.tool_calls:
            return False

        return True

    return list(filter(conversation_filter_func, messages))
