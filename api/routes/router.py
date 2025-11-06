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
    1. Tmap API를 통해 기본 경로 조회
    2. 경로를 중심으로 버퍼 영역 생성
    3. 데이터베이스의 위험 지역(신고)과 차집합 연산
    4. 안전한 지역의 중심점을 경유지로 반환
    5. 경로 근처의 위험 지역 정보 제공
    
    **요청 파라미터:**
    - **start_longitude**: 출발지 경도
    - **start_latitude**: 출발지 위도
    - **end_longitude**: 목적지 경도
    - **end_latitude**: 목적지 위도
    - **buffer_distance**: 경로 버퍼 거리(미터, 기본값: 100m)
    - **danger_radius**: 위험 지역 반경(미터, 기본값: 50m)
    
    **응답:**
    - **original_route**: 원본 경로 좌표 리스트
    - **waypoints**: 안전한 경유지 좌표 리스트
    - **nearby_dangers**: 경로 근처의 위험 지역 리스트
    - **total_distance**: 총 거리(미터)
    - **total_time**: 예상 소요 시간(분)
    """
    try:
        route_service = SafeRouteService(db)
        result = route_service.get_safe_route(request)
        return result # 거리는 미터 기준, 예상 시간 분 기준
    except ValueError as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"경로 조회 중 오류가 발생했습니다: {str(e)}"
        )
