from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class RegionResponse(BaseModel):
    """지역 응답 스키마"""
    region_id: int
    region_code: int
    region_name: str

    class Config:
        from_attributes = True


class UserRegisterRequest(BaseModel):
    """회원가입 요청 스키마"""
    email: EmailStr = Field(..., description="사용자 이메일")
    password: str = Field(..., min_length=8, max_length=30, description="비밀번호 (8-30자)")
    region_id: int = Field(..., description="지역 ID")


class UserResponse(BaseModel):
    """사용자 응답 스키마"""
    user_id: int
    email: str
    role: str
    region: RegionResponse

    class Config:
        from_attributes = True


class UserRegisterResponse(BaseModel):
    """회원가입 응답 스키마"""
    message: str
    user: UserResponse


class UpdateRegionRequest(BaseModel):
    """지역 변경 요청 스키마"""
    region_id: int = Field(..., description="새로운 지역 ID")
