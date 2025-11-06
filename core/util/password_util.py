from passlib.context import CryptContext

# 비밀번호 해싱 컨텍스트
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__default_rounds=12
)
ㅌ

class PasswordUtil:
    """비밀번호 해싱 및 검증을 위한 유틸리티 클래스"""

    @staticmethod
    def hash_password(password: str) -> str:
        """
        비밀번호 해싱

        Args:
            password: 평문 비밀번호

        Returns:
            해싱된 비밀번호
        """
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        비밀번호 검증

        Args:
            plain_password: 평문 비밀번호
            hashed_password: 해싱된 비밀번호

        Returns:
            비밀번호 일치 여부
        """
        return pwd_context.verify(plain_password, hashed_password)
