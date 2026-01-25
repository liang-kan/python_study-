import optuna
import xgboost as xgb
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


# 1. 定义目标函数 (Objective Function)
# 这是 Optuna 的核心。Optuna 会不断调用这个函数，
# 每次传入不同的 trial (尝试对象)，我们需要返回一个分数 (accuracy) 给它。
def objective(trial):
    # --- A. 加载数据 ---
    data = load_breast_cancer()
    X_train, X_test, y_train, y_test = train_test_split(data.data, data.target, test_size=0.2, random_state=42)

    # --- B. 让 Optuna 帮我们"猜"参数 ---
    # trial.suggest_xxx 就是定义搜索空间

    # 猜整数：树的数量在 50 到 300 之间
    n_estimators = trial.suggest_int('n_estimators', 50, 300)

    # 猜整数：树的最大深度在 3 到 10 之间
    max_depth = trial.suggest_int('max_depth', 3, 10)

    # 猜浮点数：学习率在 0.01 到 0.3 之间 (对数刻度)
    learning_rate = trial.suggest_float('learning_rate', 0.01, 0.3, log=True)

    # 猜子样本比例：每次抽 50%~100% 的数据建树
    subsample = trial.suggest_float('subsample', 0.5, 1.0)

    # --- C. 构建并训练模型 ---
    # 把猜出来的参数填进去
    model = xgb.XGBClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        learning_rate=learning_rate,
        subsample=subsample,
        use_label_encoder=False,
        eval_metric='logloss',
        random_state=42
    )

    model.fit(X_train, y_train)

    # --- D. 返回分数 ---
    # Optuna 根据这个分数来判断这组参数好不好
    preds = model.predict(X_test)
    accuracy = accuracy_score(y_test, preds)

    return accuracy


def main():
    print("Start Optuna Optimization...")

    # 2. 创建一个 Study (研究项目)
    # direction='maximize' 表示我们的目标是让 accuracy 越大越好
    study = optuna.create_study(direction='maximize')

    # 3. 开始优化
    # n_trials=20: 即使让它试 20 次 (Grid Search 可能要试几百次)
    study.optimize(objective, n_trials=20)

    # 4. 打印最佳结果
    print("\n--- Tuning Finished ---")
    print(f"Best Accuracy: {study.best_value:.4f}")
    print("Best Params:")
    for key, value in study.best_params.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()