from typing import Dict

from starlette.exceptions import HTTPException


class JSONException(HTTPException):

        def __init__(self, status_code: int, payload: Dict, detail: str = None):
            super(JSONException, self).__init__(status_code, detail)
            self.payload = payload


def handle_no_content_exception(default_message):
    raise HTTPException(
        status_code=204,
        detail=default_message
    )


def handle_unauthorized_exception(default_message):
    raise HTTPException(
        status_code=401,
        detail=default_message
    )


def handle_default_error_exception(default_message):
    raise HTTPException(
        status_code=400,
        detail=default_message
    )


def handle_not_found_exception(default_message):
    raise HTTPException(
        status_code=404,
        detail=default_message
    )
