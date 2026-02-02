import os
from zhipuai import ZhipuAI

# --- 配置区域 ---
# 请把你的智谱 API Key 填在这里
API_KEY = "8354280bc4d84b13aea514cd0b55c8a2.97vqKhN5Nlw1MvBV"

client = ZhipuAI(api_key=API_KEY)


def stream_print_and_collect(response):
    """
    专门用来处理流式输出的辅助函数
    """
    full_content = ""
    print("\n" + "-" * 30)

    for chunk in response:
        # 获取增量内容
        delta = chunk.choices[0].delta.content

        # !!! 关键修复 !!!
        # 如果 delta 是 None (通常是最后一次响应)，则跳过，防止报错
        if delta is not None:
            print(delta, end="", flush=True)
            full_content += delta

    print("\n" + "-" * 30)
    return full_content


def main():
    print("=" * 40)
    print("🧠 智谱 AI 写作助手 (V2.1 修复版)")
    print("=" * 40)

    topic = input("👉 主题: ")
    style = input("👉 风格: ")

    # 初始化历史消息列表
    # System Prompt 放在最前面，定下基调
    messages = [
        {"role": "system", "content": "你是一个资深的专栏作家，擅长根据用户要求撰写高质量、有逻辑、有深度的文章。"}
    ]

    # 构建第一条用户指令
    first_prompt = f"请以【{style}】的风格，写一篇关于【{topic}】的文章。要求：结构清晰，观点独特。"
    messages.append({"role": "user", "content": first_prompt})

    # --- 第一次生成 ---
    print("\n🤖 AI 正在思考...", end="", flush=True)
    try:
        response = client.chat.completions.create(
            model="glm-4",
            messages=messages,
            stream=True
        )
        content = stream_print_and_collect(response)

        # 将 AI 的回答加入历史，以便后续修改时它知道上下文
        messages.append({"role": "assistant", "content": content})

    except Exception as e:
        print(f"\n❌ 请求失败: {e}")
        return

    # --- 循环调试模式 ---
    while True:
        print("\n🤔 满意吗？")
        print("1. 满意，保存 (s)")
        print("2. 提修改意见 (r)")
        print("3. 退出 (q)")

        choice = input("👉 选择: ").lower()

        if choice in ['1', 's']:
            # 保存文件
            if not os.path.exists("ai_articles"):
                os.mkdir("ai_articles")
            filename = f"ai_articles/{topic[:10]}.md"  # 截取前10个字做文件名
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✅ 已保存: {filename}")
            break

        elif choice in ['2', 'r']:
            # 获取修改意见
            revision = input("🔧 哪里需要改: ")

            # 将用户的修改意见加入历史上下文
            messages.append({"role": "user", "content": revision})

            print(f"📡 正在重写...")
            try:
                response = client.chat.completions.create(
                    model="glm-4",
                    messages=messages,
                    stream=True
                )
                # 重新获取内容
                content = stream_print_and_collect(response)

                # 更新历史，把最新的回答记下来
                messages.append({"role": "assistant", "content": content})

            except Exception as e:
                print(f"❌ 修改失败: {e}")

        else:
            print("👋 Bye!")
            break


if __name__ == "__main__":
    main()