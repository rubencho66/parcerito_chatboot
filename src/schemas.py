"""schemas.py"""

from pydantic import BaseModel, EmailStr, ConfigDict


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    detail: str
    statusCode: int


class SecurityContext(BaseModel):
    """Security context for authenticated users."""
    id: int
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class CreateUser(BaseModel):
    """Schema for creating a new user."""
    email: EmailStr
    name: str
    password: str


class ResponseUser(BaseModel):
    """Schema for user response."""
    email: str
    name: str

    model_config = ConfigDict(from_attributes=True)


class ResponseToken(BaseModel):
    """Schema for response token."""
    access_token: str
    token_type: str
    status_code: int
    message: str


class LoginRequest(BaseModel):
    """Schema for login request."""
    email: EmailStr
    password: str


class ChatRequest(BaseModel):
    """Schema for chat request."""
    message: str
    conversation_id: str | None = None


class ChatResponse(BaseModel):
    """Schema for chat response."""
    reply: str
    statusCode: int
    conversation_id: str | None = None

    model_config = ConfigDict(from_attributes=True)


class LLMResponse(BaseModel):
    """Schema for LLM response."""
    content: str
