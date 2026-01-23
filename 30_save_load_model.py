import joblib
from sklearn.datasets import load_iris
from sklearn.neighbors import KNeighborsClassifier
import os

# 定义文件名
MODEL_FILE = "iris_knn_model.pkl"


def train_and_save():
    print("--- Training Stage ---")
    data = load_iris()
    X, y = data.data, data.target

    # 训练一个简单的 KNN
    model = KNeighborsClassifier(n_neighbors=3)
    model.fit(X, y)
    print("Model trained.")

    # 保存模型 (序列化)
    # 相当于 Java 的 ObjectOutputStream
    joblib.dump(model, MODEL_FILE)
    print(f"Model saved to {MODEL_FILE}")


def load_and_predict():
    print("\n--- Inference Stage ---")
    if not os.path.exists(MODEL_FILE):
        print("Model file not found!")
        return

    # 加载模型 (反序列化)
    # 相当于 Java 的 ObjectInputStream
    loaded_model = joblib.load(MODEL_FILE)
    print("Model loaded successfully.")

    # 模拟新数据
    new_samples = [[5.1, 3.5, 1.4, 0.2], [6.0, 3.0, 4.0, 1.3]]
    predictions = loaded_model.predict(new_samples)

    print(f"Predictions for new data: {predictions}")


def main():
    # 1. 先训练并保存
    train_and_save()

    # 2. 模拟服务器重启，重新加载模型
    load_and_predict()


if __name__ == "__main__":
    main()