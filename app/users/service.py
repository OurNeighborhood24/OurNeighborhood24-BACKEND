from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
from app.users.models import User, Region, UserRole
from app.users.schemas import UserRegisterRequest
from core.util.password_util import PasswordUtil


class UserService:
    """사용자 관련 비즈니스 로직"""

    def __init__(self, db: Session):
        self.db = db

    def get_user_by_user_id(self, user_id: str) -> Optional[User]:
        """
        user_id로 사용자 조회

        Args:
            user_id: 사용자 ID (문자열)

        Returns:
            사용자 객체 또는 None
        """
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        ID로 사용자 조회

        Args:
            user_id: 사용자 ID

        Returns:
            사용자 객체 또는 None
        """
        return self.db.query(User).filter(User.user_id == user_id).first()

    def get_region_by_id(self, region_id: int) -> Optional[Region]:
        """
        ID로 지역 조회

        Args:
            region_id: 지역 ID

        Returns:
            지역 객체 또는 None
        """
        return self.db.query(Region).filter(Region.region_id == region_id).first()

    def get_all_regions(self) -> List[Region]:
        """
        모든 지역 조회

        Returns:
            지역 목록
        """
        return self.db.query(Region).all()

    def register_user(self, request: UserRegisterRequest) -> User:
        """
        사용자 회원가입

        Args:
            request: 회원가입 요청 데이터

        Returns:
            생성된 사용자 객체

        Raises:
            HTTPException: 이메일 중복 또는 지역이 존재하지 않는 경우
        """
        # user_id 중복 체크
        existing_user = self.get_user_by_user_id(request.id)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User ID already registered"
            )

        # 지역 존재 여부 확인
        region = self.get_region_by_id(request.region_id)
        if not region:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid region_id"
            )

        # 비밀번호 해싱
        hashed_password = PasswordUtil.hash_password(request.password)

        # 사용자 생성
        new_user = User(
            id=request.id,
            password=hashed_password,
            region_id=request.region_id,
            role=UserRole.from_str(request.role)
        )

        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)

        return new_user

    def update_user_region(self, user_id: int, new_region_id: int) -> User:
        """
        사용자 지역 변경

        Args:
            user_id: 사용자 ID
            new_region_id: 새로운 지역 ID

        Returns:
            업데이트된 사용자 객체

        Raises:
            HTTPException: 사용자 또는 지역이 존재하지 않는 경우
        """
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        region = self.get_region_by_id(new_region_id)
        if not region:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid region_id"
            )

        user.region_id = new_region_id
        self.db.commit()
        self.db.refresh(user)

        return user
