from flask import Flask
from flask import jsonify, request
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError

from db import Session
from errors import HttpError, error_handler
from models import User, Advertisement, Token
from schema import RegisterUser, LoginUser, CreateAdvertisement, PatchAdvertisement
from tools import validate, hash_password, get_item, is_authorized, is_owner

app = Flask("app")
app.errorhandler(HttpError)(error_handler)


def register_user():
    json_data = request.json
    json_data = validate(json_data, RegisterUser)
    json_data["password"] = hash_password(json_data["password"])
    with Session() as session:
        user = User(**json_data)
        session.add(user)
        try:
            session.commit()
        except IntegrityError:
            raise HttpError(409, "user already exists")
        return jsonify({"id": user.id})


def login_user():
    json_data = request.json
    json_data = validate(json_data, LoginUser)
    json_data["password"] = hash_password(json_data["password"])
    with Session() as session:
        user = session.query(User).filter(User.email == json_data["email"]).first()
        if json_data["password"] == user.password:
            session.query(Token).filter(Token.user_id == user.id).delete()
            token = Token(user_id=user.id)
            session.add(token)
            session.commit()
            return jsonify({"token": token.id})
        raise HttpError(401, "invalid user or password")


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
            is_authorized(session)
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
            is_owner(adv_id, session, Advertisement)
            advertisement = get_item(adv_id, session, Advertisement)
            session.delete(advertisement)
            session.commit()
            return jsonify({"status": "deleted"})


# user routes
app.add_url_rule("/register/", view_func=register_user, methods=["POST"])
app.add_url_rule("/login", view_func=login_user, methods=["POST"])

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
