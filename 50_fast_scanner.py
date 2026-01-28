import socket
import threading
from queue import Queue

# 线程锁，防止打印乱码
print_lock = threading.Lock()

# target = "127.0.0.1"
target = "scanme.nmap.org"


def port_scan(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.5)
    try:
        con = s.connect((target, port))
        with print_lock:
            print(f"[+] Port {port} is OPEN")
        con.close()
    except:
        pass


# 线程工作函数 (Worker)
def threader():
    while True:
        # 从队列里拿一个端口号
        worker_port = q.get()

        port_scan(worker_port)

        # 告诉队列任务完成了
        q.task_done()


# 创建队列
q = Queue()


def main():
    print(f"Scanning {target} with 100 threads...")

    # 1. 创建 100 个线程
    for x in range(100):
        t = threading.Thread(target=threader)
        t.daemon = True  # 守护线程，主程序结束它也结束
        t.start()

    # 2. 把任务塞进队列 (扫描 1 到 1000 端口)
    for worker in range(1, 60000):
        q.put(worker)

    # 3. 等待队列清空 (join)
    q.join()

    print("Scan complete.")


if __name__ == "__main__":
    main()