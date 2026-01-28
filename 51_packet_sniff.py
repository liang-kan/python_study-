from scapy.all import *

# 1. 简单的抓包 (类似 Wireshark)
# 抓取 5 个包，只看 TCP 协议
print("Sniffing 5 packets...")


def packet_callback(packet):
    # 如果包里有 TCP 层
    if packet.haslayer(TCP):
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        src_port = packet[TCP].sport
        dst_port = packet[TCP].dport

        print(f"TCP Packet: {src_ip}:{src_port} -> {dst_ip}:{dst_port}")


# sniff 函数是阻塞的，直到抓够 count 个包
# filter="tcp": BPF 过滤语法
sniff(filter="tcp", prn=packet_callback, count=5)

print("\n--- Custom Packet Creation ---")
# 2. 构造一个自定义的 Ping 包 (ICMP)
# IP层: 目标是 Google DNS
ip_layer = IP(dst="8.8.8.8")
# ICMP层: 类型是 Echo Request
icmp_layer = ICMP()

# 组合包 (使用 / 符号，非常直观)
packet = ip_layer / icmp_layer

print("Sending custom Ping packet...")
# sr1: send and receive 1 packet
response = sr1(packet, timeout=2, verbose=False)

if response:
    print(f"Received reply from {response[IP].src}")
    response.show()  # 打印包的详细结构
else:
    print("No response.")