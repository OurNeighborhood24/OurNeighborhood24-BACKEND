from pydantic import BaseModel, Field
from typing import List, Optional


class CoordinatePoint(BaseModel):
    """좌표 포인트"""
    longitude: float = Field(..., description="경도")
    latitude: float = Field(..., description="위도")


class SafeRouteRequest(BaseModel):
    """안전 경로 요청"""
    start_longitude: float = Field(..., description="출발지 경도")
    start_latitude: float = Field(..., description="출발지 위도")
    end_longitude: float = Field(..., description="목적지 경도")
    end_latitude: float = Field(..., description="목적지 위도")
    buffer_distance: Optional[float] = Field(100, description="경로 버퍼 거리 (미터)", ge=10, le=500)
    danger_radius: Optional[float] = Field(50, description="위험 지역 반경 (미터)", ge=10, le=200)


class WaypointInfo(BaseModel):
    """경유지 정보"""
    longitude: float
    latitude: float
    order: int = Field(..., description="경유지 순서")


class SafeRouteResponse(BaseModel):
    """안전 경로 응답"""
    original_route: List[CoordinatePoint] = Field(..., description="원본 직선 경로 좌표 (출발지→목적지)")
    safe_route: List[CoordinatePoint] = Field(..., description="안전 경로 좌표 (경유지를 거치는 전체 경로)")
    waypoints: List[WaypointInfo] = Field(..., description="안전한 경유지 목록")
    original_distance: Optional[float] = Field(None, description="원본 경로 거리 (미터)")
    original_time: Optional[int] = Field(None, description="원본 경로 소요 시간 (분)")
    safe_distance: Optional[float] = Field(None, description="안전 경로 거리 (미터)")
    safe_time: Optional[int] = Field(None, description="안전 경로 소요 시간 (분)")
