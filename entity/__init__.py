from server import send_to_gpt
from services import Memory


def get_entity_from_memory(memory: Memory) -> str:
    response = send_to_gpt("What is your name?", memory)
