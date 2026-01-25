import xgboost as xgb
from sklearn.datasets import load_diabetes
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
import pandas as pd


def main():
    # 1. 加载糖尿病数据集 (回归问题)
    # 目标是预测一年后的疾病进展指标 (数值)，而不是分类
    data = load_diabetes()
    X = pd.DataFrame(data.data, columns=data.feature_names)
    y = data.target

    # 2. 划分数据
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 3. 构建 XGBoost 回归模型
    # XGBoost 有很多参数，核心是：
    # n_estimators: 树的数量
    # learning_rate: 学习率 (每棵树的贡献权重，越小越稳，但需要更多树)
    # max_depth: 树的深度 (防止过拟合)
    model = xgb.XGBRegressor(
        n_estimators=1000,
        learning_rate=0.05,
        max_depth=8,
        early_stopping_rounds=10,  # 重要：如果连着 10 次效果没提升，就提前停止 (防止过拟合)
        n_jobs=-1
    )

    # 4. 训练 (带验证集)
    # eval_set: 用来让模型一边学一边考试，看看有没有过拟合
    print("Training XGBoost...")
    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        verbose=False  # 设为 True 可以看到每一步的 Loss
    )

    # 5. 预测
    y_pred = model.predict(X_test)

    # 6. 评估 (MSE 和 R2 Score)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    print(f"\nModel Performance:")
    print(f"MSE: {mse:.2f}")
    print(f"R2 Score: {r2:.4f} (越接近 1 越好)")

    # 7. 特征重要性 (Feature Importance) - 它是可解释的 AI
    # 查看哪些特征对病情影响最大
    print("\nFeature Importances:")
    # model.feature_importances_ 是一个数组
    importance_df = pd.DataFrame({
        'Feature': X.columns,
        'Importance': model.feature_importances_
    }).sort_values(by='Importance', ascending=False)

    print(importance_df)

    # 8. 画图 (XGBoost 自带画图功能)
    xgb.plot_importance(model)
    plt.title("XGBoost Feature Importance")
    plt.show()


if __name__ == "__main__":
    main()