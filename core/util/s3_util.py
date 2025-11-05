import boto3
from botocore.exceptions import ClientError
from fastapi import HTTPException, status, UploadFile
from typing import Optional
import uuid
from datetime import datetime
import os
from core.config import get_settings

settings = get_settings()


class S3Util:
    """AWS S3 파일 업로드 유틸리티"""

    def __init__(self):
        """S3 클라이언트 초기화"""
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.aws_access_key,
            aws_secret_access_key=settings.aws_secret_key,
            region_name=settings.aws_region
        )
        self.bucket_name = settings.aws_s3_bucket

    def _generate_unique_filename(self, original_filename: str) -> str:
        """
        고유한 파일명 생성

        Args:
            original_filename: 원본 파일명

        Returns:
            고유한 파일명
        """
        # 파일 확장자 추출
        _, ext = os.path.splitext(original_filename)

        # UUID와 타임스탬프를 결합하여 고유한 파일명 생성
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        unique_filename = f"{timestamp}_{unique_id}{ext}"

        return unique_filename

    def _validate_image_file(self, file: UploadFile) -> None:
        """
        이미지 파일 유효성 검사

        Args:
            file: 업로드할 파일

        Raises:
            HTTPException: 파일이 이미지가 아닌 경우
        """
        allowed_content_types = [
            "image/jpeg",
            "image/jpg",
            "image/png",
            "image/gif",
            "image/webp"
        ]

        if file.content_type not in allowed_content_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Allowed types: {', '.join(allowed_content_types)}"
            )

        # 파일 크기 검사
        if file.size and file.size > settings.max_upload_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds maximum allowed size ({settings.max_upload_size} bytes)"
            )

    async def upload_image(
        self,
        file: UploadFile,
        folder: str = "reports"
    ) -> str:
        """
        이미지 파일을 S3에 업로드

        Args:
            file: 업로드할 파일
            folder: S3 내 저장할 폴더명

        Returns:
            업로드된 파일의 public URL

        Raises:
            HTTPException: 업로드 실패 시
        """
        # 파일 유효성 검사
        self._validate_image_file(file)

        # 고유한 파일명 생성
        unique_filename = self._generate_unique_filename(file.filename)
        s3_key = f"{folder}/{unique_filename}"

        try:
            # 파일 내용 읽기
            file_content = await file.read()

            # S3에 업로드
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_content,
                ContentType=file.content_type
            )

            # Public URL 생성
            public_url = f"https://{self.bucket_name}.s3.{settings.aws_region}.amazonaws.com/{s3_key}"

            return public_url

        except ClientError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload file to S3: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unexpected error during file upload: {str(e)}"
            )
        finally:
            # 파일 포인터를 처음으로 되돌림
            await file.seek(0)

    def delete_image(self, image_url: str) -> bool:
        """
        S3에서 이미지 삭제

        Args:
            image_url: 삭제할 이미지의 URL

        Returns:
            삭제 성공 여부
        """
        try:
            # URL에서 S3 key 추출
            # 예: https://bucket.s3.region.amazonaws.com/folder/filename.jpg
            # -> folder/filename.jpg
            s3_key = image_url.split(f"{self.bucket_name}.s3.{settings.aws_region}.amazonaws.com/")[1]

            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )

            return True

        except Exception as e:
            print(f"Failed to delete file from S3: {str(e)}")
            return False


def get_s3_util() -> S3Util:
    """S3Util 인스턴스 반환"""
    return S3Util()
