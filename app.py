from hashlib import md5

import pydantic
from flask import Flask
from flask import jsonify, request
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError

from db import Session
from errors import HttpError, error_handler
from models import User, Advertisement
from schema import CreateUser, PatchUser, CreateAdvertisement, PatchAdvertisement

app = Flask("app")
app.errorhandler(HttpError)(error_handler)


def validate(input_data: dict, validation_model):
    try:
        model_items = validation_model(**input_data)
        return model_items.dict(exclude_none=True)
    except pydantic.ValidationError as e:
        raise HttpError(403, e.errors())


def get_user(user_id: int, session: Session):
    user = session.get(User, user_id)
    if user is None:
        raise HttpError(404, "user not found")
    return user


def get_advertisement(adv_id: int, session: Session):
    advertisement = session.get(Advertisement, adv_id)
    if advertisement is None:
        raise HttpError(404, "advertisement not found")
    return advertisement


def hash_password(password: str):
    return md5(password.encode()).hexdigest()


class UserView(MethodView):
    def get(self, user_id: int):
        with Session() as session:
            user = get_user(user_id, session)
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
            user = get_user(user_id, session)
            for field, value in json_data.items():
                setattr(user, field, value)
            session.add(user)
            session.commit()
            return jsonify({"status": "patched"})

    def delete(self, user_id: int):
        with Session() as session:
            user = get_user(user_id, session)
            session.delete(user)
            session.commit()
            return jsonify({"status": "deleted"})


class AdvertisementView(MethodView):
    def get(self, adv_id: int):
        with Session() as session:
            advertisement = get_advertisement(adv_id, session)
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
            get_user(json_data["user_id"], session)
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
            get_user(json_data["user_id"], session)
            advertisement = get_advertisement(adv_id, session)
            for field, value in json_data.items():
                setattr(advertisement, field, value)
            session.add(advertisement)
            session.commit()
            return jsonify({"status": "patched"})

    def delete(self, adv_id: int):
        with Session() as session:
            advertisement = get_advertisement(adv_id, session)
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
    app.run(host="127.0.0.1", port=5000)
