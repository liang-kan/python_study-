import zipfile
import threading
import queue
import itertools
import time

# --- 配置区域 ---
zip_filename = "test.zip"
thread_count = 10  # 雇佣 10 个工人
# ----------------

# 1. 创建一个全局的“停止信号”
# 当有人找到密码时，把这个设为 True，其他人就可以下班了
stop_event = threading.Event()


def attempt_crack(zip_file, password_queue):
    """
    这是工人的工作流程
    """
    # 每个线程需要单独打开文件句柄，避免争抢同一个文件指针出错
    try:
        z_file = zipfile.ZipFile(zip_file)
    except Exception:
        return

    while not password_queue.empty():
        # 如果有人喊停，就立刻停止
        if stop_event.is_set():
            break

        # 从队列里拿一个密码
        try:
            password = password_queue.get(timeout=0.1)
        except queue.Empty:
            break

        # 尝试解压
        try:
            # 这里的逻辑和上一课一样
            z_file.extractall(pwd=password.encode('utf-8'))

            # 成功了！
            print(f"\n\n🎉 找到了！密码是: {password}")
            print(f"🧵 功臣线程: {threading.current_thread().name}")

            # 发出停止信号
            stop_event.set()

        except (RuntimeError, zipfile.BadZipFile):
            # 失败是常态，不做处理，继续下一个
            pass
        except Exception as e:
            print(e)
        finally:
            # 告诉队列，这个任务做完了
            password_queue.task_done()


def main():
    print(f"🚀 正在准备多线程爆破: {zip_filename}")

    # 2. 准备队列 (大池子)
    pass_queue = queue.Queue()

    # 3. 生产密码 (0000 - 9999)
    print("📦 正在生成密码字典...")
    chars = "0123456789"
    for p in itertools.product(chars, repeat=4):
        pass_queue.put("".join(p))

    print(f"✅ 字典准备完毕，共 {pass_queue.qsize()} 个密码。")
    print(f"⚡ 启动 {thread_count} 个线程开始轰炸...\n")

    start_time = time.time()

    # 4. 创建并启动线程
    threads = []
    for i in range(thread_count):
        t = threading.Thread(target=attempt_crack, args=(zip_filename, pass_queue), name=f"Worker-{i + 1}")
        t.start()
        threads.append(t)

    # 5. 等待所有线程结束
    for t in threads:
        t.join()

    end_time = time.time()
    print(f"\n🏁 任务结束，耗时: {end_time - start_time:.4f} 秒")


if __name__ == "__main__":
    main()