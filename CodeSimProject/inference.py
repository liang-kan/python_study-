import torch
from transformers import AutoTokenizer
from model import CodeSiameseNetwork


def predict_similarity(code1, code2):
    # 1. 准备模型和环境
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")

    model = CodeSiameseNetwork()
    # 加载刚才训练好的权重
    try:
        model.load_state_dict(torch.load("code_sim_model.pth", map_location=device))
    except:
        print("未找到训练好的模型，将使用初始权重进行演示...")

    model.to(device)
    model.eval()

    # 2. 数据处理
    inputs_a = tokenizer(code1, return_tensors='pt', max_length=128, padding='max_length', truncation=True)
    inputs_b = tokenizer(code2, return_tensors='pt', max_length=128, padding='max_length', truncation=True)

    ids_a = inputs_a['input_ids'].to(device)
    mask_a = inputs_a['attention_mask'].to(device)
    ids_b = inputs_b['input_ids'].to(device)
    mask_b = inputs_b['attention_mask'].to(device)

    # 3. 预测
    with torch.no_grad():
        similarity, vec_a, vec_b = model(ids_a, mask_a, ids_b, mask_b)

    score = similarity.item()
    print("-" * 50)
    print(f"代码 A: {code1[:50]}...")
    print(f"代码 B: {code2[:50]}...")
    print(f"语义相似度: {score:.4f}")

    if score > 0.8:
        print("判定结果: 【高度相似 / 疑似克隆】")
    elif score > 0.5:
        print("判定结果: 【部分相似】")
    else:
        print("判定结果: 【不相似】")
    print("-" * 50)


if __name__ == "__main__":
    # 测试案例 1: 变量名不同，逻辑相同 (Type-2/3 克隆)
    c1 = """
    def bubble_sort(arr):
        n = len(arr)
        for i in range(n):
            for j in range(0, n-i-1):
                if arr[j] > arr[j+1]:
                    arr[j], arr[j+1] = arr[j+1], arr[j]
    """

    c2 = """
    def sort_list(items):
        length = len(items)
        for x in range(length):
            for y in range(0, length-x-1):
                if items[y] > items[y+1]:
                    temp = items[y]
                    items[y] = items[y+1]
                    items[y+1] = temp
    """

    predict_similarity(c1, c2)

    # 测试案例 2: 完全不同的功能
    c3 = "def get_user_id(user): return user.id"
    predict_similarity(c1, c3)