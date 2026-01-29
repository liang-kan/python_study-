import time
from web3 import Web3

# 1. 配置连接
rpc_url = "https://cloudflare-eth.com"
w3 = Web3(Web3.HTTPProvider(rpc_url))

# 检查连接
if not w3.is_connected():
    print("❌ 连接失败")
    exit()
else:
    print("✅ 连接成功，监控系统启动中...")

# 2. 定义我们要监控的“鲸鱼”列表
# 这里可以放你感兴趣的任何地址
targets = [
    "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",  # Vitalik Buterin (V神)
    "0xF977814e90dA44bFA03b6295A0616a897441aceC",  # Binance Hot Wallet (币安热钱包)
]

# 3. 初始化“记事本” (字典)
# 结构: { "地址A": 余额A, "地址B": 余额B }
last_balances = {}

print("🔍 正在初始化初始余额数据...")
for address in targets:
    # 获取余额 (Wei)
    balance = w3.eth.get_balance(address)
    # 存入字典
    last_balances[address] = balance
    print(f"   - {address[:10]}... 初始余额: {w3.from_wei(balance, 'ether'):.4f} ETH")

print("🚀 监控已开始！(按 Ctrl+C 停止)")
print("-" * 30)

# 4. 开始死循环监控
try:
    while True:
        # 遍历每一个目标地址
        for address in targets:
            # 获取当前最新余额
            current_balance = w3.eth.get_balance(address)

            # 读取上一次记录的余额
            previous_balance = last_balances[address]

            # 5. 核心判断：是否变化？
            if current_balance != previous_balance:
                # 计算变化量
                diff = current_balance - previous_balance
                # 转换成 ETH 单位方便阅读
                diff_eth = w3.from_wei(diff, 'ether')

                # 打印警报 (加上时间戳)
                current_time = time.strftime("%H:%M:%S", time.localtime())
                print(f"\n🚨 [警报 {current_time}] 资金异动！")
                print(f"   🏠 地址: {address}")

                if diff > 0:
                    print(f"   📈 进账: +{diff_eth:.6f} ETH")
                else:
                    print(f"   📉 转出: {diff_eth:.6f} ETH")

                # !!! 非常重要：更新“记事本”，否则会一直重复报警
                last_balances[address] = current_balance

            # (可选) 如果没变化，也可以打印个点点，证明程序还活着
            # print(".", end="", flush=True)

        # 6. 休息一下
        # 很多公共节点限制每秒请求次数，建议至少停 5-10 秒
        time.sleep(10)

except KeyboardInterrupt:
    print("\n🛑 监控已停止。")