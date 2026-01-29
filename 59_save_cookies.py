import time
import pickle  # 用来保存数据的库
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# 1. 启动浏览器
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# 2. 打开目标网站
driver.get("https://www.baidu.com")
driver.maximize_window()

print("🚨 请在 30 秒内手动完成登录操作！")
print("⏳ 计时开始...")

# 给用户足够的时间去扫码登录
time.sleep(30)

# 3. 此时假设你已经登录了，我们把 Cookies 拿出来
cookies = driver.get_cookies()

# 4. 保存到本地文件 "baidu_cookies.pkl"
# "wb" 意思是 write binary (二进制写入)
with open("baidu_cookies.pkl", "wb") as f:
    pickle.dump(cookies, f)

print(f"✅ Cookies 已保存！共 {len(cookies)} 条数据。")
print("现在你可以关闭浏览器了。")

driver.quit()