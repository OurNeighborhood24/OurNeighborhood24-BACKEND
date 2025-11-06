from typing import Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()


class CategoryClassificationResult(BaseModel):
    """카테고리 분류 결과 스키마"""
    category: str = Field(description="신고 문장에 가장 적합한 카테고리 이름")
    confidence_reason: str = Field(description="이 카테고리를 선택한 이유에 대한 간단한 설명")

class ReportClassifier:
    """
    신고 텍스트를 카테고리로 분류하는 LLM 기반 분류기
    """

    CATEGORIES = [
        "가로정비",
        "공원녹지",
        "교통-불법주차",
        "교통-장애인주차구역위반",
        "교통-거주자우선주차위반",
        "교통-기타",
        "도로",
        "소방안전",
        "청소-쓰레기무단투기",
        "청소-기타",
        "치수방재",
        "환경",
        "보건",
        "주택",
        "범죄",
        "기타"
    ]

    def __init__(self, model_name: str = "gemini-2.0-flash-exp", temperature: float = 0.0):
        # with_structured_output을 사용하기 위한 LLM 설정
        base_llm = ChatGoogleGenerativeAI(model=model_name, temperature=temperature)
        self.llm = base_llm.with_structured_output(CategoryClassificationResult)
        
        categories_str = "".join([f"- {c}" for c in self.CATEGORIES])

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "당신은 한국어 신고 텍스트를 주어진 카테고리 중 하나로 정확히 분류하는 AI 어시스턴트입니다."),
            ("human", f"""다음 신고 문장을 가장 적절한 카테고리로 분류하세요.

가능한 카테고리 목록:
{categories_str}

신고 문장:
{{text}}

반드시 위 목록에 있는 카테고리 중 하나를 선택하고, 선택한 이유를 간단히 설명하세요.""")
        ])

    def classify(self, text: str) -> Dict[str, str]:
        """
        신고 텍스트를 카테고리로 분류
        
        Args:
            text: 분류할 신고 텍스트
            
        Returns:
            Dict[str, str]: category와 confidence_reason을 포함하는 딕셔너리
        """
        try:
            # with_structured_output을 사용하면 Pydantic 모델이 직접 반환됨
            result: CategoryClassificationResult = self.llm.invoke(
                self.prompt.format_messages(text=text)
            )
            
            return {
                "category": result.category,
                "confidence_reason": result.confidence_reason
            }
        except Exception as e:
            # 분류 실패 시 기본 카테고리 반환
            print(f"Classification error: {e}")
            return {
                "category": "기타",
                "confidence_reason": f"분류 중 오류가 발생했습니다: {str(e)}"
            }


if __name__ == "__main__":
    classifier = ReportClassifier(model_name="gemini-2.0-flash-exp")

    examples = [
        "횡단보도 옆 가로등이 고장났어요",
        "공원에 쓰레기가 너무 많아요",
        "불법주차 차량이 도로를 막고 있습니다",
        "비가 올 때마다 하수구가 역류해요",
        "밤에 소음이 심해서 잠을 잘 수 없어요"
    ]

    for ex in examples:
        result = classifier.classify(ex)
        print(f"[{ex}] → {result['category']} ({result['confidence_reason']})")

