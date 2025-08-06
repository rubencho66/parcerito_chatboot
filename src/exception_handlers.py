from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from src.schemas import ErrorResponse
from src.constants import NOT_AUTHENTICATED_MESSAGE
import logging

def register_exception_handlers(app: FastAPI):
    logger = logging.getLogger(__name__)

    @app.exception_handler(StarletteHTTPException)
    async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
        logger.error("HTTP Exception: %s - Status Code: %s", exc.detail, exc.status_code)
        response = ErrorResponse(detail=exc.detail, statusCode=exc.status_code)
        if exc.status_code == 401:
            response = ErrorResponse(
                detail=NOT_AUTHENTICATED_MESSAGE, statusCode=exc.status_code
            )
        return JSONResponse(status_code=exc.status_code, content=response.model_dump())
