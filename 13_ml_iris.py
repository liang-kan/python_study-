from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
import pandas as pd


def main():
    # 1. 加载经典数据集 (Iris)
    # 数据包含 150 朵花，4 个特征 (花萼/花瓣的长宽)，3 个品种
    iris = load_iris()
    X = iris.data  # 特征矩阵 (Feature Matrix)
    y = iris.target  # 目标标签 (Target Vector): 0, 1, 2 代表三种花

    # 打印看一眼数据长啥样
    feature_names = iris.feature_names
    print(f"Features: {feature_names}")
    print(f"Example data (Row 0): {X[0]} -> Label: {y[0]}")

    # 2. 划分数据集
    # 80% 用来训练 (学习)，20% 用来考试 (测试)
    # random_state=42 是为了保证每次运行结果一致 (42是宇宙终极答案)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 3. 选择模型：K-近邻算法 (KNN)
    # 逻辑很简单：新来一朵花，看它离已知的哪 3 朵花最近，谁多就听谁的。
    model = KNeighborsClassifier(n_neighbors=3)

    # 4. 训练模型 (Training)
    print("\nTraining model...")
    model.fit(X_train, y_train)

    # 5. 预测与评估 (Evaluation)
    y_pred = model.predict(X_test)

    # 算出准确率
    acc = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy: {acc * 100:.2f}%")

    # 6. 实战演示：预测一朵新花
    # 假设我们在路边捡到一朵花，测量数据如下：
    # [花萼长, 花萼宽, 花瓣长, 花瓣宽]
    new_flower = [[5.1, 3.5, 1.4, 0.2]]
    prediction = model.predict(new_flower)
    predicted_name = iris.target_names[prediction[0]]

    print(f"\nNew flower prediction: Class {prediction[0]} ({predicted_name})")


if __name__ == "__main__":
    main()