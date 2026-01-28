import pandas as pd
import numpy as np


def create_dummy_excel(filename="sales_data.xlsx"):
    """创建一个模拟的 Excel 文件"""
    df = pd.DataFrame({
        "Order_ID": range(1, 21),  # 20个订单
        "Product": np.random.choice(["Laptop", "Mouse", "Keyboard"], 20),
        "Amount": np.random.randint(100, 10000, 20),
        "Region": np.random.choice(["North", "South", "East", "West"], 20)
    })
    df.to_excel(filename, index=False)
    print(f"Created {filename}")


def process_excel():
    input_file = "sales_data.xlsx"
    output_file = "high_value_orders.xlsx"

    # 1. 制造数据
    create_dummy_excel(input_file)

    # 2. 读取 Excel
    print("Reading Excel...")
    df = pd.read_excel(input_file)

    # 3. 数据过滤 (类似于 SQL: SELECT * FROM df WHERE Amount > 5000)
    # 这就是 Python 的强大之处，一行代码搞定
    high_value_df = df[df["Amount"] > 5000]

    print(f"Found {len(high_value_df)} high value orders.")

    # 4. 写入新的 Excel (带样式)
    # 使用 ExcelWriter 引擎
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        # 写数据
        high_value_df.to_excel(writer, sheet_name='BigOrders', index=False)

        # 获取 workbook 和 worksheet 对象
        workbook = writer.book
        worksheet = writer.sheets['BigOrders']

        # 定义样式: 黄色背景，加粗
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#FFFF00',  # 黄色
            'border': 1
        })

        # 设置列宽
        worksheet.set_column('A:D', 15)

        # 重写表头应用样式
        for col_num, value in enumerate(high_value_df.columns.values):
            worksheet.write(0, col_num, value, header_format)

    print(f"Report saved to {output_file}")


if __name__ == "__main__":
    process_excel()