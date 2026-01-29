import requests
from bs4 import BeautifulSoup
import csv
import time

# 1. 设置文件保存 (CSV格式，Excel可以直接打开)
# encoding='utf-8-sig' 是为了防止 Excel 打开中文乱码
file = open('quotes_data.csv', mode='w', newline='', encoding='utf-8-sig')
writer = csv.writer(file)
# 写入表头
writer.writerow(['名言内容', '作者', '标签'])

# 2. 伪装请求头 (User-Agent)
# 告诉服务器：我是一个浏览器，不是 Python 脚本 (虽然这个靶场不需要，但真实开发必须加)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# 3. 开始循环爬取前 5 页
print("🚀 爬虫启动！开始抓取数据...")

for page in range(1, 6):  # 范围 1 到 5
    print(f"📄 正在抓取第 {page} 页...")

    # 构造 URL
    url = f"http://quotes.toscrape.com/page/{page}/"

    # A. 发送请求
    response = requests.get(url, headers=headers)

    # 检查状态码 (200 代表成功)
    if response.status_code != 200:
        print(f"❌ 第 {page} 页请求失败")
        continue

    # B. 解析网页 (做汤)
    soup = BeautifulSoup(response.text, "html.parser")

    # C. 提取数据
    # 找到所有的名言方块 (div class="quote")
    quote_blocks = soup.find_all("div", class_="quote")

    for block in quote_blocks:
        # 1. 提取名言文本 (在 span class="text" 里)
        text = block.find("span", class_="text").text

        # 2. 提取作者 (在 small class="author" 里)
        author = block.find("small", class_="author").text

        # 3. 提取标签 (在 meta class="keywords" 的 content 属性里)
        # 或者遍历里面的 a 标签
        tags_meta = block.find("meta", class_="keywords")
        tags = tags_meta["content"] if tags_meta else "无标签"

        # D. 写入 CSV
        writer.writerow([text, author, tags])

    # 礼貌性延时，防止请求太快把人家服务器搞挂了
    time.sleep(1)

# 4. 关闭文件
file.close()
print("\n✅ 爬取完成！数据已保存到 'quotes_data.csv'。")