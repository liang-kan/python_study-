import pandas as pd
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report


def main():
    # 1. 加载乳腺癌数据集 (二分类问题)
    # 这是一个非常经典的医疗数据集，特征包含细胞核的半径、质地等
    data = load_breast_cancer()
    X = data.data
    y = data.target

    print(f"Dataset shape: {X.shape}")  # (569, 30)

    # 2. 划分数据集
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 3. 初始化一个基础模型 (随机森林)
    # 随机森林有很多参数：树的棵数(n_estimators), 最大深度(max_depth)等
    rf = RandomForestClassifier(random_state=42)

    # 4. 定义参数网格 (Parameter Grid)
    # 我们想尝试以下所有组合：
    # n_estimators: [50, 100, 200] (3种)
    # max_depth: [None, 10, 20] (3种)
    # min_samples_split: [2, 5] (2种)
    # 总共尝试次数: 3 * 3 * 2 = 18 次组合
    # 还要乘以 5 折交叉验证 (CV=5)，实际训练 18 * 5 = 90 次
    param_grid = {
        'n_estimators': [50, 100, 200],
        'max_depth': [None, 10, 20],
        'min_samples_split': [2, 5]
    }

    # 5. 配置网格搜索
    # cv=5: 交叉验证，把训练集分成 5 份，轮流做验证集，确保结果不偶然
    # n_jobs=-1: 动用所有 CPU 核心并行跑 (Java 里的 ForkJoinPool)
    # verbose=2: 打印进度
    print("Starting Grid Search (this involves training many models)...")
    grid_search = GridSearchCV(estimator=rf, param_grid=param_grid, cv=5, n_jobs=-1, verbose=1)

    # 6. 开始暴力搜索 (Training)
    grid_search.fit(X_train, y_train)

    # 7. 查看结果
    print("\n--- Tuning Results ---")
    print(f"Best Parameters: {grid_search.best_params_}")
    print(f"Best CV Score: {grid_search.best_score_:.4f}")

    # 8. 使用最优模型进行预测
    # grid_search.best_estimator_ 已经是训练好的最优模型了
    best_model = grid_search.best_estimator_
    y_pred = best_model.predict(X_test)

    print("\n--- Test Set Evaluation ---")
    print(classification_report(y_test, y_pred, target_names=data.target_names))


if __name__ == "__main__":
    main()