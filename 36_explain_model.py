import shap
import xgboost as xgb
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.datasets import load_diabetes
from sklearn.model_selection import train_test_split


def main():
    # 1. 快速训练一个 XGBoost 模型 (复习第 29 课)
    print("Training Model...")
    data = load_diabetes()
    X = pd.DataFrame(data.data, columns=data.feature_names)
    y = data.target

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = xgb.XGBRegressor(n_estimators=100, max_depth=3)
    model.fit(X_train, y_train)

    # 2. 初始化 SHAP 解释器
    # TreeExplainer 是专门解释树模型的 (XGBoost, Random Forest)
    explainer = shap.TreeExplainer(model)

    # 3. 计算 SHAP 值 (解释 X_test 中的每一个样本)
    print("Calculating SHAP values...")
    shap_values = explainer.shap_values(X_test)

    # --- 可视化 1: 全局解释 (Beeswarm Plot) ---
    # 这张图是 SHAP 最经典的图
    # 每一个点代表一个样本。
    # 颜色越红 = 特征值越大。
    # x轴 = 对预测结果的影响 (正向还是负向)。
    print("Plotting Global Summary...")
    plt.figure()
    shap.summary_plot(shap_values, X_test, show=False)
    plt.title("SHAP Summary Plot")
    plt.tight_layout()
    plt.show()

    # --- 可视化 2: 单个样本解释 (Force Plot) ---
    # 解释为什么模型预测"第 0 个病人"的病情是这个数值？
    # 注意: force_plot 是交互式 JS 图表，通常在 Jupyter Notebook 里用。
    # 在 PyCharm 里，我们用 matplotlib 画一个简单的条形图代替。

    print("Plotting Single Prediction Explanation...")
    shap.plots.waterfall(shap.Explanation(values=shap_values[0],
                                          base_values=explainer.expected_value,
                                          data=X_test.iloc[0],
                                          feature_names=X.columns))
    plt.show()


if __name__ == "__main__":
    main()