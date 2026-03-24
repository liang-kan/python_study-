import cv2
import os
import numpy as np
from PIL import Image

# 解决控制台中文乱码问题（可选）
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def analyze_image(image_path):
    """分析单张图片质量"""
    result = {"filename": os.path.basename(image_path), "passed": False, "msg": ""}

    try:
        # 1. 硬指标检测 (Pillow)
        with Image.open(image_path) as img:
            width, height = img.size

            # 规则：太小直接不要
            if width < 400 or height < 300:
                result["msg"] = f"❌ 尺寸过小 ({width}x{height})"
                return result

        # 2. 画质检测 (OpenCV)
        # OpenCV读取中文路径需要特殊处理，这里用标准读取方式
        # 如果文件名有中文，cv2.imread 可能返回 None，建议用英文文件名测试，或用 imdecode
        cv_img = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), -1)

        if cv_img is None:
            result["msg"] = "❌ 文件损坏或格式不支持"
            return result

        # 转灰度
        if len(cv_img.shape) == 3:
            gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        else:
            gray = cv_img

        # 模糊检测 (Laplacian方差)
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()

        # 阈值设定：一般低于100觉得有点糊，低于50是非常糊
        if blur_score < 100:
            result["msg"] = f"❌ 图片模糊 (得分:{blur_score:.1f})"
            return result

        # 3. 简单内容检测 (边缘密度)
        edges = cv2.Canny(gray, 100, 200)
        edge_density = np.sum(edges) / (width * height)

        # 阈值：如果密度极高(>0.25)，通常是密密麻麻的文字截图
        if edge_density > 0.25:
            result["msg"] = f"❌ 疑似文档截图/文字过多 (密度:{edge_density:.2f})"
            return result

        # 通关
        result["passed"] = True
        result["msg"] = f"✅ 质量合格 (清晰度:{blur_score:.1f})"
        return result

    except Exception as e:
        result["msg"] = f"❌ 程序出错: {str(e)}"
        return result


if __name__ == "__main__":
    # 设置你的图片文件夹名字
    folder_name = "test_images"
    folder_path = os.path.join(os.getcwd(), folder_name)

    # 如果文件夹不存在，自动创建
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"\n[提示] 文件夹 '{folder_name}' 已创建！")
        print(f"请手动找几张图片放进去（找一张清晰的、一张模糊的、一张特别小的），然后重新运行脚本。\n")

    else:
        print(f"\n正在扫描 '{folder_name}' 文件夹...\n")
        print(f"{'文件名':<20} | {'结果'}")
        print("-" * 50)

        files = os.listdir(folder_path)
        if not files:
            print("文件夹是空的，请放入图片。")

        for f in files:
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                full_path = os.path.join(folder_path, f)
                res = analyze_image(full_path)
                print(f"{res['filename'][:18]:<20} | {res['msg']}")
        print("-" * 50)