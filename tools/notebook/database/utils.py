import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from tools.notebook.database import models, schemas
from tools.notebook.database.connection import get_db


def create_note(note: schemas.NoteCreate):
    for db in get_db():
        db_note = models.Note(**note.dict())
        db.add(db_note)
        db.commit()
        db.refresh(db_note)
        return db_note
