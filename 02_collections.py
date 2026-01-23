def main():
    # --- 1. 列表 (List) ---
    # Java: List<String> languages = new ArrayList<>(); languages.add("Java");
    languages = ["Java", "C++", "Go"]

    # 添加元素
    languages.append("Python")

    # 访问元素 (支持负数索引，表示倒数第几个)
    print(f"First: {languages[0]}")
    print(f"Last:  {languages[-1]}")  # Java 很难做到的操作

    # 切片 (Slicing) - 截取部分
    # Java: list.subList(0, 2)
    print(f"Top 2: {languages[0:2]}")

    # --- 2. 字典 (Dictionary) ---
    # Java: Map<String, Integer> map = new HashMap<>(); map.put("Tom", 95);
    scores = {
        "Tom": 95,
        "Jerry": 80,
        "Spike": 99
    }

    # 新增或修改
    scores["Tom"] = 100

    # 遍历 Map (这是重点)
    # Java: for (Map.Entry<String, Integer> entry : map.entrySet())
    print("\n--- Scores ---")
    for name, score in scores.items():
        print(f"{name}: {score}")

    # 安全获取值 (防止 NullPointerException)
    # Java: map.getOrDefault("Unknown", 0)
    print(f"Unknown User Score: {scores.get('Unknown', 0)}")


if __name__ == "__main__":
    main()