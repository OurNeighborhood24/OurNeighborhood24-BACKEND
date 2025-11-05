from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class LoginRequest(BaseModel):
    """로그인 요청 스키마"""
    email: EmailStr = Field(..., description="사용자 이메일")
    password: str = Field(..., description="비밀번호")


class TokenResponse(BaseModel):
    """토큰 응답 스키마"""
    access_token: str = Field(..., description="Access Token")

class RefreshTokenRequest(BaseModel):
    """토큰 재발급 요청 스키마"""
    # Refresh Token은 쿠키에서 가져오므로 request body는 비어있을 수 있음
    pass


class LogoutResponse(BaseModel):
    """로그아웃 응답 스키마"""
    message: str = Field(default="Successfully logged out")
