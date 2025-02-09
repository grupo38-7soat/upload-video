from typing import Dict

from starlette.exceptions import HTTPException
from starlette.status import HTTP_204_NO_CONTENT, HTTP_401_UNAUTHORIZED, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND


class JSONException(HTTPException):

    def __init__(self, status_code: int, payload: Dict, detail: str = None):
        super(JSONException, self).__init__(status_code, detail)
        self.payload = payload


def handle_no_content_exception(default_message):
    raise JSONException(HTTP_204_NO_CONTENT, {'message': default_message})


def handle_unauthorized_exception(default_message):
    raise JSONException(HTTP_401_UNAUTHORIZED, {'message': default_message})


def handle_default_error_exception(default_message):
    raise JSONException(HTTP_400_BAD_REQUEST, {'message': default_message})


def handle_not_found_exception(default_message):
    raise JSONException(HTTP_404_NOT_FOUND, {'message': default_message})