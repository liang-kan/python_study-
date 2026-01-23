import json
import os


def main():
    # 你的数据
    app_config = {
        "app_name": "PyCharm Demo",
        "version": 2.0,
        "features": ["smart_code_completion", "debugger"],
        "database": {"host": "127.0.0.1", "port": 5432}
    }

    filename = "config.json"

    # 写文件
    # Tip: 在 PyCharm 里输入 'with' 然后 Tab，可能会有模板
    print(f"Writing to {filename}...")
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(app_config, f, indent=4)

    # 读文件
    print("Reading file...")
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # 这里的 data 是一个字典
            print(f"Loaded App Name: {data['app_name']}")


if __name__ == "__main__":
    main()