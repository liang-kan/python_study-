import torch
from torch.utils.data import Dataset
from transformers import AutoTokenizer


class CodePairDataset(Dataset):
    def __init__(self, data_list, max_len=128):
        self.data = data_list
        # 加载 CodeBERT 分词器
        self.tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
        self.max_len = max_len

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        code1, code2, label = self.data[index]

        # 对两段代码进行分词和编码
        inputs_a = self.tokenizer(code1, return_tensors='pt', max_length=self.max_len, padding='max_length',
                                  truncation=True)
        inputs_b = self.tokenizer(code2, return_tensors='pt', max_length=self.max_len, padding='max_length',
                                  truncation=True)

        return {
            'ids_a': inputs_a['input_ids'].squeeze(),
            'mask_a': inputs_a['attention_mask'].squeeze(),
            'ids_b': inputs_b['input_ids'].squeeze(),
            'mask_b': inputs_b['attention_mask'].squeeze(),
            'label': torch.tensor(label, dtype=torch.float)
        }


# --- 模拟数据生成函数 ---
def get_dummy_data():
    # 格式: (代码A, 代码B, 标签)
    # 标签 1 表示相似，0 表示不相似
    data = [
        # 相似对 (Type-3/4 克隆：逻辑相同，写法不同)
        ("def add(a, b): return a + b", "def sum_nums(x, y): return x + y", 1),
        ("int x = 10; if(x>5) print('High');", "int val = 10; if(val > 5) System.out.println('High');", 1),

        # 不相似对
        ("def add(a, b): return a + b", "def multiply(a, b): return a * b", 0),
        ("for i in range(10): print(i)", "if x > 0: print(x)", 0)
    ]
    # 复制多份以便训练能跑起来
    return data * 20 