from fastapi import FastAPI
import uvicorn

# 1. 创建 App 实例
app = FastAPI()

# 模拟的数据库
fake_db = {
    "user_01": {"name": "Alice", "balance": 1000},
    "user_02": {"name": "Bob", "balance": 50},
    "user_03": {"name": "Charlie", "balance": 9999}
}

# 2. 定义路由 (Route)
# 当用户访问根目录 "/" 时
@app.get("/")
def home():
    return {"message": "欢迎来到我的数据 API 服务！"}

# 3. 定义带参数的路由
# 当用户访问 "/users/某人" 时
@app.get("/users/{user_id}")
def get_user_balance(user_id: str):
    """
    输入用户ID，返回用户详情
    """
    # 在字典里查找
    if user_id in fake_db:
        return fake_db[user_id]
    else:
        return {"error": "用户不存在", "status": 404}

# 4. 启动服务器 (仅在本地运行)
if __name__ == "__main__":
    # host="0.0.0.0" 表示允许局域网访问
    # port=8000 是端口号
    print("🚀 服务正在启动... 请在浏览器访问 http://127.0.0.1:8000")
    print("📄 自动文档地址: http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="127.0.0.1", port=8000)