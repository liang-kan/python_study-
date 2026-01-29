import json
from web3 import Web3

# 1. 更换为更稳定的免费 RPC 节点
# 备选1: https://eth.llamarpc.com (强烈推荐，隐私且稳定)
# 备选2: https://rpc.ankr.com/eth
rpc_url = "https://eth.llamarpc.com"
w3 = Web3(Web3.HTTPProvider(rpc_url))

if not w3.is_connected():
    print("❌ 连接失败，请检查网络")
    exit()

# 2. 准备数据
# 注意：这里使用了 w3.to_checksum_address 确保地址格式绝对正确
usdt_contract_address = w3.to_checksum_address("0xdAC17F958D2ee523a2206206994597C13D831ec7")

min_abi = json.loads('''[
    {
        "constant": true,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    },
    {
        "constant": true,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function"
    },
    {
        "constant": true,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function"
    }
]''')

contract = w3.eth.contract(address=usdt_contract_address, abi=min_abi)

# 目标地址 (币安热钱包)
target_address = w3.to_checksum_address("0xF977814e90dA44bFA03b6295A0616a897441aceC")

print(f"🎯 正在通过 LlamaRPC 查询地址: {target_address}")

try:
    # 5. 调用合约函数
    symbol = contract.functions.symbol().call()
    decimals = contract.functions.decimals().call()
    raw_balance = contract.functions.balanceOf(target_address).call()

    print(f"✅ 成功读取合约: {symbol}")
    print(f"ℹ️  合约精度: {decimals}")
    print(f"💰 原始余额 (整数): {raw_balance}")

    # 6. 计算真实余额
    real_balance = raw_balance / (10 ** decimals)
    print(f"💵 真实余额: {real_balance:,.2f} {symbol}")

except Exception as e:
    print(f"❌ 查询出错: {e}")