import time
import pickle
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# 1. 启动浏览器
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# 2. 先打开目标网站 (这一步很重要！)
# 必须先打开域名，才能写入该域名的 Cookies，否则浏览器会报错
driver.get("https://www.baidu.com")

print("👀 当前状态：未登录 (看右上角)")
time.sleep(2)  # 让你看清楚现在是没登录的

# 3. 读取并加载 Cookies
if os.path.exists("baidu_cookies.pkl"):
    print("📂 发现 Cookies 文件，正在加载...")

    with open("baidu_cookies.pkl", "rb") as f:
        cookies = pickle.load(f)

    for cookie in cookies:
        # 有时候 expiry (过期时间) 会导致报错，有些脚本会选择去掉它
        # 这里我们直接添加
        driver.add_cookie(cookie)

    print("✅ Cookies 加载完毕！正在刷新页面...")

    # 4. 刷新页面，让 Cookies 生效
    driver.refresh()

    print("🎉 恭喜！现在应该是已登录状态了！")
else:
    print("❌ 没有找到 Cookie 文件，请先运行 save_cookies.py")

# 停一会让你检查效果
time.sleep(10)
driver.quit()