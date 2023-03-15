from flask import jsonify


class HttpError(Exception):
    def __init__(self, status_code: int, description: str | dict | list):
        self.status_code = status_code
        self.description = description


def error_handler(error: HttpError):
    response = jsonify({"status": "error", "description": error.description})
    response.status_code = error.status_code
    return response
