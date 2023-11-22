from openai import OpenAI, AsyncOpenAI

from utils.retry import retry


@retry(max_attempts=3, delay_seconds=2)
async def get_response_content_from_gpt(messages: list,
                                        model_name="gpt-3.5-turbo-1106",
                                        memory=None,
                                        **kwargs) -> str:
    response = await AsyncOpenAI().chat.completions.create(
        model=model_name,
        messages=messages,
        **kwargs
    )

    if memory is None or not response.choices[0].message.tool_calls:
        return response.choices[0].message.content

    tool_calls = response.choices[0].message.tool_calls

    memory.add(Message(
        role="assistant",
        content="",
        tool_calls=[{"id": call.id, "function": call.function.__dict__, "type": call.type} for call in
                    tool_calls]
    ))


@retry(max_attempts=3, delay_seconds=2)
async def get_response_message_from_gpt(messages: list, model_name="gpt-3.5-turbo-1106", **kwargs):
    response = await AsyncOpenAI().chat.completions.create(
        model=model_name,
        messages=messages,
        **kwargs
    )
    return response.choices[0].message
