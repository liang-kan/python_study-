import torch
import torch.nn as nn
from transformers import AutoModel


class CodeSiameseNetwork(nn.Module):
    def __init__(self):
        super(CodeSiameseNetwork, self).__init__()
        # 加载预训练的 CodeBERT 模型
        # 第一次运行会自动下载模型权重 (约500MB)
        self.encoder = AutoModel.from_pretrained("microsoft/codebert-base")

    def forward_one(self, input_ids, attention_mask):
        # 将代码输入 CodeBERT
        outputs = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        # 获取 [CLS] token 的向量作为整段代码的语义表示
        # pooler_output 维度: [batch_size, 768]
        return outputs.pooler_output

    def forward(self, input_ids_a, attention_mask_a, input_ids_b, attention_mask_b):
        # 孪生网络：共享权重，分别计算两段代码的向量
        vector_a = self.forward_one(input_ids_a, attention_mask_a)
        vector_b = self.forward_one(input_ids_b, attention_mask_b)

        # 计算余弦相似度 (-1 到 1 之间)
        cosine_sim = torch.cosine_similarity(vector_a, vector_b)

        return cosine_sim, vector_a, vector_b