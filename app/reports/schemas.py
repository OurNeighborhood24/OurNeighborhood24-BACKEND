from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CategoryResponse(BaseModel):
    """카테고리 응답 스키마"""
    category_id: int
    category_name: str

    class Config:
        from_attributes = True


class ReportCreateRequest(BaseModel):
    """신고 생성 요청 스키마"""
    category_id: int = Field(..., description="카테고리 ID")
    latitude: float = Field(..., description="위도")
    longitude: float = Field(..., description="경도")
    title: str = Field(..., max_length=255, description="신고 제목")
    description: str = Field(..., description="신고 내용")
    image_url: Optional[str] = Field(None, description="이미지 URL")


class ReportResponse(BaseModel):
    """신고 응답 스키마"""
    report_id: int
    writer_id: int
    category_id: int
    latitude: float
    longitude: float
    title: str
    description: str
    image_url: Optional[str]
    state: str
    created_at: datetime

    class Config:
        from_attributes = True


class ReportDetailResponse(BaseModel):
    """신고 상세 응답 스키마"""
    report_id: int
    writer_id: int
    category: CategoryResponse
    latitude: float
    longitude: float
    title: str
    description: str
    image_url: Optional[str]
    state: str
    created_at: datetime

    class Config:
        from_attributes = True


class ReportUpdateRequest(BaseModel):
    """신고 수정 요청 스키마"""
    category_id: Optional[int] = Field(None, description="카테고리 ID")
    latitude: Optional[float] = Field(None, description="위도")
    longitude: Optional[float] = Field(None, description="경도")
    title: Optional[str] = Field(None, max_length=255, description="신고 제목")
    description: Optional[str] = Field(None, description="신고 내용")
    image_url: Optional[str] = Field(None, description="이미지 URL")


class ReportStateUpdateRequest(BaseModel):
    """신고 상태 변경 요청 스키마"""
    state: str = Field(..., description="신고 상태 (PENDING, CHECKED, PROCESSING, COMPLETED)")


class ReportAnswerCreateRequest(BaseModel):
    """신고 답변 생성 요청 스키마"""
    answer: str = Field(..., description="답변 내용")
    state: str = Field(..., description="답변 상태")


class ReportAnswerResponse(BaseModel):
    """신고 답변 응답 스키마"""
    report_answer_id: int
    report_id: int
    writer_id: int
    answer: str
    state: str
    created_at: datetime

    class Config:
        from_attributes = True


class ReportWithAnswerResponse(BaseModel):
    """답변이 포함된 신고 응답 스키마"""
    report: ReportDetailResponse
    answer: Optional[ReportAnswerResponse]

    class Config:
        from_attributes = True


class PaginatedReportResponse(BaseModel):
    """페이지네이션된 신고 목록 응답 스키마"""
    total: int = Field(..., description="전체 신고 수")
    offset: int = Field(..., description="시작 위치")
    size: int = Field(..., description="페이지 크기")
    items: List[ReportDetailResponse] = Field(..., description="신고 목록")

    class Config:
        from_attributes = True
