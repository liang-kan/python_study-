import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader


# 1. 定义神经网络结构 (Class)
class SimpleCNN(nn.Module):
    def __init__(self):
        super(SimpleCNN, self).__init__()
        # 第一层卷积：输入1通道(灰度图)，输出10通道(特征图)，卷积核大小5x5
        self.conv1 = nn.Conv2d(in_channels=1, out_channels=10, kernel_size=5)
        # 第二层卷积
        self.conv2 = nn.Conv2d(10, 20, kernel_size=5)
        # 池化层 (Pooling): 把图片缩小一半 (2x2)
        self.pooling = nn.MaxPool2d(2)
        # 全连接层 (Linear): 类似于之前的 MLP，做最终分类
        # 320 是根据卷积后的尺寸算出来的 (如果你感兴趣原理可以深究，现在先照抄)
        self.fc = nn.Linear(320, 10)  # 输出 10 个数字 (0-9)

    def forward(self, x):
        # x 是输入图片
        batch_size = x.size(0)

        # 第一层卷积 -> 激活函数(ReLU) -> 池化
        x = torch.relu(self.pooling(self.conv1(x)))

        # 第二层卷积 -> 激活函数(ReLU) -> 池化
        x = torch.relu(self.pooling(self.conv2(x)))

        # 展平 (Flatten): 把多维矩阵变成一维向量，为了塞给全连接层
        x = x.view(batch_size, -1)

        # 最后一层全连接
        x = self.fc(x)
        return x


def main():
    # 配置
    batch_size = 64
    learning_rate = 0.01
    epochs = 3  # 训练几轮

    # 2. 准备数据 (自动下载 MNIST)
    # transforms.ToTensor() 把图片变成 PyTorch 的 Tensor 格式
    transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))])

    train_dataset = datasets.MNIST(root='./data', train=True, download=True, transform=transform)
    # DataLoader 类似于 Java 的 Iterator，帮我们自动把数据分批 (Batch)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    # 3. 初始化模型
    model = SimpleCNN()

    # 定义损失函数 (CrossEntropyLoss 用于多分类)
    criterion = nn.CrossEntropyLoss()
    # 定义优化器 (SGD 随机梯度下降)
    optimizer = optim.SGD(model.parameters(), lr=learning_rate, momentum=0.5)

    # 4. 开始训练循环
    print("Start Training (CNN)...")
    model.train()  # 切换到训练模式

    for epoch in range(epochs):
        for batch_idx, (data, target) in enumerate(train_loader):
            # A. 梯度清零 (防止之前的梯度累加)
            optimizer.zero_grad()

            # B. 前向传播 (计算预测值)
            output = model(data)

            # C. 计算损失 (预测值和真实值的差距)
            loss = criterion(output, target)

            # D. 反向传播 (自动求导)
            loss.backward()

            # E. 更新参数 (W = W - lr * grad)
            optimizer.step()

            if batch_idx % 300 == 0:
                print(f"Epoch {epoch + 1}/{epochs} | Batch {batch_idx} | Loss: {loss.item():.4f}")

    print("Training Finished!")

    # 5. 保存模型 (类似序列化)
    torch.save(model.state_dict(), "mnist_cnn.pth")
    print("Model saved to mnist_cnn.pth")


if __name__ == "__main__":
    main()