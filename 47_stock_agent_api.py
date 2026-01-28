from fastapi import FastAPI
from pydantic import BaseModel
import random

app = FastAPI()


# --- 1. 定义工具函数 ---
def get_stock_price(symbol: str):
    """模拟获取股价"""
    # 随机生成一个价格
    price = round(random.uniform(100, 200), 2)
    return f"${price}"


def get_stock_news(symbol: str):
    """模拟获取新闻"""
    news = [
        f"{symbol} announces new AI product.",
        f"Analysts upgrade {symbol} rating.",
        f"{symbol} faces supply chain issues."
    ]
    return random.choice(news)


# --- 2. 定义 Agent 逻辑 ---
# 这就是一个硬编码的 "Agent"，专门处理股票任务
def stock_analyst_agent(symbol: str):
    # 第一步：查价格
    price = get_stock_price(symbol)

    # 第二步：查新闻
    news = get_stock_news(symbol)

    # 第三步：生成报告 (模拟 LLM 的总结能力)
    report = {
        "symbol": symbol,
        "current_price": price,
        "latest_news": news,
        "recommendation": "Buy" if "upgrade" in news else "Hold"
    }
    return report


# --- 3. 定义 API ---
class StockRequest(BaseModel):
    symbol: str


@app.post("/analyze_stock")
def analyze(request: StockRequest):
    print(f"Agent received task: Analyze {request.symbol}")
    result = stock_analyst_agent(request.symbol)
    return result


# --- 4. 启动 ---
if __name__ == "__main__":
    import uvicorn

    print("Starting Stock Agent API...")
    # 访问 http://localhost:8000/docs 进行测试
    uvicorn.run(app, host="0.0.0.0", port=8000)