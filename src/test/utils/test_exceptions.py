import pytest
from starlette.exceptions import HTTPException
from utils.exceptions import (
    JSONException,
    handle_no_content_exception,
    handle_unauthorized_exception,
    handle_default_error_exception,
    handle_not_found_exception,
)


# Teste da classe JSONException
def test_json_exception():
    payload = {"error": "Invalid request"}
    exception = JSONException(status_code=400, payload=payload, detail="Bad Request")

    assert exception.status_code == 400
    assert exception.detail == "Bad Request"
    assert exception.payload == payload


# Teste para handle_no_content_exception
def test_handle_no_content_exception():
    with pytest.raises(HTTPException) as exc_info:
        handle_no_content_exception("No content available")

    assert exc_info.value.status_code == 204
    assert exc_info.value.detail == "No content available"


# Teste para handle_unauthorized_exception
def test_handle_unauthorized_exception():
    with pytest.raises(HTTPException) as exc_info:
        handle_unauthorized_exception("Unauthorized access")

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Unauthorized access"


# Teste para handle_default_error_exception
def test_handle_default_error_exception():
    with pytest.raises(HTTPException) as exc_info:
        handle_default_error_exception("Invalid input")

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Invalid input"


# Teste para handle_not_found_exception
def test_handle_not_found_exception():
    with pytest.raises(HTTPException) as exc_info:
        handle_not_found_exception("Resource not found")

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Resource not found"
