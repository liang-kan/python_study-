import os
# 必加：使用国内镜像加速下载
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
from transformers import GPT2LMHeadModel, GPT2Tokenizer


def main():
    # 1. 加载 GPT-2 模型
    model_name = "distilgpt2"  # 也可以换成 'gpt2/distilgpt2' (更小)
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)
    model = GPT2LMHeadModel.from_pretrained(model_name)

    # 2. 初始提示词 (Prompt)
    input_text = "Once upon a time, there was a Java developer who learned Python,"

    # 编码
    input_ids = tokenizer.encode(input_text, return_tensors='pt')

    # 3. 生成文本
    print(f"Generating text based on: '{input_text}'...\n")

    # generate() 方法有很多参数控制生成的创造性
    output = model.generate(
        input_ids,
        max_length=100,  # 最大生成长度
        num_return_sequences=1,
        no_repeat_ngram_size=2,  # 防止它一直重复说废话
        temperature=0.7,  # 创造力 (0.7 比较平衡)
        do_sample=True,  # 随机采样 (不然每次结果都一样)
        top_k=50  # 只从概率最高的 50 个词里选
    )

    # 4. 解码并打印
    generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
    print("--- Generated Story ---")
    print(generated_text)


if __name__ == "__main__":
    main()