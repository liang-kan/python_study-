import torch
from torchvision import models, transforms
from PIL import Image
import requests
import json


def main():
    print("Loading pre-trained ResNet model...")
    # 1. 下载预训练好的 ResNet18 模型
    # weights='DEFAULT' 表示使用最新的预训练权重
    model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    model.eval()  # 切换到评估模式 (不训练)

    # 2. 定义图片预处理 (必须和模型训练时保持一致)
    preprocess = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    # 3. 下载一张测试图片 (比如一只金毛犬)
    img_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c0/Golden_Retriever_with_tennis_ball.jpg/1200px-Golden_Retriever_with_tennis_ball.jpg"
    print(f"Downloading image...")
    # 加上 header 伪装，防止 403
    headers = {"User-Agent": "Mozilla/5.0"}
    img_data = requests.get(img_url, headers=headers, stream=True).raw
    img = Image.open(img_data)

    # 4. 预处理图片并增加一个维度 (Batch Size)
    # 变成 (1, 3, 224, 224)
    img_t = preprocess(img)
    batch_t = torch.unsqueeze(img_t, 0)

    # 5. 预测
    print("Predicting...")
    with torch.no_grad():  # 告诉 PyTorch 不需要算梯度，节省内存
        out = model(batch_t)

    # 6. 解析结果
    # 下载 ImageNet 的 1000 个类别标签
    labels_url = "https://raw.githubusercontent.com/anishathalye/imagenet-simple-labels/master/imagenet-simple-labels.json"
    labels = requests.get(labels_url).json()

    # 找到概率最大的那个
    # out 是一个 1x1000 的向量，softmax 把它变成概率百分比
    percentages = torch.nn.functional.softmax(out, dim=1)[0] * 100
    _, indices = torch.sort(out, descending=True)

    # 打印前 5 个预测结果
    print("\n--- Top 5 Predictions ---")
    for idx in indices[0][:5]:
        print(f"{labels[idx]}: {percentages[idx].item():.2f}%")


if __name__ == "__main__":
    main()