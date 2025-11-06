from typing import Dict
import json
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()


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
        self.llm = ChatGoogleGenerativeAI(model=model_name, temperature=temperature)
        
        categories_str = "\n".join([f"- {c}" for c in self.CATEGORIES])

        self.system_message = "당신은 한국어 신고 텍스트를 주어진 카테고리 중 하나로 정확히 분류하는 AI 어시스턴트입니다."
        
        self.prompt_template = f"""다음 신고 문장을 가장 적절한 카테고리로 분류하세요.

가능한 카테고리 목록:
{categories_str}

신고 문장:
{{text}}

반드시 위 목록에 있는 카테고리 중 하나를 선택하고, 다음 JSON 형식으로만 응답하세요:

{{
  "category": "선택한 카테고리",
  "confidence_reason": "이 카테고리를 선택한 이유"
}}"""

    def classify(self, text: str) -> Dict[str, str]:
        """
        신고 텍스트를 카테고리로 분류
        
        Args:
            text: 분류할 신고 텍스트
            
        Returns:
            Dict[str, str]: category와 confidence_reason을 포함하는 딕셔너리
        """
        try:
            from langchain.schema import SystemMessage, HumanMessage
            
            messages = [
                SystemMessage(content=self.system_message),
                HumanMessage(content=self.prompt_template.format(text=text))
            ]
            
            response = self.llm.invoke(messages)
            response_text = response.content.strip()
            
            # JSON 블록 추출 (```json ... ``` 형식 처리)
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(1)
            else:
                # 일반 JSON 객체 추출
                json_match = re.search(r'\{.*?\}', response_text, re.DOTALL)
                if json_match:
                    response_text = json_match.group(0)
            
            # JSON 파싱
            result = json.loads(response_text)
            
            # 카테고리 검증
            category = result.get("category", "기타")
            if category not in self.CATEGORIES:
                # 가장 유사한 카테고리 찾기
                category = self._find_similar_category(category)
            
            return {
                "category": category,
                "confidence_reason": result.get("confidence_reason", "카테고리를 분류했습니다.")
            }
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}, response: {response_text if 'response_text' in locals() else 'N/A'}")
            return {
                "category": "기타",
                "confidence_reason": "응답 형식을 파싱할 수 없습니다."
            }
        except Exception as e:
            print(f"Classification error: {e}")
            return {
                "category": "기타",
                "confidence_reason": f"분류 중 오류가 발생했습니다: {str(e)}"
            }
    
    def _find_similar_category(self, category: str) -> str:
        """
        입력된 카테고리와 가장 유사한 공식 카테고리를 찾습니다.
        """
        category_lower = category.lower()
        for official_cat in self.CATEGORIES:
            if official_cat.lower() in category_lower or category_lower in official_cat.lower():
                return official_cat
        return "기타"


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
