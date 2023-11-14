from openai import OpenAI

from utils.retry import retry


@retry(max_attempts=3, delay_seconds=2)
def get_response_content_from_gpt(messages: list, model_name="gpt-3.5-turbo-1106") -> str:
    response = OpenAI().chat.completions.create(
        model=model_name,
        messages=messages,
    )
    return response.choices[0].message.content


@retry(max_attempts=3, delay_seconds=2)
def get_response_message_from_gpt(messages: list, model_name="gpt-3.5-turbo-1106", **kwargs):
    response = OpenAI().chat.completions.create(
        model=model_name,
        messages=messages,
        **kwargs
    )
    return response.choices[0].message