from pydantic import BaseModel, EmailStr

class AuthRequest(BaseModel):
    email: str
    password: str

class EmailRequest(BaseModel):
    email: EmailStr