import json
import requests  # 用来发送 HTTP 请求获取 JSON 数据
from web3 import Web3

# 1. 还是用 LlamaRPC 节点，稳！
rpc_url = "https://eth.llamarpc.com"
w3 = Web3(Web3.HTTPProvider(rpc_url))

if not w3.is_connected():
    print("❌ 连接失败")
    exit()

# 2. 准备 BAYC (无聊猿) 的合约信息
# 注意：使用 to_checksum_address 防止大小写报错
bayc_address = w3.to_checksum_address("0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D")

# NFT 专用的最小 ABI
nft_abi = json.loads('''[
    {
        "inputs": [{"internalType": "uint256", "name": "tokenId", "type": "uint256"}],
        "name": "ownerOf",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "uint256", "name": "tokenId", "type": "uint256"}],
        "name": "tokenURI",
        "outputs": [{"internalType": "string", "name": "", "type": "string"}],
        "stateMutability": "view",
        "type": "function"
    }
]''')

contract = w3.eth.contract(address=bayc_address, abi=nft_abi)

# 3. 选择你要查询的猴子编号 (ID)
# 无聊猿一共有 10000 只 (0 - 9999)
# 我们可以试试 460 (这只是 Justin Bieber 曾经买过的) 或者随便选一个
token_id = 460

print(f"🐒 正在查询无聊猿 BAYC #{token_id} ...")

try:
    # 4. 查主人 (ownerOf)
    owner = contract.functions.ownerOf(token_id).call()
    print(f"👤 当前持有者地址: {owner}")

    # 5. 查数据链接 (tokenURI)
    # 这就是 NFT 的“灵魂”，它指向一张身份证
    uri = contract.functions.tokenURI(token_id).call()
    print(f"🔗 元数据链接 (URI): {uri}")

    # 6. 处理 IPFS 链接 (关键步骤！)
    # 很多 NFT 的链接是 "ipfs://xxx"，浏览器打不开，Python 也无法直接请求
    # 我们需要把它替换成公共网关 "https://ipfs.io/ipfs/xxx"
    if uri.startswith("ipfs://"):
        http_url = uri.replace("ipfs://", "https://ipfs.io/ipfs/")
    else:
        http_url = uri

    print(f"🌐 正在从 IPFS 下载元数据...")

    # 发送请求获取具体的 JSON 内容
    response = requests.get(http_url, timeout=10)

    if response.status_code == 200:
        metadata = response.json()

        # 7. 提取图片链接
        image_url = metadata.get("image")
        # 同样的，如果图片也是 ipfs:// 开头，也要转换
        if image_url and image_url.startswith("ipfs://"):
            image_url = image_url.replace("ipfs://", "https://ipfs.io/ipfs/")

        print("\n🎨 --- NFT 详情 ---")
        print(f"图片地址: {image_url}")
        print("请按住 Ctrl 并点击上面的链接查看图片！")

        # 看看有什么属性 (Traits)
        attributes = metadata.get("attributes", [])
        print(f"属性数量: {len(attributes)} 个")
        for attr in attributes:
            print(f"  - {attr['trait_type']}: {attr['value']}")

    else:
        print("❌ 下载元数据失败")

except Exception as e:
    print(f"❌ 发生错误: {e}")