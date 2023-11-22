import os
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Annotated, Optional

import dotenv
from fastapi import FastAPI, UploadFile, Request, Form, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette.responses import FileResponse, JSONResponse

from database.connection import create_tables, get_db
from services.common import Memory, FileBaseHistory, PostgresHistory
from services.core import get_audio, get_transcript, ask
from fastapi.middleware.cors import CORSMiddleware
import logging

from utils.helpers import resize_image_file
from utils.s3 import upload_to_s3
from fastapi.middleware.gzip import GZipMiddleware

dotenv.load_dotenv()

now = datetime.today().date()

log_file_path = f"logs/{now}.log"
if os.path.isfile(log_file_path) is False:
    open(log_file_path, 'a').close()

logging.basicConfig(
    filename=log_file_path,
    filemode="a",
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

create_tables()

origins = ["*"]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.middleware("secret_key")
async def secret_key_middleware(request: Request, call_next):
    print("in secret key middleware")
    set_secret_key = os.getenv('SECRET_KEY', None)
    if set_secret_key is None:
        return await call_next(request)

    secret_key = request.headers.get('X-Secret-Key')

    if secret_key != set_secret_key:
        return JSONResponse(
            status_code=401,
            content={"msg": "Invalid Secret Key"},
        )

    print("pass secret key middleware")
    
    return await call_next(request)


class SendToGptRequest(BaseModel):
    content: str
    file: Optional[UploadFile] = None
    require_audio: bool = False


class SendToGptWithAudioRequest(BaseModel):
    audio: UploadFile
    require_audio: bool = False


@app.get('/')
def welcome():
    return {"msg": "Hello World"}


@app.post('/call')
async def send_to_gpt(req: SendToGptRequest, db: Annotated[Session, Depends(get_db)]):
    image_url = None

    if req.file is not None:
        print('here')
        content_type = req.file.content_type
        if content_type not in ["image/jpeg", "image/png"]:
            raise HTTPException(status_code=400, detail="Invalid file type")

        temp_directory = "./temp_upload_files"
        resize_image_file(file=req.file, store_file_dir_path=temp_directory)
        file_path = Path(temp_directory + "/" + req.file.filename)
        image_url = upload_to_s3(file_name=file_path, bucket="xavier-personal-agent")

    session_id: uuid.UUID = "6bd2db49-3c75-4a5c-abef-b9eac5a7dfe9"
    history = PostgresHistory(session=db, session_id=session_id)
    memory = Memory(history=history)
    response_message = await ask(req.content, memory, image_url)

    if req.require_audio:
        get_audio(response_message.id, response_message.content)

    return {
        'id': response_message.id,
        'message': response_message.content,
        'audio': req.require_audio
    }
    # return {
    #     'id': "726a4a41644741b5915d94bee03fb4f6",
    #     'message': "tresting",
    #     'audio': req.require_audio
    # }


@app.post('/call_with_audio')
async def send_to_gpt_with_audio(require_audio: Annotated[str, Form()], audio: Annotated[UploadFile, Form()]):
    temp_directory = './temp_upload_files'
    destination = Path(temp_directory + "/" + audio.filename)
    temp_file_path = os.path.join(temp_directory, audio.filename)

    try:
        with destination.open("wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)
    finally:
        audio.file.close()

    transcript = get_transcript(temp_file_path)

    send_to_gpt_request = SendToGptRequest(content=transcript, require_audio=require_audio)
    return send_to_gpt(send_to_gpt_request)


@app.get(path="/audio/{id}", response_class=FileResponse)
async def get_audio_stream(id: str):
    path = f"./audio_files/{id}.mp3"
    if os.path.isfile(path) is False:
        raise FileNotFoundError
    return FileResponse(path, media_type="audio/mpeg")


@app.get(path="/has_audio/{id}")
async def get_audio_stream(id: str):
    path = f"./audio_files/{id}.mp3"

    if os.path.isfile(path) is False:
        raise FileNotFoundError

    return True
