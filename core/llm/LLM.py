from typing import Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.schema import SystemMessage, HumanMessage
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
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

    def __init__(self, model_name: str = "gpt-4o-mini", temperature: float = 0.0):
        self.llm = ChatGoogleGenerativeAI(model=model_name, temperature=temperature)
        self.system_prompt = (
            "당신은 한국어 신고 텍스트를 주어진 카테고리 중 하나로 정확히 분류하는 AI 어시스턴트입니다."
        )

        self.response_schema = [
            ResponseSchema(
                name="category",
                description="신고 문장에 가장 적합한 카테고리 이름 (주어진 목록 중 하나)"
            ),
            ResponseSchema(
                name="confidence_reason",
                description="이 카테고리를 선택한 이유에 대한 간단한 설명"
            ),
        ]
        self.parser = StructuredOutputParser.from_response_schemas(self.response_schema)
        self.format_instructions = self.parser.get_format_instructions()

        categories_str = "\n".join([f"- {c}" for c in self.CATEGORIES])

        self.prompt = PromptTemplate.from_template(f"""
다음 신고 문장을 가장 적절한 카테고리로 분류하세요.
가능한 카테고리 목록:
{categories_str}

신고 문장:
{{text}}

출력 형식:
{{format_instructions}}
""")

    def classify(self, text: str) -> Dict[str, str]:
        """
        신고 텍스트를 카테고리로 분류
        """
        human_message = HumanMessage(
            content=self.prompt.format(
                text=text, format_instructions=self.format_instructions
            )
        )
        system_message = SystemMessage(content=self.system_prompt)

        response = self.llm.invoke([system_message, human_message])
        parsed = self.parser.parse(response.content)
        return parsed


if __name__ == "__main__":
    classifier = ReportClassifier(model_name="gemini-2.5-flash")

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

