import uuid
from typing import Optional, List

from sqlalchemy import desc, text
from sqlalchemy.orm import Session
from database import models, schemas


# from services.auth import get_password_hash


def get_user(db: Session, user_id: uuid.UUID):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email):
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_phone_number(db: Session, phone_number):
    return db.query(models.User).filter(models.User.phone == phone_number).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


# def create_user(db: Session, user: schemas.UserCreate):
#     hashed_password = get_password_hash(user.password)
#     db_user = models.User(name=user.name, email=user.email, phone=user.phone, hashed_password=hashed_password)
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user


def update_user(db: Session, user: schemas.UserEdit):
    db_user = db.query(models.User).filter(models.User.id == user.id) \
        .update({"name": user.name, "email": user.email})
    return db_user


def create_session(db: Session, user_id: uuid.UUID, agent_id: uuid.UUID):
    db_session = models.Session(user_id=user_id, agent_id=agent_id)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


def delete_session(db: Session, session_id: uuid.UUID):
    return db.query(models.Session).filter(models.Session.id == session_id).update({"deleted_at": text("now()")})


def get_sessions_by_user_agent_id(db: Session, user_id: uuid.UUID, agent_id: uuid.UUID):
    return db.query(models.Session) \
        .filter(models.Session.agent_id == agent_id) \
        .filter(models.Session.user_id == user_id) \
        .filter(models.Session.deleted_at is None) \
        .all()


def get_messages_by_session_id(db: Session, session_id: uuid.UUID, skip: int = 0, limit: int = 100):
    return db.query(models.Message) \
        .filter(models.Message.session_id == session_id) \
        .order_by(desc(text("created_at"))) \
        .offset(skip) \
        .limit(limit) \
        .all()


def create_message(db: Session, message: schemas.MessageCreate):
    db_message = models.Message(message=message.message,
                                role=message.role,
                                session_id=message.session_id)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


def delete_all_messages_by_user_and_agent_id(db: Session, user_id: uuid.UUID, agent_id: uuid.UUID):
    return db.query(models.Message) \
        .filter(models.Message.user_id == user_id) \
        .filter(models.Message.agent_id == agent_id) \
        .delete()


def get_agent_by_id(db: Session, agent_id: uuid.UUID):
    return db.query(models.Agent).filter(models.Agent.id == agent_id).first()


def get_agent_by_name_and_user_id(db: Session, name: str, user_id: uuid.UUID):
    return db.query(models.Agent).filter(models.Agent.user_id == user_id).filter(models.Agent.name == name).first()


def get_agents_by_user_id(db: Session, user_id: uuid.UUID, skip: int = 0, limit: int = 0):
    query = db.query(models.Agent).filter(models.Agent.user_id == user_id).offset(skip)

    if limit > 0:
        query = query.limit(limit)

    return query.all()


def create_agent(db: Session, agent: schemas.AgentCreate, user_id: uuid.UUID):
    db_agent = models.Agent(**agent.dict(), user_id=user_id)
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent


def get_agent_by_session_id(db, session_id: uuid.UUID):
    session = db.query(models.Session).filter(models.Session.id == session_id).first()

    if session is None:
        raise ValueError("Session not found")

    return session.agent


def get_entities_by_session_id(db: Session, session_id: uuid.UUID, skip: int = 0, limit: int = 100):
    return db.query(models.Entity) \
        .filter(models.Entity.session_id == session_id) \
        .order_by(desc(text("created_at"))) \
        .offset(skip) \
        .limit(limit) \
        .all()


def get_entity_by_session_id_and_key(db, session_id: uuid.UUID, key: str):
    return db.query(models.Entity) \
        .filter(models.Entity.session_id == session_id) \
        .filter(models.Entity.key == key) \
        .first()


def create_entity(db: Session, entity: schemas.EntityCreate):
    entity = models.Entity(content=entity.content,
                           key=entity.key,
                           session_id=entity.session_id)
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity


def update_entity(db: Session, entity_id: uuid.UUID, entity: schemas.EntityEdit):
    db_entity = db.query(models.Entity) \
        .filter(models.Entity.id == entity_id) \
        .update({"content": entity.content})

    db.refresh(db_entity)

    return db_entity


def insert_or_update_entity_by_user_id(db, session_id: uuid.UUID, entity: schemas.EntityEdit) -> schemas.Entity:
    db_entity = get_entity_by_session_id_and_key(db, session_id, entity.key)

    if db_entity is None:
        db_entity = create_entity(db, schemas.EntityCreate(content=entity.content,
                                                           session_id=session_id,
                                                           key=entity.key))
    else:
        update_entity(db, db_entity.id, entity)

    return db_entity


def delete_entity_by_user_id(db, session_id: uuid.UUID):
    return db.query(models.Entity) \
        .filter(models.Entity.session_id == session_id) \
        .delete()


def get_entity_by_session_id_and_key(db, session_id: uuid.UUID, key: str) -> schemas.Entity:
    return db.query(models.Entity) \
        .filter(models.Entity.session_id == session_id) \
        .filter(models.Entity.key == key) \
        .first()


def delete_all_messages_by_session_id(db, session_id: uuid.UUID):
    return db.query(models.Message) \
        .filter(models.Message.session_id == session_id) \
        .delete()
