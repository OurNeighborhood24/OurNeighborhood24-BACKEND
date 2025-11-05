from sqlalchemy import Column, BigInteger, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base


class Notification(Base):
    """공지사항 모델"""
    __tablename__ = "notification"

    notification_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    writer_id = Column(BigInteger, ForeignKey("user.user_id"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # 관계
    writer = relationship("User")
