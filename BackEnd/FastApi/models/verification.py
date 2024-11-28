from pydantic import BaseModel, EmailStr
from typing import Optional

class EmailVerificationRequest(BaseModel):
    email: EmailStr

    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com"
            }
        }

class EmailVerificationResponse(BaseModel):
    message: str
    expires_in_minutes: Optional[int] = None  # 토큰 만료 시간(선택적 필드)

    class Config:
        schema_extra = {
            "example": {
                "message": "Verification email sent successfully",
                "expires_in_minutes": 15
            }
        }

class EmailVerificationToken(BaseModel):
    token: str

    class Config:
        schema_extra = {
            "example": {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }

