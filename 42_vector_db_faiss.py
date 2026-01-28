from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings # 注意这里导入变了
import os

# 配置国内镜像
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

def main():
    print("Initializing FAISS Vector DB...")

    # 1. 初始化 Embedding 模型 (用来把文字变成向量)
    # 依然使用 all-MiniLM-L6-v2
    print("Loading Embedding Model...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # 2. 准备数据
    documents = [
        "The travel allowance for Tier 1 cities (like Beijing, Shanghai) is 300 CNY per day.",
        "The travel allowance for Tier 2 cities is 200 CNY per day.",
        "Employees must submit their expense reports by the 5th of the following month.",
        "The office working hours are from 9:30 AM to 6:30 PM.",
        "Python is the primary programming language for the AI team."
    ]

    # 3. 创建向量库并存入数据 (from_texts)
    # FAISS 会在内存中构建索引
    print(f"Indexing {len(documents)} documents...")
    vector_db = FAISS.from_texts(documents, embeddings)

    # 4. 语义搜索
    question = "How much money do I get for a trip to Shanghai?"
    print(f"\nUser Question: '{question}'")
    print("Searching in Vector DB...")

    # similarity_search_with_score 返回 (Document, Score)
    # Score 越小越相似 (欧氏距离)
    results = vector_db.similarity_search_with_score(question, k=2)

    # 5. 打印结果
    print("\n--- Search Results ---")
    for i, (doc, score) in enumerate(results):
        print(f"Result {i+1}: {doc.page_content}")
        print(f"Distance: {score:.4f}")

    # 6. 保存到磁盘 (可选)
    vector_db.save_local("faiss_index")
    print("Index saved to disk.")

if __name__ == "__main__":
    main()