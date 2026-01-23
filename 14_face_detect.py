import cv2
import numpy as np
import requests
import os


def download_sample_image(filename, url):
    """
    下载图片，增加了 Headers 伪装成浏览器，防止被拦截
    """
    if not os.path.exists(filename):
        print(f"Downloading from {url}...")

        # 伪装头部信息：告诉服务器我是 Windows 上的 Chrome 浏览器
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }

        try:
            resp = requests.get(url, headers=headers, timeout=10)

            # 检查是否成功 (200 OK)
            if resp.status_code == 200:
                with open(filename, 'wb') as f:
                    f.write(resp.content)
                print("Download successful.")
            else:
                print(f"Download failed. Status Code: {resp.status_code}")
        except Exception as e:
            print(f"Download error: {e}")


def main():
    # 使用你提供的 Marvel 合照
    img_url = "https://files.nowre.com/articles/2018/02/Marvel-Studios-21class-photo.jpg"
    img_path = "marvel_faces.jpg"

    # 1. 下载图片
    download_sample_image(img_path, img_url)

    # 检查文件是否存在且不为空
    if not os.path.exists(img_path) or os.path.getsize(img_path) == 0:
        print("Error: Image file not found or empty. Please check the download function.")
        # 备选方案：如果代码下载实在不行，请手动把图片下载下来，命名为 marvel_faces.jpg 放在同级目录
        return

    # 2. 读取图片
    img = cv2.imread(img_path)
    if img is None:
        print("Failed to load image with OpenCV.")
        return

    # 3. 转换为灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 4. 加载分类器
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # 5. 检测人脸
    # 对于这种大合照，我们需要调整参数：
    # minNeighbors: 调低一点 (比如 3)，因为合照里人脸可能不清晰，太严格会漏检
    # minSize: 调小一点 (比如 20x20)，因为合照里人脸很小
    print("Detecting faces... (This might take a moment)")
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=2, minSize=(10, 10))

    print(f"Found {len(faces)} faces!")

    # 6. 画框
    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # 7. 显示结果
    # 因为原图可能非常大，我们缩小一点显示，不然屏幕装不下
    # 获取原图尺寸
    h, w = img.shape[:2]
    # 如果宽度大于 1200，缩放一下
    if w > 1200:
        scale_ratio = 1200 / w
        new_dim = (1200, int(h * scale_ratio))
        img = cv2.resize(img, new_dim, interpolation=cv2.INTER_AREA)

    cv2.imshow('Face Detection', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()