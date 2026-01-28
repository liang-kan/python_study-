import socket
import time
from datetime import datetime


def scan_port(target_ip, port):
    """尝试连接指定端口，返回是否开放"""
    try:
        # AF_INET = IPv4, SOCK_STREAM = TCP
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # 设置超时时间 (0.5秒)，不然扫描太慢
        sock.settimeout(0.5)

        # connect_ex 成功返回 0，失败返回错误码
        result = sock.connect_ex((target_ip, port))

        sock.close()

        if result == 0:
            return True
        else:
            return False
    except:
        return False


def main():
    # 目标：扫你自己 (localhost) 或者路由器的 IP
    # 也可以扫 "scanme.nmap.org" (这是 Nmap 官方提供的合法测试靶机)
    # target = "127.0.0.1"
    target = "scanme.nmap.org"

    print(f"--- Starting Scan on host: {target} ---")
    start_time = datetime.now()

    # 扫描常用端口 (你可以改成 range(1, 1025) 扫前1000个)
    common_ports = [21, 22, 23, 25, 53, 80, 110, 135, 139, 443, 445, 1433, 1521, 3306, 3389, 5000, 8000, 8080]
    # common_ports = range(1, 20000)

    open_ports = []

    for port in common_ports:
        # print(f"Scanning port {port}...", end="\r") # \r 不换行打印
        is_open = scan_port(target, port)

        if is_open:
            print(f"[+] Port {port} is OPEN")
            open_ports.append(port)
        else:
            # print(f"[-] Port {port} is closed")
            pass

    end_time = datetime.now()
    duration = end_time - start_time

    print(f"\n--- Scan Completed in {duration} ---")
    print(f"Open Ports: {open_ports}")


if __name__ == "__main__":
    main()
