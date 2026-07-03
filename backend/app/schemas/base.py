from typing import Any, Generic, Optional, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class ErrorResponse(BaseModel):
    message: str
    details: Optional[Any] = None

class StandardResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: Optional[T] = None
    error: Optional[ErrorResponse] = None

def success_response(data: Any, message: str = "Operation successful") -> StandardResponse:
    return StandardResponse(success=True, message=message, data=data)

def error_response(message: str, details: Optional[Any] = None) -> StandardResponse:
    return StandardResponse(
        success=False,
        message="Operation failed",
        error=ErrorResponse(message=message, details=details)
    )
