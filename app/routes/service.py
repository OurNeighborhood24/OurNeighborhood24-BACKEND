from sqlalchemy.orm import Session
from typing import List, Tuple, Optional
from app.reports.models import Report
from app.routes.schemas import (
    SafeRouteRequest,
    SafeRouteResponse,
    CoordinatePoint,
    DangerZoneInfo,
    WaypointInfo
)
from core.adapter.tmap import (
    get_pedestrian_route,
    extract_coordinates_from_route,
    create_route_linestring,
    create_buffer_polygon,
    calculate_safe_waypoints,
    find_nearby_dangers
)
from core.config import get_settings

settings = get_settings()


class SafeRouteService:
    """안전 경로 추천 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_safe_route(self, request: SafeRouteRequest) -> SafeRouteResponse:
        """
        안전한 경로 추천
        
        1. Tmap API로 기본 경로 조회
        2. 경로를 LineString으로 변환
        3. 버퍼 Polygon 생성
        4. DB에서 위험 지역 조회
        5. 차집합 연산으로 안전 지역 계산
        6. 안전 지역의 중심점을 경유지로 반환
        7. 근처 위험 지역 정보 반환
        
        Args:
            request: 안전 경로 요청 데이터
            
        Returns:
            SafeRouteResponse: 안전 경로 응답
        """
        # 1. Tmap API로 경로 조회
        start_coord = (request.start_longitude, request.start_latitude)
        end_coord = (request.end_longitude, request.end_latitude)
        
        tmap_api_key = settings.tmap_api_key
        route_data = get_pedestrian_route(start_coord, end_coord, tmap_api_key)
        
        # 총 거리와 시간 추출
        total_distance = None
        total_time = None
        if "features" in route_data and len(route_data["features"]) > 0:
            properties = route_data["features"][0].get("properties", {})
            total_distance = properties.get("totalDistance")  # 미터
            total_time = properties.get("totalTime")  # 초
            if total_time:
                total_time = int(total_time / 60)  # 분으로 변환
        
        # 2. 경로 좌표 추출 및 LineString 생성
        coordinates = extract_coordinates_from_route(route_data)
        
        if len(coordinates) < 2:
            raise ValueError("유효한 경로를 찾을 수 없습니다.")
        
        route_linestring = create_route_linestring(coordinates)
        
        # 3. 버퍼 Polygon 생성
        route_polygon = create_buffer_polygon(
            route_linestring, 
            buffer_distance_meters=request.buffer_distance
        )
        
        # 4. DB에서 모든 위험 지역(신고) 조회
        danger_reports = self.db.query(Report).all()
        
        # 위험 지역 좌표 리스트 생성
        danger_points = [
            (report.longitude, report.latitude)
            for report in danger_reports
        ]
        
        # 5. 안전한 경유지 계산 (차집합 연산)
        safe_waypoints = calculate_safe_waypoints(
            route_polygon,
            danger_points,
            danger_radius_meters=request.danger_radius
        )
        
        # 6. 경로 근처의 위험 지역 찾기
        danger_dicts = [
            {
                'report_id': report.report_id,
                'title': report.title,
                'description': report.description,
                'longitude': report.longitude,
                'latitude': report.latitude,
                'category_name': report.category.category_name if report.category else "미분류",
                'state': report.state.value
            }
            for report in danger_reports
        ]
        
        nearby_dangers_data = find_nearby_dangers(
            route_polygon,
            danger_dicts,
            search_distance_meters=200
        )
        
        # 7. 응답 데이터 구성
        original_route_points = [
            CoordinatePoint(longitude=lon, latitude=lat)
            for lon, lat in coordinates
        ]
        
        waypoint_infos = [
            WaypointInfo(longitude=lon, latitude=lat, order=idx + 1)
            for idx, (lon, lat) in enumerate(safe_waypoints)
        ]
        
        danger_zone_infos = [
            DangerZoneInfo(
                report_id=danger['report_id'],
                title=danger['title'],
                description=danger['description'],
                longitude=danger['longitude'],
                latitude=danger['latitude'],
                category_name=danger['category_name'],
                state=danger['state']
            )
            for danger in nearby_dangers_data
        ]
        
        return SafeRouteResponse(
            original_route=original_route_points,
            waypoints=waypoint_infos,
            nearby_dangers=danger_zone_infos,
            total_distance=total_distance,
            total_time=total_time
        )
    
    def get_route_with_waypoints(
        self,
        start: Tuple[float, float],
        waypoints: List[Tuple[float, float]],
        end: Tuple[float, float]
    ) -> dict:
        """
        경유지를 포함한 경로 조회
        
        Args:
            start: 출발지 (경도, 위도)
            waypoints: 경유지 리스트 [(경도, 위도), ...]
            end: 목적지 (경도, 위도)
            
        Returns:
            dict: 전체 경로 데이터
        """
        tmap_api_key = settings.tmap_api_key
        
        # 출발지 -> 첫 경유지 -> ... -> 마지막 경유지 -> 목적지
        points = [start] + waypoints + [end]
        
        all_routes = []
        
        for i in range(len(points) - 1):
            route_data = get_pedestrian_route(points[i], points[i + 1], tmap_api_key)
            all_routes.append(route_data)
        
        return {
            "routes": all_routes,
            "waypoints": waypoints
        }
