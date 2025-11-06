from typing import Any

from sqlalchemy import Column, BigInteger, String, Enum, ForeignKey, Integer
from sqlalchemy.orm import relationship
import enum
from core.database import Base



class UserRole(str, enum.Enum):
    """사용자 역할 Enum"""
    USER = "USER"
    ADMIN = "ADMIN"

    @classmethod
    def from_str(cls, value: str) -> "UserRole":
        """문자열을 UserRole Enum으로 변환"""
        try:
            return cls[value.upper()]  # Enum 이름으로 접근
        except KeyError:
            raise ValueError(f"Invalid user role: {value}")


class Region(Base):
    """지역 모델"""
    __tablename__ = "region"

    region_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    region_code = Column(Integer, unique=True, nullable=False, index=True)
    region_name = Column(String(255), nullable=False)

    # 관계
    users = relationship("User", back_populates="region")


class User(Base):
    """사용자 모델"""
    __tablename__ = "user"

    user_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    id = Column(String(255), unique=True, nullable=False, index=True)  # 사용자 ID (로그인용)
    region_id = Column(BigInteger, ForeignKey("region.region_id"), nullable=False)
    password = Column(String(255), nullable=False)  # 해싱된 비밀번호는 더 긴 길이 필요
    role = Column(Enum(UserRole), nullable=False, default=UserRole.USER)

    # 관계
    region = relationship("Region", back_populates="users")
