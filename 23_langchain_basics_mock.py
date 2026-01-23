from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms.fake import FakeListLLM
from langchain_core.output_parsers import StrOutputParser


def main():
    # 1. 定义提示词模板
    template = ChatPromptTemplate.from_messages([
        ("system", "You are an expert programmer. Please explain the following {language} code to a beginner."),
        ("user", "{code}")
    ])

    # 2. 【关键修改】使用假的 LLM
    # 我们预设 AI 会回复的内容。因为没有真实 AI，所以我们要自己写死这个"假答案"。
    # 这里的目的是测试流程是否通畅。
    fake_llm = FakeListLLM(responses=[
        "This is a Python list comprehension that squares numbers from 0 to 9."
    ])

    # 3. 定义解析器 (把 AI 的对象转成字符串)
    parser = StrOutputParser()

    # 4. 组装链条 (LCEL 语法)
    # 输入 -> 模板 -> (假)模型 -> 解析器 -> 结果
    chain = template | fake_llm | parser

    # 5. 运行
    input_data = {
        "language": "Python",
        "code": "print([x**2 for x in range(10)])"
    }

    print("--- 1. Running Chain ---")
    result = chain.invoke(input_data)
    print(f"Result: {result}")

    # --- 幕后：看看 LangChain 帮你拼出的最终提示词 ---
    print("\n--- 2. Behind the Scenes (Actual Prompt) ---")
    print(template.format(**input_data))


if __name__ == "__main__":
    main()