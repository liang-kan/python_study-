import matplotlib.pyplot as plt
from sklearn import datasets, metrics
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split


def main():
    # 1. 加载手写数字数据集
    # 这是一个 8x8 像素的灰度图集合
    digits = datasets.load_digits()

    # 看看第一张图是啥
    print("Example data matrix (8x8):")
    print(digits.images[0])

    # 展平图像：把 8x8 的二维矩阵变成 64 个特征的一维数组
    n_samples = len(digits.images)
    data = digits.images.reshape((n_samples, -1))

    # 2. 划分训练集和测试集 (50% 训练，50% 测试)
    X_train, X_test, y_train, y_test = train_test_split(
        data, digits.target, test_size=0.5, shuffle=False
    )

    # 3. 构建神经网络
    # hidden_layer_sizes=(50,): 只有一个隐藏层，里面有 50 个神经元
    # max_iter=1000: 最多训练 1000 轮
    # alpha=1e-4: 正则化参数，防止过拟合
    # solver='sgd': 随机梯度下降 (Stochastic Gradient Descent)，神经网络的核心算法
    mlp = MLPClassifier(hidden_layer_sizes=(50,), max_iter=1000, alpha=1e-4,
                        solver='sgd', verbose=10, random_state=1,
                        learning_rate_init=0.1)

    # 4. 训练 (这个过程就是在疯狂调整神经元之间的权重)
    print("Training Neural Network...")
    mlp.fit(X_train, y_train)

    # 5. 预测
    predicted = mlp.predict(X_test)

    # 6. 评估结果
    print(f"\nAccuracy: {metrics.accuracy_score(y_test, predicted) * 100:.2f}%")

    # 打印分类报告
    print(f"\nClassification report:\n{metrics.classification_report(y_test, predicted)}")

    # 7. 可视化展示前 4 个预测结果
    _, axes = plt.subplots(nrows=1, ncols=4, figsize=(10, 3))
    for ax, image, prediction in zip(axes, X_test, predicted):
        ax.set_axis_off()
        # 把一维数组还原回 8x8 用于显示
        image = image.reshape(8, 8)
        ax.imshow(image, cmap=plt.cm.gray_r, interpolation="nearest")
        ax.set_title(f"Pred: {prediction}")

    plt.show()


if __name__ == "__main__":
    main()