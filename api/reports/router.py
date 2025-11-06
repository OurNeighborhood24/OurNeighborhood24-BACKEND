from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from core.database import get_db
from core.dependencies import get_current_user_id, require_admin
from app.reports.service import CategoryService, ReportService
from core.util.s3_util import get_s3_util
from core.llm.LLM import ReportClassifier
from app.reports.schemas import (
    CategoryResponse,
    ReportCreateRequest,
    ReportResponse,
    ReportDetailResponse,
    ReportUpdateRequest,
    ReportStateUpdateRequest,
    ReportAnswerCreateRequest,
    ReportAnswerResponse,
    ReportWithAnswerResponse,
    PaginatedReportResponse,
    CategoryRecommendationResponse
)

router = APIRouter()


@router.get(
    "/categories",
    response_model=List[CategoryResponse],
    status_code=status.HTTP_200_OK,
    summary="카테고리 목록 조회",
    description="모든 신고 카테고리 목록을 조회합니다."
)
async def get_categories(db: Session = Depends(get_db)):
    """
    카테고리 목록 조회 엔드포인트

    모든 신고 카테고리를 반환합니다. 인증 불필요.
    """
    category_service = CategoryService(db)
    categories = category_service.get_all_categories()

    return [
        CategoryResponse(
            category_id=category.category_id,
            category_name=category.category_name
        )
        for category in categories
    ]


@router.get(
    "/categories/recommend",
    response_model=CategoryRecommendationResponse,
    status_code=status.HTTP_200_OK,
    summary="카테고리 추천",
    description="신고 내용을 분석하여 적절한 카테고리를 AI로 추천합니다. 인증 불필요."
)
async def recommend_category(text: str):
    """
    카테고리 추천 엔드포인트

    신고 내용 텍스트를 분석하여 가장 적절한 카테고리를 추천합니다.

    - **text**: 신고 내용 텍스트 (query parameter)
    
    **응답:**
    - category: 추천된 카테고리 이름
    - reason: 해당 카테고리를 선택한 이유
    """
    classifier = ReportClassifier(model_name="gemini-2.0-flash-exp")
    result = classifier.classify(text)
    
    return CategoryRecommendationResponse(
        category=result["category"],
        reason=result["confidence_reason"]
    )


@router.post(
    "/images",
    status_code=status.HTTP_201_CREATED,
    summary="신고 이미지 업로드",
    description="신고용 이미지를 S3에 업로드하고 public URL을 반환합니다."
)
async def upload_report_image(
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id)
):
    """
    신고 이미지 업로드 엔드포인트

    - **file**: 업로드할 이미지 파일 (jpg, jpeg, png, gif, webp)
    - 최대 파일 크기: 10MB

    **응답:**
    - image_url: 업로드된 이미지의 public URL
    """
    s3_util = get_s3_util()
    image_url = await s3_util.upload_image(file, folder="reports")

    return {
        "message": "Image uploaded successfully",
        "image_url": image_url
    }


