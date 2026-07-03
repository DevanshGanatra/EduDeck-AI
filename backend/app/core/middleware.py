from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import traceback

from app.core.exceptions import AppException
from app.core.logging import logger
from app.schemas.base import error_response

class GlobalExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except AppException as e:
            logger.warning(f"AppException: {e.message} - {e.details}")
            content = error_response(message=e.message, details=e.details).model_dump()
            return JSONResponse(status_code=e.status_code, content=content)
        except Exception as e:
            logger.error(f"Unhandled Exception: {str(e)}\n{traceback.format_exc()}")
            content = error_response(message="Internal Server Error").model_dump()
            return JSONResponse(status_code=500, content=content)
