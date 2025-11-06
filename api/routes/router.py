from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from app.routes.service import SafeRouteService
from app.routes.schemas import SafeRouteRequest, SafeRouteResponse

router = APIRouter()


@router.post(
    "/safe",
    response_model=SafeRouteResponse,
    status_code=status.HTTP_200_OK,
    summary="안전한 경로 추천",
    description="출발지와 목적지를 입력받아 위험 지역을 피한 안전한 경로를 추천합니다."
)
async def get_safe_route(
    request: SafeRouteRequest,
    db: Session = Depends(get_db)
):
    """
    안전한 경로 추천 엔드포인트

    **기능:**
    1. Tmap API를 통해 기본 경로 조회 (출발지 → 목적지 직선)
    2. 경로를 중심으로 버퍼 영역 생성
    3. 데이터베이스의 위험 지역(COMPLETED 제외 신고)과 차집합 연산
    4. 안전한 지역의 중심점을 경유지로 계산
    5. 경유지를 거치는 안전 경로를 Tmap API로 재조회

    **요청 파라미터:**
    - **start_longitude**: 출발지 경도 (124~132)
    - **start_latitude**: 출발지 위도 (33~43)
    - **end_longitude**: 목적지 경도 (124~132)
    - **end_latitude**: 목적지 위도 (33~43)
    - **buffer_distance**: 경로 버퍼 거리(미터, 기본값: 100m)
    - **danger_radius**: 위험 지역 반경(미터, 기본값: 50m)

    **응답:**
    - **original_route**: 원본 직선 경로 좌표 리스트
    - **safe_route**: 안전 경로 좌표 리스트 (경유지 포함한 전체 경로)
    - **waypoints**: 안전한 경유지 좌표 리스트
    - **original_distance**: 원본 경로 거리(미터)
    - **original_time**: 원본 경로 소요 시간(분)
    - **safe_distance**: 안전 경로 거리(미터)
    - **safe_time**: 안전 경로 소요 시간(분)
    """
    try:
        route_service = SafeRouteService(db)
        result = route_service.get_safe_route(request)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"경로 조회 중 오류가 발생했습니다: {str(e)}"
        )
