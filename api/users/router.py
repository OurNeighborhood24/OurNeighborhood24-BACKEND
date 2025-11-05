from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from core.database import get_db
from core.dependencies import get_current_user_id
from app.users.service import UserService
from app.users.schemas import (
    UserRegisterRequest,
    UserRegisterResponse,
    UserResponse,
    RegionResponse
)

router = APIRouter(prefix="/users")


@router.post(
    "/register",
    response_model=UserRegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="회원가입",
    description="새로운 사용자를 등록합니다."
)
async def register(
    request: UserRegisterRequest,
    db: Session = Depends(get_db)
):
    """
    회원가입 엔드포인트

    - **email**: 사용자 이메일 (고유해야 함)
    - **password**: 비밀번호 (8-30자)
    - **region_id**: 지역 ID
    """
    user_service = UserService(db)
    user = user_service.register_user(request)

    return UserRegisterResponse(
        message="User registered successfully",
        user=UserResponse(
            user_id=user.user_id,
            email=user.email,
            role=user.role.value,
            region=RegionResponse(
                region_id=user.region.region_id,
                region_code=user.region.region_code,
                region_name=user.region.region_name
            )
        )
    )


@router.get(
    "/regions",
    response_model=List[RegionResponse],
    status_code=status.HTTP_200_OK,
    summary="지역 목록 조회",
    description="모든 지역 목록을 조회합니다."
)
async def get_regions(db: Session = Depends(get_db)):
    """
    지역 목록 조회 엔드포인트

    모든 지역 목록을 반환합니다.
    """
    user_service = UserService(db)
    regions = user_service.get_all_regions()

    return [
        RegionResponse(
            region_id=region.region_id,
            region_code=region.region_code,
            region_name=region.region_name
        )
        for region in regions
    ]


@router.get(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="본인 정보 조회",
    description="현재 로그인한 사용자의 정보를 조회합니다."
)
async def get_my_info(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    본인 정보 조회 엔드포인트

    JWT 토큰을 통해 인증된 사용자의 정보를 반환합니다.
    """
    user_service = UserService(db)
    user = user_service.get_user_by_id(user_id)

    if not user:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse(
        user_id=user.user_id,
        email=user.email,
        role=user.role.value,
        region=RegionResponse(
            region_id=user.region.region_id,
            region_code=user.region.region_code,
            region_name=user.region.region_name
        )
    )


@router.patch(
    "/my/region",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="지역 설정 변경",
    description="현재 로그인한 사용자의 지역을 변경합니다."
)
async def update_my_region(
    region_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    지역 설정 변경 엔드포인트

    - **region_id**: 새로운 지역 ID
    """
    user_service = UserService(db)
    user = user_service.update_user_region(user_id, region_id)

    return UserResponse(
        user_id=user.user_id,
        email=user.email,
        role=user.role.value,
        region=RegionResponse(
            region_id=user.region.region_id,
            region_code=user.region.region_code,
            region_name=user.region.region_name
        )
    )
