from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
from app.reports.models import Category, Report, ReportAnswer, ReportState
from app.reports.schemas import (
    ReportCreateRequest,
    ReportUpdateRequest,
    ReportStateUpdateRequest,
    ReportAnswerCreateRequest
)


class CategoryService:
    """카테고리 관련 비즈니스 로직"""

    def __init__(self, db: Session):
        self.db = db

    def get_all_categories(self) -> List[Category]:
        """
        모든 카테고리 조회

        Returns:
            카테고리 목록
        """
        return self.db.query(Category).all()

    def get_category_by_id(self, category_id: int) -> Optional[Category]:
        """
        ID로 카테고리 조회

        Args:
            category_id: 카테고리 ID

        Returns:
            카테고리 객체 또는 None
        """
        return self.db.query(Category).filter(Category.category_id == category_id).first()


class ReportService:
    """신고 관련 비즈니스 로직"""

    def __init__(self, db: Session):
        self.db = db

    def create_report(self, user_id: int, request: ReportCreateRequest) -> Report:
        """
        신고 생성

        Args:
            user_id: 작성자 ID
            request: 신고 생성 요청 데이터

        Returns:
            생성된 신고 객체

        Raises:
            HTTPException: 카테고리가 존재하지 않는 경우
        """
        # 카테고리 존재 여부 확인
        category = self.db.query(Category).filter(
            Category.category_id == request.category_id
        ).first()

        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid category_id"
            )

        # 신고 생성
        new_report = Report(
            writer_id=user_id,
            category_id=request.category_id,
            latitude=request.latitude,
            longitude=request.longitude,
            title=request.title,
            description=request.description,
            image_url=request.image_url,
            state=ReportState.PENDING
        )

        self.db.add(new_report)
        self.db.commit()
        self.db.refresh(new_report)

        return new_report

    def get_report_by_id(self, report_id: int) -> Optional[Report]:
        """
        ID로 신고 조회

        Args:
            report_id: 신고 ID

        Returns:
            신고 객체 또는 None
        """
        return self.db.query(Report).filter(Report.report_id == report_id).first()

    def get_reports_by_user(self, user_id: int) -> List[Report]:
        """
        사용자의 신고 목록 조회

        Args:
            user_id: 사용자 ID

        Returns:
            신고 목록
        """
        return self.db.query(Report).filter(Report.writer_id == user_id).all()

    def get_all_reports(self, offset: int = 0, size: int = 15) -> tuple[List[Report], int]:
        """
        모든 신고 조회 (페이지네이션)

        Args:
            offset: 시작 위치 (default: 0)
            size: 페이지 크기 (default: 15)

        Returns:
            (신고 목록, 전체 신고 수) 튜플
        """
        # 전체 신고 수 조회
        total = self.db.query(Report).count()

        # 페이지네이션된 신고 목록 조회
        reports = self.db.query(Report).offset(offset).limit(size).all()

        return reports, total

    def update_report(
        self,
        report_id: int,
        user_id: int,
        request: ReportUpdateRequest
    ) -> Report:
        """
        신고 수정

        Args:
            report_id: 신고 ID
            user_id: 사용자 ID
            request: 신고 수정 요청 데이터

        Returns:
            수정된 신고 객체

        Raises:
            HTTPException: 신고가 존재하지 않거나 권한이 없는 경우
        """
        report = self.get_report_by_id(report_id)

        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )

        # 작성자 확인
        if report.writer_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this report"
            )

        # 수정 가능한 필드만 업데이트
        if request.category_id is not None:
            # 카테고리 존재 여부 확인
            category = self.db.query(Category).filter(
                Category.category_id == request.category_id
            ).first()
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid category_id"
                )
            report.category_id = request.category_id

        if request.latitude is not None:
            report.latitude = request.latitude

        if request.longitude is not None:
            report.longitude = request.longitude

        if request.title is not None:
            report.title = request.title

        if request.description is not None:
            report.description = request.description

        if request.image_url is not None:
            report.image_url = request.image_url

        self.db.commit()
        self.db.refresh(report)

        return report

    def delete_report(self, report_id: int, user_id: int) -> None:
        """
        신고 삭제

        Args:
            report_id: 신고 ID
            user_id: 사용자 ID

        Raises:
            HTTPException: 신고가 존재하지 않거나 권한이 없는 경우
        """
        report = self.get_report_by_id(report_id)

        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )

        # 작성자 확인
        if report.writer_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this report"
            )

        self.db.delete(report)
        self.db.commit()

    def update_report_state(
        self,
        report_id: int,
        request: ReportStateUpdateRequest
    ) -> Report:
        """
        신고 상태 변경 (관리자용)

        Args:
            report_id: 신고 ID
            request: 상태 변경 요청 데이터

        Returns:
            수정된 신고 객체

        Raises:
            HTTPException: 신고가 존재하지 않거나 유효하지 않은 상태인 경우
        """
        report = self.get_report_by_id(report_id)

        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )

        # 상태 검증
        try:
            new_state = ReportState(request.state)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid state value"
            )

        report.state = new_state
        self.db.commit()
        self.db.refresh(report)

        return report

    def create_report_answer(
        self,
        report_id: int,
        admin_id: int,
        request: ReportAnswerCreateRequest
    ) -> ReportAnswer:
        """
        신고 답변 생성 (관리자용)

        Args:
            report_id: 신고 ID
            admin_id: 관리자 ID
            request: 답변 생성 요청 데이터

        Returns:
            생성된 답변 객체

        Raises:
            HTTPException: 신고가 존재하지 않거나 이미 답변이 있는 경우
        """
        report = self.get_report_by_id(report_id)

        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )

        # 이미 답변이 있는지 확인
        existing_answer = self.db.query(ReportAnswer).filter(
            ReportAnswer.report_id == report_id
        ).first()

        if existing_answer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Report already has an answer"
            )

        # 답변 생성
        new_answer = ReportAnswer(
            report_id=report_id,
            writer_id=admin_id,
            answer=request.answer,
            state=request.state
        )

        self.db.add(new_answer)
        self.db.commit()
        self.db.refresh(new_answer)

        return new_answer

    def get_reports_with_answers(self) -> List[Report]:
        """
        답변이 있는 신고 목록 조회 (관리자용)

        Returns:
            답변이 있는 신고 목록
        """
        return self.db.query(Report).join(ReportAnswer).all()
