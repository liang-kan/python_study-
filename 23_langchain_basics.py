from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


# 如果你安装了 langchain_openai，可以 import ChatOpenAI
# from langchain_openai import ChatOpenAI

def main():
    # 1. 定义提示词模板 (Prompt Template)
    # 这就是 LangChain 的核心：把对 AI 的指令参数化
    # {language} 和 {code} 是占位符，类似 Java String.format 的 %s
    template = ChatPromptTemplate.from_messages([
        ("system", "You are an expert programmer. Please explain the following {language} code to a beginner."),
        ("user", "{code}")
    ])

    # 2. 模拟一段输入数据
    input_data = {
        "language": "Python",
        "code": "print([x**2 for x in range(10)])"
    }

    # 3. 渲染模板
    # 这一步 LangChain 会把变量填进去，生成最终发给 AI 的字符串
    final_prompt = template.invoke(input_data)

    print("--- 1. Constructed Prompt Messages ---")
    for msg in final_prompt.messages:
        print(f"[{msg.type.upper()}]: {msg.content}")

    # --- 关键概念：Chain (链) ---
    # 在真实的 LangChain 应用中，我们会把 Model 接在 Prompt 后面
    # chain = template | model | output_parser

    # 因为没有配置真实的 Model Key，我们这里只演示 Chain 的前半部分
    # 这就像你配置好了 MyBatis 的 Mapper，但还没连数据库，你依然可以看到生成的 SQL。


if __name__ == "__main__":
    main()