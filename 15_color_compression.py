import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.utils import shuffle
import cv2


def main():
    # 1. 依然使用之前下载的那张图
    img_path = "marvel_faces.jpg"

    # OpenCV 默认读入是 BGR 格式，matplotlib 需要 RGB，所以要转一下
    img_bgr = cv2.imread(img_path)
    if img_bgr is None:
        print("Run previous script to download image first!")
        return

    img = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

    # 归一化：把像素值从 0-255 变成 0.0-1.0 (机器学习的标准操作)
    img = np.array(img, dtype=np.float64) / 255

    # 2. 变换数据形状
    # 图片是 (Height, Width, 3)，我们需要把它变成一个长列表 (Pixels, 3)
    # 这样每一行就是一个 RGB 颜色点
    w, h, d = tuple(img.shape)
    image_array = np.reshape(img, (w * h, d))

    print("Fitting model on a small sub-sample of the data...")
    # 为了速度，只取 1000 个像素点来训练模型
    image_array_sample = shuffle(image_array, random_state=0, n_samples=1000)

    # 3. K-Means 聚类
    # 告诉 AI：这张图里虽然有几万种颜色，但我只想要 4 种主色
    n_colors = 4
    kmeans = KMeans(n_clusters=n_colors, random_state=0).fit(image_array_sample)

    # 获取这 4 个中心颜色
    print(f"The {n_colors} main colors found are:\n{kmeans.cluster_centers_}")

    # 4. 预测整张图
    # 算出每一个像素点离哪个主色最近
    labels = kmeans.predict(image_array)

    # 5. 重构图片
    # 用那 4 个主色替换掉原来的几万种颜色
    new_img = np.zeros((w, h, d))
    label_idx = 0
    for i in range(w):
        for j in range(h):
            new_img[i][j] = kmeans.cluster_centers_[labels[label_idx]]
            label_idx += 1

    # 6. 画图对比
    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.axis('off')
    plt.title('Original Image')
    plt.imshow(img)

    plt.subplot(1, 2, 2)
    plt.axis('off')
    plt.title(f'Compressed ({n_colors} Colors)')
    plt.imshow(new_img)

    plt.show()


if __name__ == "__main__":
    main()