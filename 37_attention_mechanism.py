import torch
import torch.nn as nn
import math


class SelfAttention(nn.Module):
    def __init__(self, embed_size, heads):
        super(SelfAttention, self).__init__()
        self.embed_size = embed_size  # 词向量维度 (比如 256)
        self.heads = heads  # 多头注意力的头数 (比如 8)
        self.head_dim = embed_size // heads

        assert (
                self.head_dim * heads == embed_size
        ), "Embedding size needs to be divisible by heads"

        # 定义 Q, K, V 的线性变换矩阵
        # 这一步相当于把输入词向量映射到 Q, K, V 空间
        self.values = nn.Linear(self.head_dim, self.head_dim, bias=False)
        self.keys = nn.Linear(self.head_dim, self.head_dim, bias=False)
        self.queries = nn.Linear(self.head_dim, self.head_dim, bias=False)

        # 最后的输出层
        self.fc_out = nn.Linear(heads * self.head_dim, embed_size)

    def forward(self, values, keys, query, mask):
        # N: Batch size
        # value_len, key_len, query_len: 句子长度
        N = query.shape[0]
        value_len, key_len, query_len = values.shape[1], keys.shape[1], query.shape[1]

        # 1. 拆分成多头 (Split embedding into self.heads pieces)
        # 这里的 reshape 操作是为了让每个头独立计算
        values = values.reshape(N, value_len, self.heads, self.head_dim)
        keys = keys.reshape(N, key_len, self.heads, self.head_dim)
        query = query.reshape(N, query_len, self.heads, self.head_dim)

        # 2. 线性变换 (Q, K, V)
        values = self.values(values)
        keys = self.keys(keys)
        queries = self.queries(query)

        # 3. 计算注意力分数 (Energy)
        # 公式: Q * K^T
        # torch.einsum 是爱因斯坦求和约定，非常强大的矩阵乘法工具
        # "nqhd,nkhd->nhqk":
        # n=Batch, h=Heads, q=Query Len, k=Key Len, d=Head Dim
        # 结果形状: (Batch, Heads, Query Len, Key Len)
        energy = torch.einsum("nqhd,nkhd->nhqk", [queries, keys])

        # 4. Mask (可选)
        # 如果是生成式模型 (如 GPT)，我们要遮住未来的词，不让它看见
        if mask is not None:
            energy = energy.masked_fill(mask == 0, float("-1e20"))

        # 5. Softmax 归一化
        # 把分数变成概率 (0~1 之间，和为 1)
        # attention shape: (N, Heads, Query Len, Key Len)
        attention = torch.softmax(energy / (self.embed_size ** (1 / 2)), dim=3)

        # 6. 加权求和
        # 公式: Attention * V
        # "nhqk,nvhd->nqhd": 把概率乘回到 Values 上
        out = torch.einsum("nhqk,nvhd->nqhd", [attention, values])

        # 7. 拼接多头并输出
        out = out.reshape(N, query_len, self.heads * self.head_dim)
        out = self.fc_out(out)

        return out


def main():
    # 模拟输入数据
    # Batch Size=1, 句子长度=5, 词向量维度=256
    x = torch.tensor([[1, 2, 3, 4, 5, 6, 7, 8]]).float()  # 只是演示，这里我们需要 embeddings

    embed_size = 256
    heads = 8

    # 随机生成一个输入 Embedding (Batch=1, Seq=10, Dim=256)
    input_data = torch.randn(1, 10, embed_size)

    # 初始化我们写的 Attention 层
    attention = SelfAttention(embed_size, heads)

    # 前向传播 (Q, K, V 都是输入本身 -> 所以叫 Self-Attention)
    out = attention(input_data, input_data, input_data, mask=None)

    print(f"Input shape: {input_data.shape}")  # [1, 10, 256]
    print(f"Output shape: {out.shape}")  # [1, 10, 256]
    print("\nSuccess! The output shape matches the input shape.")
    print("This block allows information to flow between all words regardless of distance.")


if __name__ == "__main__":
    main()