import time
import uuid
from hashlib import md5

import pydantic
from flask import request

from config import TOKEN_TTL
from db import Session
from errors import HttpError
from models import Token, ORM_MODEL_CLS


def validate(input_data: dict, validation_model):
    try:
        model_items = validation_model(**input_data)
        return model_items.dict(exclude_none=True)
    except pydantic.ValidationError as e:
        raise HttpError(403, e.errors())


def get_item(item_id: int, session: Session, model: ORM_MODEL_CLS):
    item = session.get(model, item_id)
    if item is None:
        raise HttpError(404, "object not found")
    return item


def hash_password(password: str):
    return md5(password.encode()).hexdigest()


def is_authorized(session: Session):
    try:
        token = uuid.UUID(request.headers.get("token"))
    except (ValueError, TypeError):
        raise HttpError(403, "incorrect token")
    token = session.query(Token).get(token)
    if token is None:
        raise HttpError(403, "incorrect token")
    if time.time() - token.creation_time.timestamp() > TOKEN_TTL:
        session.query(Token).filter(Token.id == token.id).delete()
        session.commit()
        raise HttpError(403, "incorrect token")
    return token


def is_owner(item_id: int, session: Session, model: ORM_MODEL_CLS):
    user_id = is_authorized(session).user_id
    item = get_item(item_id, session, model)
    if user_id == item.user_id:
        return item
    raise HttpError(403, "forbidden")
