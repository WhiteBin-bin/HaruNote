from pydantic import BaseModel, EmailStr

class EmailVerificationRequest(BaseModel):
    email: EmailStr

class EmailVerificationResponse(BaseModel):
    message: str

class EmailVerificationToken(BaseModel):
    token: str
