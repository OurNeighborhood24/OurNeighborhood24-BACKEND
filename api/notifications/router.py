from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from core.database import get_db
from core.dependencies import get_current_user_id, require_admin
from app.notifications.service import NotificationService
from app.notifications.schemas import (
    NotificationCreateRequest,
    NotificationUpdateRequest,
    NotificationResponse,
    PaginatedNotificationResponse
)

router = APIRouter()


@router.post(
    "",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="공지 등록",
    description="새로운 공지사항을 등록합니다. 관리자 권한 필요."
)
async def create_notification(
    request: NotificationCreateRequest,
    admin_id: int = Depends(get_current_user_id),
    _: None = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    공지사항 생성 엔드포인트 (관리자용)

    - **title**: 공지사항 제목
    - **content**: 공지사항 내용
    """
    notification_service = NotificationService(db)
    notification = notification_service.create_notification(admin_id, request)

    return NotificationResponse(
        notification_id=notification.notification_id,
        writer_id=notification.writer_id,
        title=notification.title,
        content=notification.content,
        created_at=notification.created_at
    )


@router.get(
    "",
    response_model=PaginatedNotificationResponse,
    status_code=status.HTTP_200_OK,
    summary="공지 조회",
    description="공지사항 목록을 페이지네이션하여 조회합니다. 인증 불필요."
)
async def get_notifications(
    offset: int = 0,
    size: int = 15,
    db: Session = Depends(get_db)
):
    """
    공지사항 목록 조회 엔드포인트

    오프셋 기반 페이지네이션을 사용합니다. 최신순으로 정렬됩니다.

    - **offset**: 시작 위치 (default: 0)
    - **size**: 페이지 크기 (default: 15)
    """
    notification_service = NotificationService(db)
    notifications, total = notification_service.get_all_notifications(
        offset=offset,
        size=size
    )

    items = [
        NotificationResponse(
            notification_id=notification.notification_id,
            writer_id=notification.writer_id,
            title=notification.title,
            content=notification.content,
            created_at=notification.created_at
        )
        for notification in notifications
    ]

    return PaginatedNotificationResponse(
        total=total,
        offset=offset,
        size=size,
        items=items
    )


@router.patch(
    "/{notification_id}",
    response_model=NotificationResponse,
    status_code=status.HTTP_200_OK,
    summary="공지 수정",
    description="공지사항을 수정합니다. 관리자 권한 필요."
)
async def update_notification(
    notification_id: int,
    request: NotificationUpdateRequest,
    _: None = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    공지사항 수정 엔드포인트 (관리자용)

    - **notification_id**: 공지사항 ID (경로 파라미터)
    - **title**: 공지사항 제목 (선택)
    - **content**: 공지사항 내용 (선택)
    """
    notification_service = NotificationService(db)
    notification = notification_service.update_notification(notification_id, request)

    return NotificationResponse(
        notification_id=notification.notification_id,
        writer_id=notification.writer_id,
        title=notification.title,
        content=notification.content,
        created_at=notification.created_at
    )


@router.delete(
    "/{notification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="공지 삭제",
    description="공지사항을 삭제합니다. 관리자 권한 필요."
)
async def delete_notification(
    notification_id: int,
    _: None = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    공지사항 삭제 엔드포인트 (관리자용)

    - **notification_id**: 공지사항 ID (경로 파라미터)
    """
    notification_service = NotificationService(db)
    notification_service.delete_notification(notification_id)
    return None
