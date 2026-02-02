import os
import PyPDF2
from docx import Document
from zhipuai import ZhipuAI

# --- 配置 ---
API_KEY = "8354280bc4d84b13aea514cd0b55c8a2.97vqKhN5Nlw1MvBV"
client = ZhipuAI(api_key=API_KEY)


# 1. 定义读取文件的函数
def read_file(file_path):
    """
    自动判断文件类型并读取文字
    """
    ext = os.path.splitext(file_path)[1].lower()
    content = ""

    try:
        if ext == '.pdf':
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                # 遍历每一页
                for page in reader.pages:
                    content += page.extract_text() + "\n"

        elif ext == '.docx':
            doc = Document(file_path)
            for para in doc.paragraphs:
                content += para.text + "\n"

        elif ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

        else:
            return None, "不支持的文件格式"

        return content, "success"

    except Exception as e:
        return None, str(e)


# 2. 让 AI 分析需求
def analyze_requirements(text):
    print("\n🧠 AI 正在阅读招标文件并提取关键点...", end="", flush=True)

    # 构建 Prompt
    # 标书文件通常很长，Token 可能会超。
    # 这里为了演示，我们假设文件不太大。如果文件超大，需要切片（进阶课会讲）。
    prompt = f"""
    下面是一份招标文件的内容。请你扮演一名资深的投标专员，帮我提取以下关键信息：
    1. 项目名称
    2. 采购预算 (如有)
    3. 核心技术指标/需求
    4. 交付/工期要求
    5. 废标条款/红线要求 (非常重要)

    ---招标文件内容开始---
    {text[:5000]}  
    ---招标文件内容结束---
    (注意：为了防止超长，我只截取了前5000字)
    """

    try:
        response = client.chat.completions.create(
            model="glm-4",  # 或者 glm-4-long (专门处理长文本)
            messages=[
                {"role": "system", "content": "你是一个专业的标书分析师。"},
                {"role": "user", "content": prompt}
            ],
            stream=True
        )

        full_result = ""
        print("\n" + "-" * 30)
        for chunk in response:
            delta = chunk.choices[0].delta.content
            if delta:
                print(delta, end="", flush=True)
                full_result += delta
        print("\n" + "-" * 30)
        return full_result

    except Exception as e:
        print(f"❌ 分析失败: {e}")
        return None


# --- 主程序 ---
def main():
    print("📂 标书 AI 助手 - 第一步: 需求分析")
    file_path = input("👉 请输入招标文件路径 (如 zhaobiao.docx): ")

    if not os.path.exists(file_path):
        print("❌ 文件不存在！")
        return

    # 1. 读取文字
    print(f"📄 正在读取 {file_path} ...")
    content, msg = read_file(file_path)

    if not content:
        print(f"❌ 读取失败: {msg}")
        return

    print(f"✅ 读取成功！共 {len(content)} 字符。")

    # 2. 调用 AI 分析
    analysis = analyze_requirements(content)

    # 3. 保存分析结果 (后续生成标书要用)
    if analysis:
        with open("bid_analysis.txt", "w", encoding="utf-8") as f:
            f.write(analysis)
        print("\n✅ 需求分析已保存到 bid_analysis.txt")


if __name__ == "__main__":
    main()