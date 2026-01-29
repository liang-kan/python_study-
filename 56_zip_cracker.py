import zipfile
import threading
import time

# 1. 配置目标
zip_filename = "test.zip"  # 你的加密压缩包
dictionary_file = "passwords.txt"  # 你的密码字典


def extract_file(z_file, password):
    """
    尝试用指定密码解压文件
    """
    try:
        # 密码需要转换为 bytes 类型 (utf-8 编码)
        password_bytes = password.encode('utf-8')

        # 尝试解压
        z_file.extractall(pwd=password_bytes)

        # 如果代码走到这里没报错，说明密码正确！
        print(f"\n✅ 找到密码了: {password}")
        return True

    except (RuntimeError, zipfile.BadZipFile):
        # 密码错误会报错，我们捕获它并不做任何事，继续下一个
        return False
    except Exception as e:
        # 其他未知错误
        print(f"❌ 发生未知错误: {e}")
        return False


def main():
    # 打开 zip 文件对象
    try:
        z_file = zipfile.ZipFile(zip_filename)
    except FileNotFoundError:
        print(f"❌ 找不到文件: {zip_filename}")
        return

    print(f"🚀 开始破解 {zip_filename} ...")

    # 记录开始时间
    start_time = time.time()

    # 打开字典文件，一行行读取
    with open(dictionary_file, 'r', encoding='utf-8') as f:
        for line in f:
            # 去掉行尾的换行符
            password = line.strip()

            if not password:
                continue

            # (可选) 打印正在尝试的密码，让过程看起来很酷
            # 为了不刷屏太快，可以用 \r 覆盖打印
            print(f"🔑 正在尝试: {password}   ", end="\r")

            # 调用破解函数
            if extract_file(z_file, password):
                # 找到后跳出循环
                break

    end_time = time.time()
    print(f"\n🏁 任务结束，耗时: {end_time - start_time:.4f} 秒")


if __name__ == "__main__":
    main()