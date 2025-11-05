from sqlalchemy import Column, BigInteger, String, Enum, ForeignKey, Integer
from sqlalchemy.orm import relationship
import enum
from core.database import Base


class UserRole(str, enum.Enum):
    """사용자 역할 Enum"""
    USER = "USER"
    ADMIN = "ADMIN"


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
    region_id = Column(BigInteger, ForeignKey("region.region_id"), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)  # 해싱된 비밀번호는 더 긴 길이 필요
    role = Column(Enum(UserRole), nullable=False, default=UserRole.USER)

    # 관계
    region = relationship("Region", back_populates="users")
