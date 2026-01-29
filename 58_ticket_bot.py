import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# 1. 启动浏览器
print("🚀 正在启动浏览器...")
# 自动下载并设置适合你电脑的 Chrome 驱动
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# 2. 打开目标网页
# 注意：这里我们要用绝对路径打开本地文件
# 这里的路径必须改成你电脑上实际存放 ticket_page.html 的路径
import os

file_path = "file://" + os.path.abspath("ticket_page.html")
driver.get(file_path)

print("👀 页面已打开，正在监控按钮状态...")

# 3. 循环检测逻辑 (抢票核心)
while True:
    try:
        # A. 寻找按钮元素
        # 我们根据 HTML 里的 id="buy_btn" 来找
        btn = driver.find_element(By.ID, "buy_btn")

        # B. 检查按钮是否包含 disabled 属性
        # 如果 get_attribute("disabled") 返回 None，说明按钮可用了！
        if btn.get_attribute("disabled") is None:
            print("⚡ 按钮已激活！点击中！！！")
            btn.click()
            break  # 抢到了就退出循环
        else:
            # 按钮还不能点
            print("⏳ 等待开售...", end="\r")

            # 真实抢票中，这里通常需要 driver.refresh() 刷新页面
            # 但我们的模拟网页是倒计时自动变，所以不需要刷新，只需要等待
            time.sleep(0.1)

    except Exception as e:
        print(f"❌ 出错了: {e}")
        break

# 抢到后，留给用户一点时间看结果，不要马上关浏览器
print("\n✅ 脚本执行完毕。")
input("按回车键关闭浏览器...")
driver.quit()