import uvicorn as uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import UJSONResponse
from starlette.responses import Response
from starlette.status import HTTP_204_NO_CONTENT, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_422_UNPROCESSABLE_ENTITY

from src import __version__

from src.services.upload_video import upload_video_router
from src.settings import HOST, PORT
from src.utils.exceptions import JSONException

app = FastAPI(
    title="Upload de Vídeos",
    version=__version__,
    description="Serviço Upload de Vídeos",
    docs_url="/docs"
)

app.include_router(upload_video_router)


# @app.exception_handlers(RequestValidationError)
# async def unprocessable_entity_error(exc: RequestValidationError):
#     return UJSONResponse(content={'message': exc.errors()}, status_code=HTTP_422_UNPROCESSABLE_ENTITY)
#
#
# @app.exception_handlers(JSONException)
# async def treated_error(exc: JSONException):
#     if exc.status_code == HTTP_204_NO_CONTENT:
#         return Response(status_code=exc.status_code)
#     return UJSONResponse(content=exc.payload, status_code=exc.status_code)
#
#
# @app.exception_handlers(Exception)
# async def unkown_error(exc: Exception):
#     return UJSONResponse(content={'message': str(exc)}, status_code=HTTP_500_INTERNAL_SERVER_ERROR)


if __name__ == "__main__":
    uvicorn.run(
        "src.app:app",
        host=HOST,
        port=PORT,
        log_level="info"
    )
