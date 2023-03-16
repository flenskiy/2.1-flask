from hashlib import md5

import pydantic
from flask import Flask
from flask import jsonify, request
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError

from db import Session
from errors import HttpError, error_handler
from models import User, Advertisement, ORM_MODEL
from schema import CreateUser, PatchUser, CreateAdvertisement, PatchAdvertisement

app = Flask("app")
app.errorhandler(HttpError)(error_handler)


def validate(input_data: dict, validation_model):
    try:
        model_items = validation_model(**input_data)
        return model_items.dict(exclude_none=True)
    except pydantic.ValidationError as e:
        raise HttpError(403, e.errors())


def get_item(item_id: int, session: Session, model: ORM_MODEL):
    item = session.get(model, item_id)
    if item is None:
        raise HttpError(404, "object not found")
    return item


def hash_password(password: str):
    return md5(password.encode()).hexdigest()


class UserView(MethodView):
    def get(self, user_id: int):
        with Session() as session:
            user = get_item(user_id, session, User)
            return jsonify(
                {
                    "id": user.id,
                    "email": user.email,
                    "registration_time": user.registration_time.isoformat(),
                }
            )

    def post(self):
        json_data = request.json
        json_data = validate(json_data, CreateUser)
        json_data["password"] = hash_password(json_data["password"])
        with Session() as session:
            user = User(**json_data)
            session.add(user)
            try:
                session.commit()
            except IntegrityError:
                raise HttpError(409, "user already exists")
            return jsonify({"id": user.id})

    def patch(self, user_id: int):
        json_data = request.json
        json_data = validate(json_data, PatchUser)
        if "password" in json_data:
            json_data["password"] = hash_password(json_data["password"])
        with Session() as session:
            user = get_item(user_id, session, User)
            for field, value in json_data.items():
                setattr(user, field, value)
            session.add(user)
            session.commit()
            return jsonify({"status": "patched"})

    def delete(self, user_id: int):
        with Session() as session:
            user = get_item(user_id, session, User)
            session.delete(user)
            session.commit()
            return jsonify({"status": "deleted"})


class AdvertisementView(MethodView):
    def get(self, adv_id: int):
        with Session() as session:
            advertisement = get_item(adv_id, session, Advertisement)
            return jsonify(
                {
                    "id": advertisement.id,
                    "title": advertisement.title,
                    "description": advertisement.description,
                    "registration_time": advertisement.registration_time.isoformat(),
                    "user_id": advertisement.user_id,
                }
            )

    def post(self):
        json_data = request.json
        json_data = validate(json_data, CreateAdvertisement)
        with Session() as session:
            get_item(json_data["user_id"], session, User)
            advertisement = Advertisement(**json_data)
            session.add(advertisement)
            try:
                session.commit()
            except IntegrityError:
                raise HttpError(409, "advertisement already exists")
            return jsonify({"id": advertisement.id})

    def patch(self, adv_id: int):
        json_data = request.json
        json_data = validate(json_data, PatchAdvertisement)
        with Session() as session:
            get_item(json_data["user_id"], session, User)
            advertisement = get_item(adv_id, session, Advertisement)
            for field, value in json_data.items():
                setattr(advertisement, field, value)
            session.add(advertisement)
            session.commit()
            return jsonify({"status": "patched"})

    def delete(self, adv_id: int):
        with Session() as session:
            advertisement = get_item(adv_id, session, Advertisement)
            session.delete(advertisement)
            session.commit()
            return jsonify({"status": "deleted"})


# user routes
app.add_url_rule(
    rule="/user/<int:user_id>/",
    view_func=UserView.as_view("user"),
    methods=["GET", "PATCH", "DELETE"],
)
app.add_url_rule(
    rule="/user/", view_func=UserView.as_view("user_create"), methods=["POST"]
)

# advertisement routes
app.add_url_rule(
    rule="/advertisement/<int:adv_id>/",
    view_func=AdvertisementView.as_view("advertisement"),
    methods=["GET", "PATCH", "DELETE"],
)
app.add_url_rule(
    rule="/advertisement/",
    view_func=AdvertisementView.as_view("advertisement_create"),
    methods=["POST"],
)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
