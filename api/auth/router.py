from fastapi import APIRouter, Depends, status, Response, Cookie, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from core.database import get_db
from core.dependencies import jwt_util, get_current_user_id
from core.config import get_settings
from app.auth.service import AuthService
from app.auth.schemas import (
    LoginRequest,
    TokenResponse,
    LogoutResponse
)
from core.util.cookie_util import CookieUtil

router = APIRouter()
settings = get_settings()


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="로그인",
    description="user_id와 비밀번호로 로그인합니다. Access Token은 응답 본문에, Refresh Token은 쿠키에 포함됩니다."
)
async def login(
    request: LoginRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    로그인 엔드포인트

    - **user_id**: 사용자 ID
    - **password**: 비밀번호

    **응답:**
    - Access Token은 응답 본문에 포함
    - Refresh Token은 HttpOnly 쿠키로 설정
    """
    auth_service = AuthService(db, jwt_util)
    result = auth_service.login(request)

    # Refresh Token을 쿠키에 설정
    CookieUtil.set_refresh_token_cookie(
        response=response,
        refresh_token=result["refresh_token"],
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60
    )

    # Access Token은 응답 본문으로 반환
    return TokenResponse(
        access_token=result["access_token"]
    )


@router.post(
    "/reissue",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="토큰 재발급",
    description="Refresh Token을 사용하여 새로운 Access Token을 발급받습니다."
)
async def reissue_token(
    refresh_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    """
    토큰 재발급 엔드포인트

    Refresh Token은 쿠키에서 자동으로 읽어옵니다.

    **응답:**
    - 새로운 Access Token
    """
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    auth_service = AuthService(db, jwt_util)
    new_access_token = auth_service.refresh_access_token(refresh_token)

    return TokenResponse(
        access_token=new_access_token,
    )


@router.delete(
    "/logout",
    response_model=LogoutResponse,
    status_code=status.HTTP_200_OK,
    summary="로그아웃",
    description="로그아웃하고 Refresh Token 쿠키를 삭제합니다."
)
async def logout(
    response: Response,
    user_id: int = Depends(get_current_user_id)
):
    """
    로그아웃 엔드포인트

    - Refresh Token 쿠키를 삭제합니다.
    - Access Token은 클라이언트에서 직접 삭제해야 합니다.
    """
    # Refresh Token 쿠키 삭제
    CookieUtil.delete_refresh_token_cookie(response)

    return LogoutResponse(
        message="Successfully logged out"
    )
