from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from fastapi import HTTPException, status


class JWTUtil:
    """JWT 토큰 생성 및 검증을 위한 유틸리티 클래스"""

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days

    def create_access_token(self, data: Dict[str, Any]) -> str:
        """
        Access Token 생성

        Args:
            data: 토큰에 포함할 페이로드 데이터

        Returns:
            생성된 JWT 토큰 문자열
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire, "type": "access"})

        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """
        Refresh Token 생성

        Args:
            data: 토큰에 포함할 페이로드 데이터

        Returns:
            생성된 JWT 토큰 문자열
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})

        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        """
        JWT 토큰 검증 및 디코딩

        Args:
            token: 검증할 JWT 토큰
            token_type: 토큰 타입 ("access" 또는 "refresh")

        Returns:
            디코딩된 페이로드

        Raises:
            HTTPException: 토큰이 유효하지 않거나 만료된 경우
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            # 토큰 타입 검증
            if payload.get("type") != token_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Invalid token type. Expected {token_type}",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            return payload

        except JWTError as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        JWT 토큰 디코딩 (검증 없이)

        Args:
            token: 디코딩할 JWT 토큰

        Returns:
            디코딩된 페이로드 또는 None
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={"verify_signature": False}
            )
            return payload
        except JWTError:
            return None

    def get_user_id_from_token(self, token: str) -> int:
        """
        토큰에서 사용자 ID 추출

        Args:
            token: JWT 토큰

        Returns:
            사용자 ID

        Raises:
            HTTPException: 토큰이 유효하지 않거나 user_id가 없는 경우
        """
        payload = self.verify_token(token)
        user_id = payload.get("user_id")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user_id

    def get_user_role_from_token(self, token: str) -> str:
        """
        토큰에서 사용자 역할 추출

        Args:
            token: JWT 토큰

        Returns:
            사용자 역할 (USER 또는 ADMIN)

        Raises:
            HTTPException: 토큰이 유효하지 않거나 role이 없는 경우
        """
        payload = self.verify_token(token)
        role = payload.get("role")

        if role is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return role