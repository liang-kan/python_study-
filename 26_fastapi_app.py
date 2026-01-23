from fastapi import FastAPI
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_community.llms.fake import FakeListLLM
from pydantic import BaseModel as LangChainBaseModel, Field

# 1. 初始化 APP (类似 SpringApplication.run)
app = FastAPI(
    title="My AI Service",
    description="A simple AI translation API powered by LangChain",
    version="1.0"
)


# --- 复用第 24 课的 LangChain 逻辑 ---

# 定义 AI 输出结构 (用于 LangChain Parser)
class TranslationResult(LangChainBaseModel):
    original_text: str = Field(description="Original text")
    translated_text: str = Field(description="Translated text")
    tone: str = Field(description="Tone")


# 定义 API 请求体 (DTO)
class TranslationRequest(BaseModel):
    text: str
    target_lang: str = "Chinese"  # 默认值


# 初始化 Chain (作为全局单例)
def get_translation_chain():
    # 模拟 AI 返回
    mock_response = '{"original_text": "Hello", "translated_text": "你好", "tone": "formal"}'
    llm = FakeListLLM(responses=[mock_response])

    parser = JsonOutputParser(pydantic_object=TranslationResult)

    prompt = ChatPromptTemplate.from_template(
        """
        Translate the following text to {target_lang}.
        Text: {input_text}
        {format_instructions}
        """
    ).partial(format_instructions=parser.get_format_instructions())

    return prompt | llm | parser


# 创建 Chain 实例
translation_chain = get_translation_chain()


# --- 2. 定义接口 (Controller) ---

@app.get("/")
def health_check():
    """健康检查接口"""
    return {"status": "ok", "service": "AI Translator"}


@app.post("/api/translate")
def translate_text(request: TranslationRequest):
    """
    翻译接口
    - request: JSON Body
    """
    print(f"Received request: {request.text} -> {request.target_lang}")

    # 调用 LangChain
    result = translation_chain.invoke({
        "input_text": request.text,
        "target_lang": request.target_lang
    })

    return result


# --- 3. 启动逻辑 ---
# 注意：在生产环境通常用命令行启动，但在开发时这样写方便调试
if __name__ == "__main__":
    import uvicorn

    # host="0.0.0.0" 允许外部访问, port=8000
    uvicorn.run(app, host="0.0.0.0", port=8000)