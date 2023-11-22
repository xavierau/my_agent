import datetime
import enum
import json
import pickle

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, func, types, UUID, JSON, ARRAY, TEXT, \
    Enum
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from database.connection import Base
import uuid

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


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    name = Column(String(255))
    phone = Column(String(255), nullable=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    is_active = Column(Boolean, default=True)

    sessions = relationship("Session", back_populates="user")
    agents = relationship("Agent", back_populates="user")
    notes = relationship("Note", back_populates="user")

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    role = Column(String(255), nullable=False)
    message = Column(JSON, nullable=True)
    session_id = Column(UUID, ForeignKey("sessions.id"), index=True, nullable=False)
    session = relationship("Session", back_populates="messages")

    deleted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def to_dict(self) -> dict:
        data = self.__dict__

        data['id'] = data['id'].hex

        return data


class Entity(Base):
    __tablename__ = "entities"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    key = Column(String(255))
    content = Column(String(255))

    session_id = Column(UUID, ForeignKey("sessions.id"), index=True, nullable=False)
    session = relationship("Session", back_populates="entities")

    deleted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class Agent(Base):
    __tablename__ = "agents"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    name = Column(String(255))
    configuration = Column(AgentConfigurationType())
    type = Column(String(255))

    user_id = Column(UUID, ForeignKey("users.id"))
    user = relationship("User", back_populates="agents")

    sessions = relationship("Session", back_populates="agent")

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class Session(Base):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)

    user_id = Column(UUID, ForeignKey("users.id"))
    user = relationship("User", back_populates="sessions")

    agent_id = Column(UUID, ForeignKey("agents.id"))
    agent = relationship("Agent", back_populates="sessions")

    entities = relationship("Entity", back_populates="session")
    messages = relationship("Message", back_populates="session")

    deleted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


# Tools Tables
class Note(Base):
    __tablename__ = "notes"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    name = Column(String(255))
    content = Column(TEXT)
    session_id = Column(UUID, nullable=True)

    user_id = Column(UUID, ForeignKey("users.id"))
    user = relationship("User", back_populates="notes")

    deleted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
