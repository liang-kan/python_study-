# 类型提示 (Type Hints): Python 3.5+ 特性
# 虽然 Python 是动态的，但我们可以像 Java 一样写类型，IDE 会有提示
def calculate_price(price: float, tax_rate: float = 0.1, discount: float = 0) -> float:
    """
    这是一个文档字符串 (Docstring)，相当于 JavaDoc
    tax_rate 默认是 0.1 (10%)
    discount 默认是 0
    """
    total = price * (1 + tax_rate) - discount
    return total


def main():
    # 1. 正常调用
    p1 = calculate_price(100.0)
    print(f"Price 1: {p1}")

    # 2. 覆盖默认参数
    p2 = calculate_price(100.0, 0.2)
    print(f"Price 2 (High Tax): {p2}")

    # 3. 关键字参数 (Keyword Arguments) - Java 并没有的功能
    # 可以不按顺序传参，只要指定名字
    p3 = calculate_price(price=100.0, discount=10.0, tax_rate=0.05)
    print(f"Price 3 (Custom order): {p3}")


if __name__ == "__main__":
    main()