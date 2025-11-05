from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class NotificationCreateRequest(BaseModel):
    """공지사항 생성 요청 스키마"""
    title: str = Field(..., max_length=255, description="공지사항 제목")
    content: str = Field(..., description="공지사항 내용")


class NotificationUpdateRequest(BaseModel):
    """공지사항 수정 요청 스키마"""
    title: Optional[str] = Field(None, max_length=255, description="공지사항 제목")
    content: Optional[str] = Field(None, description="공지사항 내용")


class NotificationResponse(BaseModel):
    """공지사항 응답 스키마"""
    notification_id: int
    writer_id: int
    title: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedNotificationResponse(BaseModel):
    """페이지네이션된 공지사항 목록 응답 스키마"""
    total: int = Field(..., description="전체 공지사항 수")
    offset: int = Field(..., description="시작 위치")
    size: int = Field(..., description="페이지 크기")
    items: List[NotificationResponse] = Field(..., description="공지사항 목록")

    class Config:
        from_attributes = True
