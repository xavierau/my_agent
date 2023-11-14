import cProfile

import uvicorn
from fastapi import FastAPI
from playsound import playsound
from pydantic import BaseModel
from starlette.responses import FileResponse

from services import ask
from services.common import Memory, FileBaseHistory
from services.core import get_audio

app = FastAPI()


class SendToGptRequest(BaseModel):
    content: str
    require_audio: bool = False


@app.get('/')
def welcome():
    return {"msg": "Hello World"}


@app.post('/call')
def send_to_gpt(req: SendToGptRequest):
    memory_path = './mem.db'
    history = FileBaseHistory(file_path=memory_path)
    memory = Memory(history=history)
    response_message = ask(req.content, memory)

    if req.require_audio:
        get_audio(response_message.id, response_message.content)

    return {
        'id': response_message.id,
        'message': response_message.content,
        'audio': req.require_audio
    }


@app.get(path="/audio/{id}", response_class=FileResponse)
def get_audio_stream(id: str):
    path = f"./audio_files/{id}.mp3"
    return FileResponse(path, media_type='application/octet-stream', filename=f"{id}.mp3")
