from openai import OpenAI
import os

# --- 配置 ---
# 如果你有 OpenAI Key，填这里。如果没有，推荐去智谱AI申请一个免费的。
# 这里我演示标准代码结构。
# 也可以使用 'https://api.moonshot.cn/v1' (Kimi) 等国内中转服务
API_KEY = "你的_API_KEY_在这里"
BASE_URL = "https://api.openai.com/v1"  # 或者国内大模型的 Base URL


# 如果你完全没有 Key，我们可以用一个临时的开源方案（比如 Ollama 本地跑），
# 但为了演示代码逻辑，假设你有一个 Key。
# ⚠️ 注意：如果没有真实 Key，运行会报错。建议去申请一个智谱AI或Kimi的Key。

def main():
    print("Initializing LLM Client...")

    # 1. 初始化客户端
    # 就像 JDBC 的 Connection
    client = OpenAI(
        api_key=API_KEY,
        base_url=BASE_URL
    )

    try:
        # 2. 发送对话请求
        # Messages 是一个列表，模拟对话历史
        # system: 给 AI 设定人设
        # user: 你的问题
        print("Sending request to AI...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # 如果用智谱，这里填 "glm-4"
            messages=[
                {"role": "system", "content": "You are a senior Java Architect."},
                {"role": "user", "content": "Please write a Java Singleton pattern using Enum. Explain why it is good."}
            ],
            temperature=0.7  # 0.0-1.0，越高越有创造力，越低越严谨
        )

        # 3. 解析回答
        ai_reply = response.choices[0].message.content
        print("\n--- AI Response ---")
        print(ai_reply)

    except Exception as e:
        print(f"\nError: {e}")
        print("Tip: If you don't have an API Key, this script will fail.")
        print("Please register at https://open.bigmodel.cn/ (Zhipu AI) to get a free key.")


if __name__ == "__main__":
    main()