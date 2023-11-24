import uuid
from datetime import datetime
from pydantic import BaseModel


# Tools
class NoteBase(BaseModel):
    name: str
    content: str


class NoteCreate(NoteBase):
    session_id: uuid.UUID


class Note(NoteBase):
    id: uuid.UUID
    session_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
