def main():
    # 1.变量声明
    # Java： int age =25; String name = "Python";
    # Python: 不需要 声明类型，自动引导
    age = 25
    name = "Python"
    # 注意：True/False 首字母大写，Java 是 true/false
    is_java_dev = True
    # 2. 字符串格式化 (f-string) - 这是 Python 3.6+ 的杀手级特性
    # Java: String.format("Hi, I am %s", name) 或 "Hi, I am " + name
    print(f"Hello,I am learing {name}.My age is {age} .")
    # 3. 类型转换
    # Java: Integer.parseInt("100")
    score_str = "100"
    score_int = int(score_str)
    print(f"Next year score: {score_int +1}.")
    # 4. 类型检查
    # Java: if (obj instanceof String)
    if isinstance(name, str):
        print(f"'{name}' is a string object.")

if __name__ == "__main__":
    main()