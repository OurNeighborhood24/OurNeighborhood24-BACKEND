import math
from typing import Tuple


class GeoUtil:
    """지리적 위치 계산 유틸리티"""

    # 지구 반지름 (미터)
    EARTH_RADIUS_M = 6371000

    @staticmethod
    def haversine_distance(
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """
        두 지점 간의 거리를 Haversine 공식으로 계산

        Args:
            lat1: 첫 번째 지점의 위도
            lon1: 첫 번째 지점의 경도
            lat2: 두 번째 지점의 위도
            lon2: 두 번째 지점의 경도

        Returns:
            두 지점 간의 거리 (미터)
        """
        # 위도, 경도를 라디안으로 변환
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        # 위도, 경도 차이
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        # Haversine 공식
        a = (
            math.sin(dlat / 2) ** 2 +
            math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.asin(math.sqrt(a))

        # 거리 계산 (미터)
        distance = GeoUtil.EARTH_RADIUS_M * c

        return distance

    @staticmethod
    def calculate_bounding_box(
            latitude: float,
            longitude: float,
            radius_m: float
    ) -> Tuple[float, float, float, float]:
        """
        중심점(lat, lon)과 반경(m)으로 경계 상자(bounding box)를 정확하게 계산
        """
        R = GeoUtil.EARTH_RADIUS_M  # 6371000m
        lat_rad = math.radians(latitude)
        lon_rad = math.radians(longitude)

        # 반경(m)을 위도/경도 차이(라디안)로 변환
        lat_delta = radius_m / R
        lon_delta = radius_m / (R * math.cos(lat_rad))

        # 다시 도 단위로 변환
        min_lat = math.degrees(lat_rad - lat_delta)
        max_lat = math.degrees(lat_rad + lat_delta)
        min_lon = math.degrees(lon_rad - lon_delta)
        max_lon = math.degrees(lon_rad + lon_delta)

        return min_lat, max_lat, min_lon, max_lon

    @staticmethod
    def is_within_radius(
        center_lat: float,
        center_lon: float,
        point_lat: float,
        point_lon: float,
        radius_m: float
    ) -> bool:
        """
        주어진 지점이 중심점으로부터 반경 내에 있는지 확인

        Args:
            center_lat: 중심점 위도
            center_lon: 중심점 경도
            point_lat: 확인할 지점의 위도
            point_lon: 확인할 지점의 경도
            radius_m: 반경 (미터)

        Returns:
            반경 내에 있으면 True, 아니면 False
        """
        distance = GeoUtil.haversine_distance(
            center_lat, center_lon, point_lat, point_lon
        )
        return distance <= radius_m
