import pyautogui
import time


def auto_type_anywhat():
    print("⚠️ 警告：程序将在 3 秒后接管你的键盘鼠标！")
    print("⚠️ 请确保你的输入法已经切换为【英文模式】，否则可能无法输入！")
    print("3...")
    time.sleep(1)
    print("2...")
    time.sleep(1)
    print("1... Action!")
    time.sleep(1)

    # --- 1. 打开记事本 ---
    # 模拟按下 Win + R
    pyautogui.hotkey('win', 'r')
    time.sleep(0.5)  # 等窗口弹出来

    # 输入 notepad 并回车
    pyautogui.write('notepad')
    pyautogui.press('enter')

    # 等待记事本完全打开
    time.sleep(1)

    # --- 2. 输入 "AnyWhat" ---
    # 为了看起来像黑客在打字，我们设置 interval (打字间隔)
    target_word = "AnyWhat"

    # 比如我们想打个标题
    pyautogui.write("Hello, I am Python Agent.", interval=0.05)
    pyautogui.press('enter')
    pyautogui.press('enter')  # 空两行

    # --- 3. 循环书写 ---
    for i in range(5):
        # f-string 格式化
        line_content = f"[{i + 1}] Writing: {target_word}"

        # interval=0.1 表示每个字母间隔 0.1 秒，看起来很有科技感
        pyautogui.write(line_content, interval=0.1)

        # 换行
        pyautogui.press('enter')

    # --- 4. 结束 ---
    # 模拟按下 Ctrl + A 全选 (演示组合键)
    # pyautogui.hotkey('ctrl', 'a')

    print("Mission Complete.")


if __name__ == "__main__":
    # 为了防止程序失控，PyAutoGUI 提供了一个保险措施：
    # 如果你把鼠标猛地移到屏幕四个角的任何一个角，程序会自动报错停止。
    pyautogui.FAILSAFE = True

    auto_type_anywhat()