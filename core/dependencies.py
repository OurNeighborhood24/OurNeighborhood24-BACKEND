from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from core.database import get_db
from core.util.jwt_util import JWTUtil
from core.config import get_settings

settings = get_settings()
security = HTTPBearer()

# JWT 유틸리티 인스턴스
jwt_util = JWTUtil(
    secret_key=settings.secret_key,
    algorithm=settings.algorithm,
    access_token_expire_minutes=settings.access_token_expire_minutes,
    refresh_token_expire_days=settings.refresh_token_expire_days
)


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> int:
    """
    현재 인증된 사용자의 ID를 반환

    Args:
        credentials: HTTP Authorization 헤더

    Returns:
        사용자 ID

    Raises:
        HTTPException: 인증 실패 시
    """
    token = credentials.credentials
    user_id = jwt_util.get_user_id_from_token(token)
    return user_id


async def get_current_user_role(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    현재 인증된 사용자의 역할을 반환

    Args:
        credentials: HTTP Authorization 헤더

    Returns:
        사용자 역할 (USER 또는 ADMIN)

    Raises:
        HTTPException: 인증 실패 시
    """
    token = credentials.credentials
    role = jwt_util.get_user_role_from_token(token)
    return role


async def require_admin(
    role: str = Depends(get_current_user_role)
) -> None:
    """
    관리자 권한 확인

    Args:
        role: 사용자 역할

    Raises:
        HTTPException: 관리자가 아닌 경우
    """
    if role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )


async def get_optional_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[int]:
    """
    선택적으로 현재 사용자 ID를 반환 (인증되지 않은 경우 None)

    Args:
        credentials: HTTP Authorization 헤더 (선택적)

    Returns:
        사용자 ID 또는 None
    """
    if credentials is None:
        return None

    try:
        token = credentials.credentials
        user_id = jwt_util.get_user_id_from_token(token)
        return user_id
    except HTTPException:
        return None