import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def main():
    # 1. 模拟数据生成
    # 假设我们有 100 天的销售数据
    days = 100

    # 创建一个 DataFrame (相当于 Excel 表格)
    # date_range: 自动生成日期序列
    df = pd.DataFrame({
        "Date": pd.date_range(start="2023-01-01", periods=days),
        # 生成正态分布的随机数作为销售额 (平均值 1000，波动 200)
        "Sales": np.random.normal(loc=1000, scale=200, size=days),
        # 生成随机类别
        "Category": np.random.choice(["Electronics", "Clothing", "Home"], size=days)
    })

    # 故意制造一些脏数据 (模拟真实世界)
    df.loc[5, "Sales"] = np.nan  # 第 5 天数据丢失

    # 2. 数据清洗 (Pandas 的强项)
    print("--- Raw Data Head ---")
    print(df.head())  # 打印前 5 行

    # 填充缺失值 (用平均值填充)
    mean_val = df["Sales"].mean()
    df["Sales"] = df["Sales"].fillna(mean_val)

    # 3. 数据统计
    print("\n--- Sales by Category ---")
    # Group By 类似 SQL: SELECT Category, SUM(Sales) FROM df GROUP BY Category
    summary = df.groupby("Category")["Sales"].sum()
    print(summary)

    # 4. 可视化 (画图)
    # 设置画图风格
    sns.set_theme(style="whitegrid")

    # 创建一个画布，包含 2 个子图 (1行 2列)
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    # 图 1: 折线图 (Line Plot) - 销售额趋势
    sns.lineplot(data=df, x="Date", y="Sales", ax=axes[0], color="blue")
    axes[0].set_title("Daily Sales Trend")
    axes[0].set_ylabel("Sales Amount ($)")

    # 图 2: 箱线图 (Box Plot) - 不同类别的销售分布
    sns.boxplot(data=df, x="Category", y="Sales", ax=axes[1], palette="Set2")
    axes[1].set_title("Sales Distribution by Category")

    # 调整布局并显示
    plt.tight_layout()
    print("\nDisplaying plot window...")
    plt.show()  # 这会弹出一个窗口显示图片


if __name__ == "__main__":
    main()