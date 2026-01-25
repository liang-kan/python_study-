import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt

# --- 1.数据准备（Data Preparation） ---
def create_sine_wave_data(seq_length,num_samples=1000):
    #生成 0 - 100 之间的1000个点
    x = np.linspace(0, 100,num_samples)
    y = np.sin(x)
    return y


def create_sequences(data, seq_length):
    """
    滑动窗口切分数据
    输入: [1, 2, 3, 4, 5], seq_length=3
    输出 X: [[1, 2, 3], [2, 3, 4]]
    输出 y: [4, 5]
    """
    xs = []
    ys = []
    for i in range(len(data) - seq_length):
        x = data[i:i + seq_length]
        y = data[i + seq_length]
        xs.append(x)
        ys.append(y)
    return np.array(xs), np.array(ys)


# --- 2. 定义 LSTM 模型 ---
class LSTMModel(nn.Module):
    def __init__(self, input_size=1, hidden_layer_size=50, output_size=1):
        super().__init__()
        self.hidden_layer_size = hidden_layer_size

        # LSTM 层
        # batch_first=True: 输入格式为 (batch, seq, feature)
        self.lstm = nn.LSTM(input_size, hidden_layer_size, batch_first=True)

        # 全连接层: 把 LSTM 的记忆状态转为最终预测值
        self.linear = nn.Linear(hidden_layer_size, output_size)

    def forward(self, input_seq):
        # input_seq 形状: (batch_size, seq_length, 1)

        # LSTM 输出: lstm_out, (hidden_state, cell_state)
        # 我们只关心 lstm_out
        lstm_out, _ = self.lstm(input_seq)

        # 我们只需要序列中最后一个时间步的输出
        # lstm_out[:, -1, :] 取所有 batch 的最后一个时间点
        last_time_step = lstm_out[:, -1, :]

        predictions = self.linear(last_time_step)
        return predictions


def main():
    # 参数设置
    seq_length = 20  # 它是基于过去 20 个点来预测下 1 个点
    epochs = 50
    lr = 0.01

    # 1. 生成数据
    data = create_sine_wave_data(seq_length)
    X, y = create_sequences(data, seq_length)

    # 转为 Tensor
    # LSTM 要求输入形状: (Batch, Sequence Length, Features)
    # 这里的 Features 是 1 (因为只有一个值：正弦值)
    X_tensor = torch.from_numpy(X).float().unsqueeze(-1)  # 增加一个维度变为 (N, 20, 1)
    y_tensor = torch.from_numpy(y).float().unsqueeze(-1)  # (N, 1)

    # 2. 初始化模型
    model = LSTMModel()
    loss_function = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    print("Training LSTM...")
    # 3. 训练循环
    for i in range(epochs):
        optimizer.zero_grad()
        y_pred = model(X_tensor)
        loss = loss_function(y_pred, y_tensor)
        loss.backward()
        optimizer.step()

        if i % 5 == 0:
            print(f"Epoch {i} Loss: {loss.item():.6f}")

    # 4. 预测与绘图
    print("Predicting...")
    model.eval()
    with torch.no_grad():
        test_pred = model(X_tensor).numpy()

    # 画图对比
    plt.figure(figsize=(12, 6))
    # 画真实值 (要把前面的 seq_length 偏移补上，方便对齐)
    plt.plot(np.arange(seq_length, len(data)), y, label='True Data', alpha=0.6)
    plt.plot(np.arange(seq_length, len(data)), test_pred, label='LSTM Prediction', linestyle='--')
    plt.legend()
    plt.title("LSTM Sine Wave Prediction")
    plt.show()


if __name__ == "__main__":
    main()