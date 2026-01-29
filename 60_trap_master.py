import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# 启动
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# 打开靶场
file_path = "file://" + os.path.abspath("trap_page.html")
driver.get(file_path)
driver.maximize_window()

# --- 第一关：处理 Alert 弹窗 ---
print("\n🛡️  正在挑战第一关：弹窗...")
driver.find_element(By.ID, "alert_btn").click()
time.sleep(1)  # 停一下让你看到弹窗

try:
    # 1. 切换视角到 Alert
    alert = driver.switch_to.alert
    print(f"   捕获到弹窗内容: {alert.text}")

    # 2. 点击确定 (accept)
    # 如果要点取消，用 alert.dismiss()
    alert.accept()
    print("✅ 弹窗已关闭！")
except:
    print("❌ 没有检测到弹窗！")

# --- 第二关：处理 IFrame ---
print("\n🛡️  正在挑战第二关：IFrame...")
try:
    # 直接找肯定报错，因为按钮在结界里
    # driver.find_element(By.ID, "frame_btn").click() # 这行会报错

    # 1. 切换进入 IFrame
    # 可以传 ID，也可以传 element 对象
    driver.switch_to.frame("inner_frame")
    print("   已进入 Frame 内部世界")

    # 2. 现在可以点击了
    btn = driver.find_element(By.ID, "frame_btn")
    print(f"   找到按钮文本: {btn.text}")

    # 3. !!! 重要 !!! 办完事必须切回主文档
    # 否则你后续找外面的元素都找不到
    driver.switch_to.default_content()
    print("✅ 已切回主世界！")
except Exception as e:
    print(f"❌ IFrame 操作失败: {e}")

# --- 第三关：处理新标签页 ---
print("\n🛡️  正在挑战第三关：多窗口切换...")

# 记录当前窗口的 ID (句柄)
original_window = driver.current_window_handle
print(f"   当前窗口 ID: {original_window}")

# 点击链接，弹出新窗口
driver.find_element(By.ID, "new_tab_link").click()
time.sleep(2)  # 等新窗口弹出来

# 此时 driver 依然停留在老窗口！如果不切换，找百度搜索框会报错
# 获取所有打开的窗口 ID 列表
all_windows = driver.window_handles
print(f"   所有窗口 ID: {all_windows}")

# 遍历寻找新窗口
for window_handle in all_windows:
    if window_handle != original_window:
        # 切换到新窗口
        driver.switch_to.window(window_handle)
        break

print(f"   已切换到新窗口: {driver.title}")

# 验证一下：在新窗口找百度的搜索框
try:
    driver.find_element(By.ID, "kw").send_keys("Selenium 窗口切换")
    print("✅ 在新窗口操作成功！")
except:
    print("❌ 没找到元素，可能切换失败")

# (可选) 关掉新窗口，切回老窗口
driver.close()
driver.switch_to.window(original_window)
print("🔙 已回到老窗口")

# 结束
time.sleep(3)
driver.quit()