@router.post(
    "",
    response_model=ReportDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="신고하기",
    description="새로운 신고를 등록합니다."
)
async def create_report(
    request: ReportCreateRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    신고 생성 엔드포인트

    - **category_id**: 카테고리 ID
    - **latitude**: 위도
    - **longitude**: 경도
    - **title**: 신고 제목
    - **description**: 신고 내용
    - **image_url**: 이미지 URL (선택)
    """
    report_service = ReportService(db)
    report = report_service.create_report(user_id, request)

    return ReportDetailResponse(
        report_id=report.report_id,
        writer_id=report.writer_id,
        category=CategoryResponse(
            category_id=report.category.category_id,
            category_name=report.category.category_name
        ),
        latitude=report.latitude,
        longitude=report.longitude,
        title=report.title,
        description=report.description,
        image_url=report.image_url,
        state=report.state.value,
        created_at=report.created_at
    )


@router.get(
    "/map",
    response_model=List[ReportDetailResponse],
    status_code=status.HTTP_200_OK,
    summary="신고 조회 (지도)",
    description="위치 기반으로 반경 내의 신고를 조회합니다. 인증 불필요."
)
async def get_reports_by_location(
    latitude: float,
    longitude: float,
    radius: int = 1000,
    category: Optional[int] = None,
    limit: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    지도용 신고 조회 엔드포인트

    위도/경도를 기준으로 반경 내의 신고를 조회합니다.

    - **latitude**: 중심점 위도 (필수)
    - **longitude**: 중심점 경도 (필수)
    - **radius**: 검색 반경 (미터, default: 1000)
    - **category**: 카테고리 ID 필터 (선택)
    - **limit**: 최대 조회 개수 (선택)
    """
    report_service = ReportService(db)
    reports = report_service.get_reports_by_location(
        latitude=latitude,
        longitude=longitude,
        radius_m=radius,
        category_id=category,
        limit=limit
    )

    return [
        ReportDetailResponse(
            report_id=report.report_id,
            writer_id=report.writer_id,
            category=CategoryResponse(
                category_id=report.category.category_id,
                category_name=report.category.category_name
            ),
            latitude=report.latitude,
            longitude=report.longitude,
            title=report.title,
            description=report.description,
            image_url=report.image_url,
            state=report.state.value,
            created_at=report.created_at
        )
        for report in reports
    ]


@router.get(
    "/my",
    response_model=List[ReportDetailResponse],
    status_code=status.HTTP_200_OK,
    summary="내 신고 조회",
    description="현재 로그인한 사용자의 신고 목록을 조회합니다."
)
async def get_my_reports(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    내 신고 조회 엔드포인트

    현재 로그인한 사용자가 작성한 신고 목록을 반환합니다.
    """
    report_service = ReportService(db)
    reports = report_service.get_reports_by_user(user_id)

    return [
        ReportDetailResponse(
            report_id=report.report_id,
            writer_id=report.writer_id,
            category=CategoryResponse(
                category_id=report.category.category_id,
                category_name=report.category.category_name
            ),
            latitude=report.latitude,
            longitude=report.longitude,
            title=report.title,
            description=report.description,
            image_url=report.image_url,
            state=report.state.value,
            created_at=report.created_at
        )
        for report in reports
    ]


@router.get(
    "/answers",
    response_model=List[ReportWithAnswerResponse],
    status_code=status.HTTP_200_OK,
    summary="응답한 신고 목록 조회 (관리자)",
    description="답변이 있는 신고 목록을 조회합니다. 관리자 권한 필요."
)
async def get_reports_with_answers(
    _: None = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    답변이 있는 신고 목록 조회 엔드포인트 (관리자용)

    답변이 작성된 신고와 답변을 함께 반환합니다.
    """
    report_service = ReportService(db)
    reports = report_service.get_reports_with_answers()

    return [
        ReportWithAnswerResponse(
            report=ReportDetailResponse(
                report_id=report.report_id,
                writer_id=report.writer_id,
                category=CategoryResponse(
                    category_id=report.category.category_id,
                    category_name=report.category.category_name
                ),
                latitude=report.latitude,
                longitude=report.longitude,
                title=report.title,
                description=report.description,
                image_url=report.image_url,
                state=report.state.value,
                created_at=report.created_at
            ),
            answers=[
                ReportAnswerResponse(
                    report_answer_id=answer.report_answer_id,
                    report_id=answer.report_id,
                    writer_id=answer.writer_id,
                    answer=answer.answer,
                    state=answer.state,
                    created_at=answer.created_at
                )
                for answer in report.answers
            ]
        )
        for report in reports
    ]


@router.patch(
    "/{report_id}",
    response_model=ReportDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="내 신고 수정",
    description="자신이 작성한 신고를 수정합니다."
)
async def update_report(
    report_id: int,
    request: ReportUpdateRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    신고 수정 엔드포인트

    - **report_id**: 신고 ID (경로 파라미터)
    - 수정 가능한 필드: category_id, latitude, longitude, title, description, image_url
    """
    report_service = ReportService(db)
    report = report_service.update_report(report_id, user_id, request)

    return ReportDetailResponse(
        report_id=report.report_id,
        writer_id=report.writer_id,
        category=CategoryResponse(
            category_id=report.category.category_id,
            category_name=report.category.category_name
        ),
        latitude=report.latitude,
        longitude=report.longitude,
        title=report.title,
        description=report.description,
        image_url=report.image_url,
        state=report.state.value,
        created_at=report.created_at
    )


@router.delete(
    "/{report_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="내 신고 삭제",
    description="자신이 작성한 신고를 삭제합니다."
)
async def delete_report(
    report_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    신고 삭제 엔드포인트

    - **report_id**: 신고 ID (경로 파라미터)
    """
    report_service = ReportService(db)
    report_service.delete_report(report_id, user_id)
    return None


@router.get(
    "/{report_id}",
    response_model=ReportWithAnswerResponse,
    status_code=status.HTTP_200_OK,
    summary="신고 상세 조회",
    description="신고 ID로 신고의 상세 정보를 조회합니다. 신고 답변도 함께 조회됩니다. 인증 불필요."
)
async def get_report_detail(
    report_id: int,
    db: Session = Depends(get_db)
):
    """
    신고 상세 조회 엔드포인트

    신고 정보와 답변을 함께 조회합니다.

    - **report_id**: 신고 ID (경로 파라미터)
    """
    report_service = ReportService(db)
    report = report_service.get_report_by_id(report_id)

    if not report:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )

    return ReportWithAnswerResponse(
        report=ReportDetailResponse(
            report_id=report.report_id,
            writer_id=report.writer_id,
            category=CategoryResponse(
                category_id=report.category.category_id,
                category_name=report.category.category_name
            ),
            latitude=report.latitude,
            longitude=report.longitude,
            title=report.title,
            description=report.description,
            image_url=report.image_url,
            state=report.state.value,
            created_at=report.created_at
        ),
        answers=[
            ReportAnswerResponse(
                report_answer_id=answer.report_answer_id,
                report_id=answer.report_id,
                writer_id=answer.writer_id,
                answer=answer.answer,
                state=answer.state,
                created_at=answer.created_at
            )
            for answer in report.answers
        ]
    )


@router.get(
    "",
    response_model=PaginatedReportResponse,
    status_code=status.HTTP_200_OK,
    summary="신고 목록 조회",
    description="모든 신고 목록을 페이지네이션하여 조회합니다. 인증 불필요."
)
async def get_all_reports(
    offset: int = 0,
    size: int = 15,
    db: Session = Depends(get_db)
):
    """
    신고 목록 조회 엔드포인트

    오프셋 기반 페이지네이션을 사용합니다.

    - **offset**: 시작 위치 (default: 0)
    - **size**: 페이지 크기 (default: 15)
    """
    report_service = ReportService(db)
    reports, total = report_service.get_all_reports(offset=offset, size=size)

    items = [
        ReportDetailResponse(
            report_id=report.report_id,
            writer_id=report.writer_id,
            category=CategoryResponse(
                category_id=report.category.category_id,
                category_name=report.category.category_name
            ),
            latitude=report.latitude,
            longitude=report.longitude,
            title=report.title,
            description=report.description,
            image_url=report.image_url,
            state=report.state.value,
            created_at=report.created_at
        )
        for report in reports
    ]

    return PaginatedReportResponse(
        total=total,
        offset=offset,
        size=size,
        items=items
    )


@router.patch(
    "/{report_id}/state",
    response_model=ReportDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="신고 상태 전환 (관리자)",
    description="신고의 상태를 변경합니다. 관리자 권한 필요."
)
async def update_report_state(
    report_id: int,
    request: ReportStateUpdateRequest,
    _: None = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    신고 상태 전환 엔드포인트 (관리자용)

    - **report_id**: 신고 ID (경로 파라미터)
    - **state**: 새로운 상태 (PENDING, CHECKED, PROCESSING, COMPLETED)
    """
    report_service = ReportService(db)
    report = report_service.update_report_state(report_id, request)

    return ReportDetailResponse(
        report_id=report.report_id,
        writer_id=report.writer_id,
        category=CategoryResponse(
            category_id=report.category.category_id,
            category_name=report.category.category_name
        ),
        latitude=report.latitude,
        longitude=report.longitude,
        title=report.title,
        description=report.description,
        image_url=report.image_url,
        state=report.state.value,
        created_at=report.created_at
    )


@router.post(
    "/{report_id}/answer",
    response_model=ReportAnswerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="신고 응답하기 (관리자)",
    description="신고에 대한 답변을 작성합니다. 관리자 권한 필요."
)
async def create_report_answer(
    report_id: int,
    request: ReportAnswerCreateRequest,
    admin_id: int = Depends(get_current_user_id),
    _: None = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    신고 답변 생성 엔드포인트 (관리자용)

    - **report_id**: 신고 ID (경로 파라미터)
    - **answer**: 답변 내용
    - **state**: 현재 신고의 상태가 자동으로 스냅샷으로 저장됩니다
    """
    report_service = ReportService(db)
    answer = report_service.create_report_answer(report_id, admin_id, request)

    return ReportAnswerResponse(
        report_answer_id=answer.report_answer_id,
        report_id=answer.report_id,
        writer_id=answer.writer_id,
        answer=answer.answer,
        state=answer.state,
        created_at=answer.created_at
    )
