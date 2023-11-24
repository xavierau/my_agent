import datetime
import enum
import json

from sqlalchemy import Boolean, Column, ForeignKey, String, DateTime, types, UUID, JSON
from sqlalchemy.orm import relationship
import uuid

from tools.notebook.database.connection import Base

SIZE = 1024


class MessageRole(enum.Enum):
    user = "user"
    assistant = "assistant"
    TOOL = "tool"


class AgentConfigurationType(types.TypeDecorator):
    impl = types.String(SIZE)

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)

        return value

    def process_result_value(self, value, dialect):

        if value == '':
            value = None

        if value is not None and not '':
            value = json.loads(value)

        return value


# Tools Tables
class Note(Base):
    __tablename__ = "notes"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    name = Column(String)
    content = Column(String)
    session_id = Column(UUID, nullable=True)

    deleted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
