from pydantic import BaseModel, EmailStr

class EmailVerificationRequest(BaseModel):
    """이메일 인증 요청 모델"""
    email: EmailStr

class EmailVerificationCode(BaseModel):
    """이메일 코드 검증 모델"""
    email: EmailStr
    code: str
