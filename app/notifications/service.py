from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
from app.notifications.models import Notification
from app.notifications.schemas import (
    NotificationCreateRequest,
    NotificationUpdateRequest
)


class NotificationService:
    """공지사항 관련 비즈니스 로직"""

    def __init__(self, db: Session):
        self.db = db

    def create_notification(
        self,
        admin_id: int,
        request: NotificationCreateRequest
    ) -> Notification:
        """
        공지사항 생성

        Args:
            admin_id: 관리자 ID
            request: 공지사항 생성 요청 데이터

        Returns:
            생성된 공지사항 객체
        """
        new_notification = Notification(
            writer_id=admin_id,
            title=request.title,
            content=request.content
        )

        self.db.add(new_notification)
        self.db.commit()
        self.db.refresh(new_notification)

        return new_notification

    def get_notification_by_id(self, notification_id: int) -> Optional[Notification]:
        """
        ID로 공지사항 조회

        Args:
            notification_id: 공지사항 ID

        Returns:
            공지사항 객체 또는 None
        """
        return self.db.query(Notification).filter(
            Notification.notification_id == notification_id
        ).first()

    def get_all_notifications(
        self,
        offset: int = 0,
        size: int = 15
    ) -> tuple[List[Notification], int]:
        """
        모든 공지사항 조회 (페이지네이션)

        Args:
            offset: 시작 위치 (default: 0)
            size: 페이지 크기 (default: 15)

        Returns:
            (공지사항 목록, 전체 공지사항 수) 튜플
        """
        # 전체 공지사항 수 조회
        total = self.db.query(Notification).count()

        # 페이지네이션된 공지사항 목록 조회 (최신순)
        notifications = self.db.query(Notification).order_by(
            Notification.created_at.desc()
        ).offset(offset).limit(size).all()

        return notifications, total

    def update_notification(
        self,
        notification_id: int,
        request: NotificationUpdateRequest
    ) -> Notification:
        """
        공지사항 수정

        Args:
            notification_id: 공지사항 ID
            request: 공지사항 수정 요청 데이터

        Returns:
            수정된 공지사항 객체

        Raises:
            HTTPException: 공지사항이 존재하지 않는 경우
        """
        notification = self.get_notification_by_id(notification_id)

        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )

        # 수정 가능한 필드만 업데이트
        if request.title is not None:
            notification.title = request.title

        if request.content is not None:
            notification.content = request.content

        self.db.commit()
        self.db.refresh(notification)

        return notification

    def delete_notification(self, notification_id: int) -> None:
        """
        공지사항 삭제

        Args:
            notification_id: 공지사항 ID

        Raises:
            HTTPException: 공지사항이 존재하지 않는 경우
        """
        notification = self.get_notification_by_id(notification_id)

        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )

        self.db.delete(notification)
        self.db.commit()
