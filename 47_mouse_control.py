import pyautogui
import time
import random


def main():
    print("⚠️ WARNING: This script will move your mouse!")
    print("You have 3 seconds to switch to an empty Paint (画图) window or just watch desktop.")
    time.sleep(3)

    # 1. 获取屏幕分辨率
    width, height = pyautogui.size()
    print(f"Screen size: {width}x{height}")

    # 2. 鼠标画一个正方形
    distance = 200
    print("Drawing a square...")

    # 这里的 duration 是移动耗时
    # dragRel: 相对当前位置拖拽
    pyautogui.dragRel(distance, 0, duration=0.5)  # 向右
    pyautogui.dragRel(0, distance, duration=0.5)  # 向下
    pyautogui.dragRel(-distance, 0, duration=0.5)  # 向左
    pyautogui.dragRel(0, -distance, duration=0.5)  # 向上

    # 3. 键盘输入
    # 找个能输入文字的地方 (比如记事本)，脚本会自动打字
    # 这里我们只演示移动鼠标，防止误操作

    # 模拟按下 Win 键
    # pyautogui.press('win')
    # time.sleep(1)
    # pyautogui.write('notepad', interval=0.1)
    # pyautogui.press('enter')

    print("Done!")


if __name__ == "__main__":
    main()