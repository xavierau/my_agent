from fastapi import FastAPI
from playsound import playsound
from pydantic import BaseModel
from starlette.responses import FileResponse

from services import ask
from services.common import Memory, FileBaseHistory

app = FastAPI()


class SendToGptRequest(BaseModel):
    content: str


@app.get('/')
def welcome():
    return {"msg": "Hello World"}


@app.post('/call')
def send_to_gpt(req: SendToGptRequest):
    memory_path = './mem.db'
    history = FileBaseHistory(file_path=memory_path)
    memory = Memory(history=history)
    response = ask(req.content, memory)

    # audio = get_audio(response)

    return {
        'message': response,
        'audio': None
    }


@app.get(path="/audio", response_class=FileResponse)
def get_audio_stream():
    return FileResponse('./speech.mp3', media_type='application/octet-stream', filename="speech.mp3")
