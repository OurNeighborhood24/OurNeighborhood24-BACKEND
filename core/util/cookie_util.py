from fastapi import Response
from datetime import timedelta


class CookieUtil:
    """쿠키 관리를 위한 유틸리티 클래스"""

    @staticmethod
    def set_refresh_token_cookie(
        response: Response,
        refresh_token: str,
        max_age: int = 7 * 24 * 60 * 60  # 7일 (초 단위)
    ) -> None:
        """
        Refresh Token을 쿠키에 설정

        Args:
            response: FastAPI Response 객체
            refresh_token: Refresh Token 값
            max_age: 쿠키 만료 시간 (초)
        """
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,  # JavaScript 접근 방지
            secure=False,  # HTTPS에서만 전송 (프로덕션에서는 True로 설정)
            samesite="lax",  # CSRF 방어
            max_age=max_age,
            path="/"
        )

    @staticmethod
    def delete_refresh_token_cookie(response: Response) -> None:
        """
        Refresh Token 쿠키 삭제

        Args:
            response: FastAPI Response 객체
        """
        response.delete_cookie(
            key="refresh_token",
            path="/"
        )
