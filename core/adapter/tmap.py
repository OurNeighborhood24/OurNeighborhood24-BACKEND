import requests
import json
import re
from pprint import pprint
from shapely.geometry import LineString, Point, Polygon
from typing import List, Tuple


def get_pedestrian_route(start, end, app_key):
    """
    Tmap 보행자 경로 탐색 함수

    Args:
        start (tuple): (경도, 위도) 형태의 출발지 좌표
        end (tuple): (경도, 위도) 형태의 도착지 좌표
        app_key (str): Tmap API 인증키

    Returns:
        dict: 경로 데이터(JSON)
    """
    url = "https://apis.openapi.sk.com/tmap/routes/pedestrian?version=1"
    headers = {
        "appKey": app_key,
        "Content-Type": "application/json"
    }
    data = {
        "startX": start[0],
        "startY": start[1],
        "endX": end[0],
        "endY": end[1],
        "reqCoordType": "WGS84GEO",
        "resCoordType": "WGS84GEO",
        "startName": "출발지",
        "endName": "도착지"
    }

    response = requests.post(url, headers=headers, json=data)

    # 응답 상태 코드 확인
    if response.status_code != 200:
        error_msg = f"Tmap API 호출 실패 (status: {response.status_code})"
        try:
            error_detail = response.json()
            error_msg += f" - {error_detail}"
        except:
            error_msg += f" - {response.text[:200]}"
        raise Exception(error_msg)

    # 응답이 비어있는지 확인
    if not response.text or response.text.strip() == "":
        raise Exception("Tmap API 응답이 비어있습니다.")

    # 제어문자 제거 후 JSON 파싱
    try:
        clean_text = re.sub(r'[\x00-\x1f\x7f]', '', response.text)
        route_data = json.loads(clean_text)
    except json.JSONDecodeError as e:
        raise Exception(f"Tmap API 응답 JSON 파싱 실패: {str(e)} - 응답: {response.text[:200]}")

    return route_data



def extract_coordinates_from_route(route_data: dict) -> List[Tuple[float, float]]:
    """
    Tmap 경로 데이터에서 좌표 리스트 추출
    
    Args:
        route_data (dict): Tmap API 응답 데이터
        
    Returns:
        List[Tuple[float, float]]: (경도, 위도) 튜플 리스트
    """
    coordinates = []
    
    if "features" not in route_data:
        return coordinates
    
    for feature in route_data["features"]:
        geometry = feature.get("geometry", {})
        geom_type = geometry.get("type")
        coords = geometry.get("coordinates", [])
        
        if geom_type == "LineString":
            # LineString: [[lon, lat], [lon, lat], ...]
            coordinates.extend(coords)
        elif geom_type == "Point":
            # Point: [lon, lat]
            coordinates.append(coords)
    
    return coordinates


def create_route_linestring(coordinates: List[Tuple[float, float]]) -> LineString:
    """
    좌표 리스트로부터 LineString 생성
    
    Args:
        coordinates (List[Tuple[float, float]]): (경도, 위도) 튜플 리스트
        
    Returns:
        LineString: Shapely LineString 객체
    """
    if len(coordinates) < 2:
        raise ValueError("LineString을 생성하기 위해서는 최소 2개의 좌표가 필요합니다.")
    
    return LineString(coordinates)


def create_buffer_polygon(linestring: LineString, buffer_distance_meters: float = 100) -> Polygon:
    """
    LineString 주변에 버퍼 Polygon 생성
    
    Args:
        linestring (LineString): 경로 LineString
        buffer_distance_meters (float): 버퍼 거리 (미터). 기본값: 100m
        
    Returns:
        Polygon: 버퍼 영역 Polygon
        
    Note:
        WGS84 좌표계에서 대략적인 미터 변환:
        - 위도 1도 ≈ 111km
        - buffer_distance를 도(degree) 단위로 변환
    """
    # 미터를 도(degree)로 변환 (대략적인 값)
    # 위도 1도 = 약 111,000m
    buffer_distance_deg = buffer_distance_meters / 111000.0
    
    return linestring.buffer(buffer_distance_deg)


def calculate_safe_waypoints(
    route_polygon: Polygon,
    danger_points: List[Tuple[float, float]],
    danger_radius_meters: float = 50
) -> List[Tuple[float, float]]:
    """
    위험 지역을 제외한 안전 지역의 중심점들을 경유지로 계산
    
    Args:
        route_polygon (Polygon): 경로 버퍼 영역
        danger_points (List[Tuple[float, float]]): 위험 지역 좌표 리스트 (경도, 위도)
        danger_radius_meters (float): 위험 지역 반경 (미터). 기본값: 50m
        
    Returns:
        List[Tuple[float, float]]: 안전한 경유지 좌표 리스트 (경도, 위도)
    """
    # 미터를 도(degree)로 변환
    danger_radius_deg = danger_radius_meters / 111000.0
    
    # 안전 지역 계산 (전체 경로에서 위험 지역 제외)
    safe_area = route_polygon
    
    for lon, lat in danger_points:
        danger_circle = Point(lon, lat).buffer(danger_radius_deg)
        safe_area = safe_area.difference(danger_circle)
    
    # 안전 지역이 없거나 비어있으면 빈 리스트 반환
    if safe_area.is_empty:
        return []
    
    waypoints = []
    
    # MultiPolygon인 경우 (여러 개의 안전 지역으로 나뉜 경우)
    if safe_area.geom_type == 'MultiPolygon':
        for polygon in safe_area.geoms:
            centroid = polygon.centroid
            waypoints.append((centroid.x, centroid.y))
    # Polygon인 경우 (하나의 연속된 안전 지역)
    elif safe_area.geom_type == 'Polygon':
        centroid = safe_area.centroid
        waypoints.append((centroid.x, centroid.y))
    
    return waypoints


def find_nearby_dangers(
    route_polygon: Polygon,
    all_danger_points: List[dict],
    search_distance_meters: float = 200
) -> List[dict]:
    """
    경로 근처의 위험 지역 찾기
    
    Args:
        route_polygon (Polygon): 경로 버퍼 영역
        all_danger_points (List[dict]): 모든 위험 지역 정보 리스트
            각 항목은 {'longitude': float, 'latitude': float, ...} 형태
        search_distance_meters (float): 검색 거리 (미터). 기본값: 200m
        
    Returns:
        List[dict]: 경로 근처의 위험 지역 리스트
    """
    search_distance_deg = search_distance_meters / 111000.0
    expanded_route = route_polygon.buffer(search_distance_deg)
    
    nearby_dangers = []
    
    for danger in all_danger_points:
        lon = danger.get('longitude')
        lat = danger.get('latitude')
        
        if lon is None or lat is None:
            continue
        
        danger_point = Point(lon, lat)
        
        if expanded_route.contains(danger_point) or expanded_route.intersects(danger_point):
            nearby_dangers.append(danger)
    
    return nearby_dangers
