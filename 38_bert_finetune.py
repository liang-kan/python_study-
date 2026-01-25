import os
# 关键：设置 Hugging Face 镜像地址 (必须在 import transformers 之前设置)
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
import torch
from torch.utils.data import DataLoader
from transformers import BertTokenizer, BertForSequenceClassification
from torch.optim import AdamW
from sklearn.model_selection import train_test_split

# 1. 准备数据 (模拟 IMDB 影评)
texts = [
    "I absolutely loved this movie! The acting was great.",  # Pos
    "Terrible film. Waste of time and money.",  # Neg
    "The plot was boring but the visual effects were nice.",  # Neg (Mixed)
    "Best movie of the year! Highly recommended.",  # Pos
    "I fell asleep halfway through. Not good.",  # Neg
    "Masterpiece. A must watch.",  # Pos
]
labels = [1, 0, 0, 1, 0, 1]  # 1=Pos, 0=Neg


def main():
    # 2. 加载预训练模型和分词器
    model_name = 'bert-base-uncased'
    tokenizer = BertTokenizer.from_pretrained(model_name)
    model = BertForSequenceClassification.from_pretrained(model_name, num_labels=2)

    # 3. 数据预处理 (Tokenization)
    # padding=True: 补全到一样长
    # truncation=True: 太长切断
    # return_tensors='pt': 返回 PyTorch Tensor
    inputs = tokenizer(texts, padding=True, truncation=True, return_tensors="pt")
    labels_tensor = torch.tensor(labels)

    # 4. 训练设置
    optimizer = AdamW(model.parameters(), lr=1e-5)  # BERT 需要很小的学习率
    model.train()

    print("Start Fine-tuning BERT...")
    # 简单的训练循环 (只跑 3 轮)
    for epoch in range(3):
        optimizer.zero_grad()

        # 前向传播 (BERT 内部会自动计算 Loss)
        outputs = model(**inputs, labels=labels_tensor)
        loss = outputs.loss

        # 反向传播
        loss.backward()
        optimizer.step()

        print(f"Epoch {epoch + 1}, Loss: {loss.item():.4f}")

    # 5. 预测测试
    print("\n--- Prediction Test ---")
    test_sentence = "This movie is really amazing!"

    # 预处理测试句
    test_input = tokenizer(test_sentence, return_tensors="pt")

    model.eval()
    with torch.no_grad():
        outputs = model(**test_input)

    # 获取概率 (Logits -> Softmax)
    probs = torch.softmax(outputs.logits, dim=1)
    predicted_class = torch.argmax(probs).item()

    label_map = {0: "Negative", 1: "Positive"}
    print(f"Input: '{test_sentence}'")
    print(f"Prediction: {label_map[predicted_class]} (Score: {probs[0][predicted_class]:.4f})")


if __name__ == "__main__":
    main()