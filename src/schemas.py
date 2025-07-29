from pydantic import BaseModel, EmailStr, ConfigDict

class CreateUser(BaseModel):
    email: EmailStr
    name: str
    password: str

class ResponseUser(BaseModel):
    id: int
    email: str
    name: str
    password: str

    model_config = ConfigDict(from_attributes=True)
