import requests
import json
import os

# 1. 目标 API
url = "https://pvp.qq.com/web201605/js/herolist.json"

# 2. 伪装 Headers (腾讯通常不太查这个，但习惯要养好)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

print("🎮 正在请求王者荣耀英雄数据...")

try:
    response = requests.get(url, headers=headers)

    # 3. 解析 JSON
    hero_list = response.json()

    print(f"✅ 成功获取！共有 {len(hero_list)} 位英雄。\n")

    # 4. 创建图片保存目录
    save_dir = "heros_img"
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)

    print(f"📂 图片将保存到: {save_dir} 文件夹")
    print("-" * 30)

    # 5. 遍历抓取前 5 个英雄演示 (避免下载几百张太慢)
    for hero in hero_list[:5]:
        cname = hero['cname']  # 名字
        ename = hero['ename']  # ID

        # 构造头像 URL 规律
        # 官网头像规律通常是: https://game.gtimg.cn/images/yxzj/img201606/heroimg/{ID}/{ID}.jpg
        img_url = f"https://game.gtimg.cn/images/yxzj/img201606/heroimg/{ename}/{ename}.jpg"

        print(f"📥 正在下载: {cname} ...", end="")

        # 下载图片
        img_resp = requests.get(img_url, headers=headers)

        # 保存文件
        if img_resp.status_code == 200:
            with open(f"{save_dir}/{cname}.jpg", "wb") as f:
                f.write(img_resp.content)
            print(" ✅ 完成")
        else:
            print(" ❌ 图片下载失败")

    print("\n🎉 演示结束！请打开文件夹查看图片。")

except Exception as e:
    print(f"❌ 出错了: {e}")