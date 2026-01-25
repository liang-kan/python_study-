import torch
from torchvision import transforms
from PIL import Image
import requests
import matplotlib.pyplot as plt
import numpy as np
import io


def get_image_from_url(url):
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    return Image.open(io.BytesIO(response.content))


def main():
    # 1. 下载一张测试图片
    url = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/PNG_transparency_demonstration_1.png/280px-PNG_transparency_demonstration_1.png"
    # 或者用我们之前的金毛犬
    url = "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c0/Golden_Retriever_with_tennis_ball.jpg/600px-Golden_Retriever_with_tennis_ball.jpg"

    try:
        orig_img = get_image_from_url(url)
    except:
        print("Download failed. Please check internet.")
        return

    # 2. 定义增强流水线 (Pipeline)
    # Compose 就像 LangChain 的 Chain，把处理步骤串起来
    train_transforms = transforms.Compose([
        transforms.Resize((200, 200)),  # 1. 统一缩放到 200x200
        transforms.RandomRotation(30),  # 2. 随机旋转 -30度 到 +30度
        transforms.RandomHorizontalFlip(p=0.5),  # 3. 50% 概率水平翻转 (镜像)
        transforms.ColorJitter(brightness=0.5),  # 4. 随机调整亮度
        # transforms.ToTensor()               # 最后通常会转成 Tensor，但为了画图我们先不转
    ])

    # 3. 生成 4 张增强后的图片
    print("Generating augmented images...")
    fig, axes = plt.subplots(1, 5, figsize=(15, 3))

    # 显示原图
    axes[0].imshow(orig_img)
    axes[0].set_title("Original")
    axes[0].axis('off')

    for i in range(4):
        # 每次调用 train_transforms(orig_img)，因为有 Random 步骤，结果都会不一样！
        aug_img = train_transforms(orig_img)

        axes[i + 1].imshow(aug_img)
        axes[i + 1].set_title(f"Augmented {i + 1}")
        axes[i + 1].axis('off')

    plt.show()


if __name__ == "__main__":
    main()