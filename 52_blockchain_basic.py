from web3 import Web3


def interact_with_blockchain():
    # 1. 连接到以太坊主网 (使用 Cloudflare 的公共免费节点)
    # 这就像连上了区块链的“互联网接口”
    rpc_url = "https://cloudflare-eth.com"
    w3 = Web3(Web3.HTTPProvider(rpc_url))

    # 2. 检查连接状态
    if w3.is_connected():
        print("✅ 成功连接到以太坊主网！")
    else:
        print("❌ 连接失败，请检查网络。")
        return

    # 3. 获取当前最新的区块高度 (相当于区块链的“楼层”)
    latest_block = w3.eth.block_number
    print(f"🔗 当前以太坊最新区块高度: {latest_block}")

    # 4. 离线生成一个新的钱包 (账号)
    # 这一步是在你本地生成的，非常安全，不会上传到网络
    account = w3.eth.account.create()
    print("\n🎫 --- 本地生成新钱包 ---")
    print(f"地址 (公钥): {account.address}")
    print(f"私钥 (切勿泄露): {account.key.hex()}")
    # 注意：真实开发中，私钥绝对不能print出来，这里仅用于演示结构

    # 5. 查询余额 (读取链上数据)
    # 我们可以查一下以太坊创始人 Vitalik Buterin 的公开钱包地址看看他有多少钱
    # 这是一个公开的 ENS 地址对应的钱包
    vitalik_address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"

    # 获取余额 (单位是 Wei，这是以太坊最小单位)
    balance_wei = w3.eth.get_balance(vitalik_address)

    # 将 Wei 转换为 Ether (1 Ether = 10^18 Wei)
    balance_eth = w3.from_wei(balance_wei, 'ether')

    print(f"\n💰 --- 查询大户余额 ---")
    print(f"目标地址: {vitalik_address}")
    print(f"余额 (Wei): {balance_wei}")
    print(f"余额 (ETH): {balance_eth:.4f} ETH")


if __name__ == "__main__":
    interact_with_blockchain()