from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.llms.fake import FakeListLLM

def main():
    # 1. 模拟一个会聊天的 AI
    # 假设我们问两句，所以预设两个回复
    fake_llm = FakeListLLM(responses=[
        "I am an AI assistant.",  # 回复第一句
        "My name is LangChain."   # 回复第二句
    ])

    # 2. 定义带记忆的 Prompt
    # MessagesPlaceholder(variable_name="history"): 这里会插入历史聊天记录
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful chatbot."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}")
    ])

    # 3. 基础 Chain
    chain = prompt | fake_llm

    # 4. 内存存储 (Session Store)
    # 用一个字典模拟数据库，存储不同 Session 的聊天记录
    store = {}

    def get_session_history(session_id: str):
        if session_id not in store:
            store[session_id] = InMemoryChatMessageHistory()
        return store[session_id]

    # 5. 包装 Chain，使其具备自动读取/写入历史的能力
    # 相当于加了一个 AOP 切面，在调用 LLM 前读取历史，调用后保存历史
    chain_with_history = RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="question",
        history_messages_key="history",
    )

    # --- 第一轮对话 ---
    session_id = "user_123"
    print(f"--- Round 1 (Session: {session_id}) ---")
    response1 = chain_with_history.invoke(
        {"question": "Who are you?"},
        config={"configurable": {"session_id": session_id}}
    )
    print(f"AI: {response1}")

    # --- 第二轮对话 ---
    print(f"\n--- Round 2 (Session: {session_id}) ---")
    response2 = chain_with_history.invoke(
        {"question": "What is your name?"},
        config={"configurable": {"session_id": session_id}} # 同一个 session_id
    )
    print(f"AI: {response2}")

    # --- 验证记忆 ---
    print("\n--- Checking Memory Store ---")
    history = store[session_id].messages
    for msg in history:
        # type: human 或 ai
        # content: 内容
        print(f"[{type(msg).__name__}]: {msg.content}")

if __name__ == "__main__":
    main()