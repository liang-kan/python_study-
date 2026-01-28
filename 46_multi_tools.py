from langchain_core.tools import tool


# 1. 定义自定义工具 (使用 @tool 装饰器)
# 只要加上这个注解，LangChain 就能自动解析函数的参数和注释，告诉 AI 怎么用

@tool
def get_weather(city: str) -> str:
    """Queries the current weather for a specific city."""
    # 这里模拟一个 API 调用
    if "Shanghai" in city:
        return "Sunny, 25°C"
    elif "Beijing" in city:
        return "Cloudy, 20°C"
    else:
        return "Unknown weather"


@tool
def send_email(recipient: str, content: str) -> str:
    """Sends an email to a recipient."""
    return f"Email sent to {recipient} with content: '{content}'"


# 2. 工具列表
tools = [get_weather, send_email]

# 3. 打印工具信息 (看看 AI 到底看到了什么)
print("--- Tool Schemas (What AI sees) ---")
for t in tools:
    print(f"Name: {t.name}")
    print(f"Description: {t.description}")
    print(f"Args: {t.args}")
    print("-" * 20)


# 4. 模拟 AI 的决策逻辑 (Router)
def simple_agent_router(user_query):
    print(f"\nUser Query: '{user_query}'")

    # 这里我们用简单的 if-else 模拟 LLM 的大脑决策过程
    # 真实场景下，是 LLM 自己判断 "我应该调用哪个函数"
    if "weather" in user_query.lower():
        # AI 决定调用 get_weather
        print(">> AI Decision: Use tool 'get_weather'")
        city = "Shanghai" if "Shanghai" in user_query else "Beijing"
        result = get_weather.invoke({"city": city})
        print(f">> Tool Output: {result}")
        return f"The weather is {result}."

    elif "email" in user_query.lower():
        # AI 决定调用 send_email
        print(">> AI Decision: Use tool 'send_email'")
        result = send_email.invoke({"recipient": "boss@company.com", "content": "Weather report"})
        print(f">> Tool Output: {result}")
        return "Email sent successfully."


# 5. 测试
simple_agent_router("What is the weather in Shanghai?")
simple_agent_router("Send an email about the weather.")