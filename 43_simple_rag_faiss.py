from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms.fake import FakeListLLM
from langchain_core.output_parsers import StrOutputParser
import os

os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'


def setup_knowledge_base():
    """初始化 FAISS 知识库"""
    print("Loading Embeddings...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    docs = [
        "Project Alpha deadline is moved to Dec 31st.",
        "Project Beta is currently paused due to budget cuts.",
        "The CEO's email is ceo@company.com."
    ]

    print("Creating Index...")
    vector_db = FAISS.from_texts(docs, embeddings)
    return vector_db


def main():
    # 1. 准备知识库
    vector_db = setup_knowledge_base()

    # 2. 用户提问
    user_query = "What is the status of Project Beta?"
    print(f"\nUser Query: {user_query}")

    # 3. 检索 (Retrieval)
    # as_retriever() 把向量库变成一个检索器接口
    retriever = vector_db.as_retriever(search_kwargs={"k": 1})

    # 这一步 LangChain 自动去搜
    retrieved_docs = retriever.invoke(user_query)
    context_text = retrieved_docs[0].page_content
    print(f"-> Found Context: '{context_text}'")

    # 4. 组装 Prompt
    prompt_template = ChatPromptTemplate.from_template(
        """
        You are a helpful assistant. Answer the question based ONLY on the context provided.

        Context: {context}

        Question: {question}
        """
    )

    # 5. 模拟 AI
    expected_answer = "Based on the context, Project Beta is currently paused because of budget cuts."
    llm = FakeListLLM(responses=[expected_answer])

    # 6. Chain
    chain = prompt_template | llm | StrOutputParser()

    # 7. 运行
    print("\nGenerating Answer...")
    final_answer = chain.invoke({
        "context": context_text,
        "question": user_query
    })

    print(f"AI Answer: {final_answer}")


if __name__ == "__main__":
    main()