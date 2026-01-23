import torch
import numpy as np


def main():
    # 1. 创建 Tensor (张量)
    # 类似于 NumPy，但它是 PyTorch 的核心数据结构
    x_data = [1.0, 2.0, 3.0]
    tensor_x = torch.tensor(x_data)
    print(f"Tensor: {tensor_x}")

    # 2. Tensor 和 NumPy 互转 (零拷贝，非常快)
    np_arr = np.array([4, 5, 6])
    tensor_from_np = torch.from_numpy(np_arr)
    print(f"From NumPy: {tensor_from_np}")

    # 3. 自动求导 (Autograd) —— PyTorch 的魔法
    # 假设我们有一个公式: y = w * x + b
    # 我们想求 y 对 w 的导数 (dy/dw)

    # requires_grad=True 告诉 PyTorch: "请盯着这个变量，我要对它求导"
    w = torch.tensor(2.0, requires_grad=True)
    x = torch.tensor(3.0)
    b = torch.tensor(1.0)

    # 前向计算 (Forward)
    y = w * x + b  # y = 2 * 3 + 1 = 7
    print(f"\nResult y: {y.item()}")  # .item() 取出具体的数值

    # 反向传播 (Backward)
    # 这一行代码会自动计算 y 关于所有变量(w)的梯度
    y.backward()

    # 查看梯度
    # 数学推导: y = w*x + b, 所以 dy/dw = x = 3
    print(f"Gradient (dy/dw): {w.grad}")

    # 此时，PyTorch 已经帮你算出了导数是 3.0。
    # 在神经网络训练中，这相当于告诉我们：为了让 y 变小，w 应该往反方向调整多少。


if __name__ == "__main__":
    main()