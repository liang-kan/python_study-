import streamlit as st
import torch
from torchvision import models, transforms
from PIL import Image
import requests
import json


# --- 1. 加载模型 (增加缓存装饰器，避免每次刷新页面都重载模型) ---
@st.cache_resource
def load_model():
    # 这一步和第 19 课一模一样
    model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    model.eval()
    return model


@st.cache_data
def load_labels():
    # 下载 ImageNet 标签
    url = "https://raw.githubusercontent.com/anishathalye/imagenet-simple-labels/master/imagenet-simple-labels.json"
    return requests.get(url).json()


# --- 2. 图像预处理 ---
def process_image(image):
    preprocess = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    img_t = preprocess(image)
    return torch.unsqueeze(img_t, 0)


# --- 3. 主界面逻辑 (Streamlit 的魔法) ---
def main():
    # 设置网页标题
    st.title("🐶 AI Image Classifier")
    st.write("Upload an image, and the AI will tell you what it is!")

    # 侧边栏
    st.sidebar.header("About")
    st.sidebar.text("Model: ResNet-18")
    st.sidebar.text("Framework: PyTorch")

    # 文件上传组件
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        # 显示用户上传的图片
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Image', use_column_width=True)

        # 添加一个按钮
        if st.button('Identify'):
            with st.spinner('AI is thinking...'):
                # 加载模型和标签
                model = load_model()
                labels = load_labels()

                # 预处理
                batch_t = process_image(image)

                # 推理
                with torch.no_grad():
                    out = model(batch_t)

                # 获取前 3 名
                percentages = torch.nn.functional.softmax(out, dim=1)[0] * 100
                _, indices = torch.sort(out, descending=True)

                # --- 显示结果 ---
                st.success("Analysis Complete!")
                st.subheader("Top Predictions:")

                # 用进度条展示置信度
                for idx in indices[0][:3]:
                    label = labels[idx]
                    score = percentages[idx].item()
                    st.write(f"**{label}** ({score:.2f}%)")
                    st.progress(int(score))


if __name__ == "__main__":
    main()