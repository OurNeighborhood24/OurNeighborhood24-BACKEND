from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional, Dict, Any
from app.users.models import User
from app.auth.schemas import LoginRequest
from core.util.password_util import PasswordUtil
from core.util.jwt_util import JWTUtil


class AuthService:
    """인증 관련 비즈니스 로직"""

    def __init__(self, db: Session, jwt_util: JWTUtil):
        self.db = db
        self.jwt_util = jwt_util

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        사용자 인증

        Args:
            email: 사용자 이메일
            password: 비밀번호

        Returns:
            인증된 사용자 객체 또는 None
        """
        user = self.db.query(User).filter(User.email == email).first()

        if not user:
            return None

        if not PasswordUtil.verify_password(password, user.password):
            return None

        return user

    def login(self, request: LoginRequest) -> Dict[str, Any]:
        """
        로그인 처리

        Args:
            request: 로그인 요청 데이터

        Returns:
            토큰 정보 딕셔너리

        Raises:
            HTTPException: 인증 실패 시
        """
        user = self.authenticate_user(request.email, request.password)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # JWT 페이로드 생성
        payload = {
            "user_id": user.user_id,
            "email": user.email,
            "role": user.role.value
        }

        # Access Token과 Refresh Token 생성
        access_token = self.jwt_util.create_access_token(payload)
        refresh_token = self.jwt_util.create_refresh_token(payload)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user
        }

    def refresh_access_token(self, refresh_token: str) -> str:
        """
        Access Token 재발급

        Args:
            refresh_token: Refresh Token

        Returns:
            새로운 Access Token

        Raises:
            HTTPException: Refresh Token이 유효하지 않은 경우
        """
        # Refresh Token 검증
        payload = self.jwt_util.verify_token(refresh_token, token_type="refresh")

        # 사용자 존재 확인
        user_id = payload.get("user_id")
        user = self.db.query(User).filter(User.user_id == user_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 새로운 Access Token 생성
        new_payload = {
            "user_id": user.user_id,
            "email": user.email,
            "role": user.role.value
        }

        new_access_token = self.jwt_util.create_access_token(new_payload)

        return new_access_token
