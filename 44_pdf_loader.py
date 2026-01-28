from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import requests
import os


def download_sample_pdf(filename):
    """下载一个关于比特币的白皮书 PDF 作为测试"""
    if not os.path.exists(filename):
        print("Downloading sample PDF...")
        url = "https://bitcoin.org/bitcoin.pdf"
        resp = requests.get(url)
        with open(filename, 'wb') as f:
            f.write(resp.content)


def main():
    pdf_file = "bitcoin.pdf"
    download_sample_pdf(pdf_file)

    # 1. 加载 PDF
    print(f"Loading {pdf_file}...")
    loader = PyPDFLoader(pdf_file)
    # load() 会把每一页作为一个 Document 对象
    pages = loader.load()
    print(f"Total pages: {len(pages)}")

    # 2. 文本切分 (Chunking) -- RAG 中最关键的一步
    # 为什么要切分？
    # 1. 向量数据库的输入长度有限制。
    # 2. 大模型的 Context Window 有限制。
    # 3. 搜索时，我们需要找到"最相关的一小段"，而不是把整本书丢给 AI。

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,  # 每块约 500 字符
        chunk_overlap=50  # 块之间重叠 50 字符 (保持上下文连贯)
    )

    chunks = text_splitter.split_documents(pages)

    print(f"Split into {len(chunks)} chunks.")

    # 3. 打印前两个切片看看
    print("\n--- Chunk 1 ---")
    print(chunks[0].page_content)
    print("\n--- Chunk 2 ---")
    print(chunks[1].page_content)

    # 在真实 RAG 中，下一步就是把这些 chunks 存入 faiss (第 42 课的内容)


if __name__ == "__main__":
    main()