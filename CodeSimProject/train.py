import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from dataset import CodePairDataset, get_dummy_data
from model import CodeSiameseNetwork

# 1. 设置设备
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# 2. 准备数据
train_data = get_dummy_data()
dataset = CodePairDataset(train_data)
dataloader = DataLoader(dataset, batch_size=4, shuffle=True)

# 3. 初始化模型
model = CodeSiameseNetwork().to(device)
optimizer = torch.optim.AdamW(model.parameters(), lr=2e-5)  # 学习率要小
criterion = nn.MSELoss()  # 损失函数

# 4. 开始训练
model.train()
epochs = 3  # 演示用，跑3轮即可

for epoch in range(epochs):
    total_loss = 0
    for batch in dataloader:
        # 将数据搬到 GPU/CPU
        ids_a = batch['ids_a'].to(device)
        mask_a = batch['mask_a'].to(device)
        ids_b = batch['ids_b'].to(device)
        mask_b = batch['mask_b'].to(device)
        labels = batch['label'].to(device)

        # 梯度清零
        optimizer.zero_grad()

        # 前向传播
        similarity, _, _ = model(ids_a, mask_a, ids_b, mask_b)

        # 计算损失 (模型输出的相似度 vs 真实标签)
        loss = criterion(similarity, labels)

        # 反向传播与优化
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    print(f"Epoch {epoch + 1}/{epochs}, Loss: {total_loss / len(dataloader):.4f}")

# 5. 保存模型
torch.save(model.state_dict(), "code_sim_model.pth")
print("模型已保存！")