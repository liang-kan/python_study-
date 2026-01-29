import requests
import json
import time

url = "http://www.kfc.com.cn/kfccda/ashx/GetStoreList.ashx?op=keyword"

# 这是一个更完整的 Headers，模拟真实浏览器
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Origin": "http://www.kfc.com.cn",
    "Referer": "http://www.kfc.com.cn/kfccda/storelist/index.aspx",
    # 很多时候爬虫挂掉就是因为缺了 Referer (告诉服务器你是从哪个页面跳转过来的)
}

print("🍗 肯德基门店搜索器 (修复版)")
city = input("请输入城市: ")

data = {
    "cname": "",
    "pid": "",
    "keyword": city,
    "pageIndex": "1",
    "pageSize": "10"
}

try:
    response = requests.post(url, headers=headers, data=data)

    # 调试信息：如果下面报错，看看这里打印了什么
    # print(response.text)

    # 尝试解析
    result = response.json()

    # KFC 返回的数据结构有时候是 {"Table1": [...]}
    stores = result.get("Table1", [])

    if stores:
        print(f"\n✅ 成功找到 {result.get('rowcount')} 家门店！\n")
        for store in stores:
            print(f"🏠 {store.get('storeName'):<15} 📍 {store.get('addressDetail')}")
    else:
        print("❌ 没找到数据，可能是城市名不对，或者接口变了。")

except json.JSONDecodeError:
    print("❌ 解析失败！服务器返回的不是 JSON。")
    print(f"服务器返回内容: {response.text}")
except Exception as e:
    print(f"❌ 发生未知错误: {e}")