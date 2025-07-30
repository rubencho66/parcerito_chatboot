from pydantic import BaseModel, EmailStr, ConfigDict

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
