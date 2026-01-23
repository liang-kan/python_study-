from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from langchain_community.llms.fake import FakeListLLM  # 这是一个用于测试的假 LLM


# 1. 定义输出的数据结构 (类似 Java 的 POJO)
# 我们希望 AI 最终返回这样的 JSON
class TranslationResult(BaseModel):
    original_text: str = Field(description="The original English text")
    translated_text: str = Field(description="The translated Chinese text")
    tone: str = Field(description="The tone of the text (e.g., formal, casual)")


def main():
    # --- 组件 1: Mock LLM (模拟器) ---
    # 我们预先定义好 AI "应该" 返回的内容
    # 当 Chain 跑到这一步时，它不会联网，而是直接从列表里吐出预设的字符串
    # 这里的字符串是模拟 AI 生成的 JSON 文本
    mock_response = '{"original_text": "Hello world", "translated_text": "你好世界", "tone": "casual"}'

    # FakeListLLM 会依次返回 responses 里的内容
    llm = FakeListLLM(responses=[mock_response])

    # --- 组件 2: Parser (解析器) ---
    # 它的作用是告诉 AI "请按这个 JSON 格式输出"，并把 AI 返回的 String 转成 Python Dict
    parser = JsonOutputParser(pydantic_object=TranslationResult)

    # --- 组件 3: Prompt Template (提示词模板) ---
    # partial_variables: 把解析器生成的 "格式说明书" 注入到 prompt 里
    prompt = ChatPromptTemplate.from_template(
        """
        You are a translation assistant.
        Translate the following English text to Chinese.

        Input Text: {input_text}

        {format_instructions}
        """
    ).partial(format_instructions=parser.get_format_instructions())

    # --- 组件 4: LCEL (LangChain Expression Language) ---
    # 这是 LangChain 最核心的语法：用 "|" 管道符把组件串起来
    # 流程：输入 -> 提示词模板 -> 模型(这里是假的) -> 解析器 -> 结果
    chain = prompt | llm | parser

    # --- 运行 Chain ---
    print("Running Chain...")
    user_input = "Hello world"

    # invoke 触发整条流水线
    result = chain.invoke({"input_text": user_input})

    # --- 结果验证 ---
    print("\n--- Final Result (Python Dict) ---")
    print(result)
    print(f"Type: {type(result)}")

    print("\n--- Accessed like an Object ---")
    print(f"Translation: {result['translated_text']}")
    print(f"Tone: {result['tone']}")

    # --- 幕后揭秘：看看 Prompt 长什么样 ---
    # 我们手动渲染一下 prompt 看看 LangChain 到底给 AI 发了什么
    raw_prompt = prompt.format(input_text=user_input)
    print("\n--- Behind the Scenes: The Actual Prompt ---")
    print(raw_prompt)


if __name__ == "__main__":
    main()