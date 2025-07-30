from pydantic import BaseModel, EmailStr, ConfigDict

class ErrorResponse(BaseModel):
    detail: str
    statusCode: int

class SecurityContext(BaseModel):
    id: int
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)

class CreateUser(BaseModel):
    email: EmailStr
    name: str
    password: str

class ResponseUser(BaseModel):
    email: str
    name: str

    model_config = ConfigDict(from_attributes=True)

class ResponseToken(BaseModel):
    access_token: str
    token_type: str
    status_code: int
    message: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None

class ChatResponse(BaseModel):
    reply: str
    statusCode: int
    conversation_id: str | None = None

    model_config = ConfigDict(from_attributes=True)

class LLMResponse(BaseModel):
    content: str
