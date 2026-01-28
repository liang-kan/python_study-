from langchain_community.llms.fake import FakeListLLM
from langchain_experimental.tools import PythonREPLTool
# 核心：使用 initialize_agent，这是跨版本兼容性最好的入口
from langchain.agents import initialize_agent, AgentType

## 运行失败

def main():
    # 1. 初始化工具
    python_tool = PythonREPLTool()
    tools = [python_tool]

    # 2. 模拟 AI 响应
    fake_responses = [
        "Action: Python_REPL\nAction Input: print(10 + 10)",
        "Final Answer: The result is 20."
    ]
    llm = FakeListLLM(responses=fake_responses)

    # 3. 创建 Agent
    print("--- Running AI Agent ---")

    # handle_parsing_errors=True 非常重要，防止模拟器输出格式微小差异导致报错
    agent_executor = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True
    )

    # 4. 运行
    try:
        result = agent_executor.invoke({"input": "Calculate 10 + 10 using Python code."})
        print(f"\nFinal Result: {result['output']}")
    except Exception as e:
        print(f"\nError: {e}")

    # --- 手动测试部分 ---
    print("\n--- Manual Tool Test ---")
    try:
        tool_output = python_tool.run("print('Hello from Python Tool')")
        print(f"Tool Output: {tool_output}")
    except Exception as e:
        print(f"Tool Error: {e}")


if __name__ == "__main__":
    main()