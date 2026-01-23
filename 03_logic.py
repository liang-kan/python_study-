def main():
    numbers = [1, 2, 3, 4, 5, 6]

    # --- 1. 传统的 For 循环 ---
    # Java: for (int n : numbers)
    print("Even numbers (Loop):")
    for n in numbers:
        if n % 2 == 0:
            print(n)

    # --- 2. 列表推导式 (List Comprehension) ---
    # 这是 Python 的精华。一行代码完成 过滤 + 转换。
    # Java: numbers.stream().map(n -> n*n).collect(Collectors.toList())

    squares = [n * n for n in numbers]
    print(f"Squares: {squares}")

    # 带条件的推导式
    # Java: stream().filter(n -> n > 3).collect(...)
    big_numbers = [n for n in numbers if n > 3]
    print(f"Numbers > 3: {big_numbers}")

    # --- 3. Range (生成数字序列) ---
    # Java: for (int i = 0; i < 5; i++)
    print("Count 0 to 4:")
    for i in range(5):
        print(i, end=" ")  # end=" " 表示不换行


if __name__ == "__main__":
    main()