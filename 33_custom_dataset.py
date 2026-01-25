import torch
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import numpy as np
import os


# --- 1. 准备一个模拟的 CSV 文件 ---
# 实际项目中，这一步你是直接从磁盘读取现成的文件
def create_dummy_csv(filename="my_sales_data.csv"):
    if not os.path.exists(filename):
        print(f"Creating dummy data: {filename}...")
        # 模拟数据：3个特征 (广告费, 促销力度, 季节)，1个标签 (销售额)
        data = {
            'feature_1': np.random.rand(100),
            'feature_2': np.random.rand(100),
            'feature_3': np.random.randint(0, 2, 100),  # 0或1
            'label': np.random.rand(100) * 1000
        }
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
    else:
        print(f"File {filename} already exists.")


# --- 2. 定义自定义 Dataset 类 (重点) ---
class SalesDataset(Dataset):
    def __init__(self, csv_file):
        """
        初始化：读取 CSV 到内存
        """
        self.data_frame = pd.read_csv(csv_file)

        # 提取特征 (前3列) 和 标签 (最后一列)
        # values 把 DataFrame 变成 numpy 数组
        # float32 是 PyTorch 最喜欢的格式
        self.x = self.data_frame.iloc[:, 0:3].values.astype(np.float32)
        self.y = self.data_frame.iloc[:, 3].values.astype(np.float32)

    def __len__(self):
        """返回数据总长度"""
        return len(self.data_frame)

    def __getitem__(self, idx):
        """
        根据索引 idx 返回一条样本
        PyTorch 会不停调用这个方法来获取数据进行训练
        """
        # 必须转成 Tensor
        sample_x = torch.from_numpy(self.x[idx])
        sample_y = torch.from_numpy(np.array([self.y[idx]]))  # 变成 [1] 形状

        return sample_x, sample_y


def main():
    csv_file = "my_sales_data.csv"
    create_dummy_csv(csv_file)

    # 1. 实例化 Dataset
    my_dataset = SalesDataset(csv_file)
    print(f"Dataset size: {len(my_dataset)}")

    # 测试一下获取第 0 条数据
    x0, y0 = my_dataset[0]
    print(f"Sample 0: X={x0}, y={y0}")

    # 2. 使用 DataLoader (数据加载器)
    # DataLoader 是 PyTorch 的调度员。它负责：
    # - batch_size=4: 每次把 4 条数据打包成一组
    # - shuffle=True: 每轮训练前把数据打乱 (洗牌)
    # - num_workers=0: Windows下通常设为0 (单进程)，Linux可以设多一点加速
    train_loader = DataLoader(dataset=my_dataset, batch_size=4, shuffle=True)

    print("\n--- Iterating with DataLoader ---")
    # 模拟一轮训练 (Epoch)
    for batch_idx, (inputs, targets) in enumerate(train_loader):
        # inputs 的形状应该是 (4, 3) -> 4条数据，每条3个特征
        # targets 的形状应该是 (4, 1)
        print(f"Batch {batch_idx}: Input shape {inputs.shape}, Target shape {targets.shape}")

        # 在这里，你通常会把 inputs 喂给模型: model(inputs)
        # ...

        if batch_idx >= 2:  # 只打印前 3 个 batch 看看演示
            break


if __name__ == "__main__":
    main()