from sqlalchemy import Column, BigInteger, String, Text, Float, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from core.database import Base


class ReportState(str, enum.Enum):
    """신고 상태 Enum"""
    PENDING = "PENDING"
    CHECKED = "CHECKED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"


class Category(Base):
    """카테고리 모델"""
    __tablename__ = "category"

    category_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    category_name = Column(Text, nullable=False)

    # 관계
    reports = relationship("Report", back_populates="category")


class Report(Base):
    """신고 모델"""
    __tablename__ = "report"

    report_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    writer_id = Column(BigInteger, ForeignKey("user.user_id"), nullable=False)
    category_id = Column(BigInteger, ForeignKey("category.category_id"), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    image_url = Column(Text, nullable=True)
    state = Column(Enum(ReportState), nullable=False, default=ReportState.PENDING)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # 관계
    writer = relationship("User")
    category = relationship("Category", back_populates="reports")
    answers = relationship("ReportAnswer", back_populates="report")


class ReportAnswer(Base):
    """신고 답변 모델"""
    __tablename__ = "report_answer"

    report_answer_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    report_id = Column(BigInteger, ForeignKey("report.report_id"), nullable=False)
    writer_id = Column(BigInteger, ForeignKey("user.user_id"), nullable=False)
    answer = Column(Text, nullable=False)
    state = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # 관계
    report = relationship("Report", back_populates="answers")
    writer = relationship("User")
