from transformers import pipeline


def main():
    print("Downloading model pipeline (this might take a while for the first time)...")

    # 1. 创建一个情感分析的流水线 (Pipeline)
    # 第一次运行会自动从 Hugging Face 官网下载默认的预训练模型 (distilbert)
    # 任务类型: sentiment-analysis (情感分析)
    classifier = pipeline("sentiment-analysis")

    # 2. 准备测试数据
    comments = [
        "Python is amazing and I love machine learning!",  # 积极
        "The code is messy and hard to understand.",  # 消极
        "I had toast for breakfast."  # 中性/或偏消极(取决于模型)
    ]

    print("\n--- Analyzing Sentiments ---")

    # 3. 批量预测
    results = classifier(comments)

    # 4. 输出结果
    for text, result in zip(comments, results):
        # result 格式: {'label': 'POSITIVE', 'score': 0.99...}
        print(f"Text: '{text}'")
        print(f"Result: {result['label']} (Confidence: {result['score']:.4f})\n")


if __name__ == "__main__":
    main()