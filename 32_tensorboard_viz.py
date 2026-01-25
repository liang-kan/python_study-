import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.tensorboard import SummaryWriter  # 导入 TensorBoard 写入器
import numpy as np

# 1. 准备假数据 (模拟 y = 2x + 10)
# 生成 100 个点，加一点点随机噪声
X = np.linspace(0, 10, 100).astype(np.float32).reshape(-1, 1)
y = 2 * X + 10 + np.random.normal(0, 1, (100, 1)).astype(np.float32)

# 转为 Tensor
X_tensor = torch.from_numpy(X)
y_tensor = torch.from_numpy(y)

# 2. 定义简单的线性模型 (1个输入 -> 1个输出)
model = nn.Linear(1, 1)

# 3. 优化器和损失函数
optimizer = optim.SGD(model.parameters(), lr=0.01)
criterion = nn.MSELoss()


def main():
    # --- A. 初始化 TensorBoard ---
    # log_dir="runs/experiment_1": 日志存在 runs 文件夹下
    writer = SummaryWriter(log_dir="runs/experiment_1")

    print("Training started... Check TensorBoard for live updates!")

    # 4. 训练循环
    for epoch in range(500):
        # 前向传播
        prediction = model(X_tensor)
        loss = criterion(prediction, y_tensor)

        # 反向传播
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        # --- B. 记录数据到 TensorBoard ---
        # 记录 Loss 变化
        writer.add_scalar("Loss/train", loss.item(), epoch)

        # 记录权重 Weight 的变化 (看看斜率是不是在接近 2.0)
        current_weight = model.weight.item()
        writer.add_scalar("Parameters/weight", current_weight, epoch)

        # 记录偏置 Bias 的变化 (看看截距是不是在接近 10.0)
        current_bias = model.bias.item()
        writer.add_scalar("Parameters/bias", current_bias, epoch)

        if epoch % 50 == 0:
            print(f"Epoch {epoch}: Loss = {loss.item():.4f}")

    # --- C. 关闭写入器 ---
    writer.close()
    print("Training finished.")
    print("To view results, run this in Terminal:")
    print("tensorboard --logdir=runs")


if __name__ == "__main__":
    main()