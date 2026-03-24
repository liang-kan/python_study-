import streamlit as st
import requests
import re
import pandas as pd
import time
import json
import os
import datetime
import numpy as np

# --- 1. 配置与常量 ---
DATA_FILE = "my_funds.json"
st.set_page_config(page_title="基金实盘助手 v5.1", layout="wide", page_icon="📡")


# --- 2. 核心函数：数据存取 ---
def load_holdings():
    df = pd.DataFrame()
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                df = pd.DataFrame(json.load(f))
        except:
            pass
    if df.empty:
        # 默认数据
        default_data = [
            {"基金代码": "017436", "持仓份额": 2945.88, "持仓成本": 0.0, "标签": "美股"},
            {"基金代码": "018927", "持仓份额": 2012.38, "持仓成本": 0.0, "标签": "美股"},
            {"基金代码": "018463", "持仓份额": 933.12, "持仓成本": 0.0, "标签": "美股"},
            {"基金代码": "012349", "持仓份额": 1080.20, "持仓成本": 0.0, "标签": "消费"},
            {"基金代码": "018419", "持仓份额": 2303.73, "持仓成本": 0.0, "标签": "美股"},
            {"基金代码": "008182", "持仓份额": 3039.76, "持仓成本": 0.0, "标签": "科技"},
            {"基金代码": "000834", "持仓份额": 618.12, "持仓成本": 0.0, "标签": "宽基"},
            {"基金代码": "025490", "持仓份额": 346.50, "持仓成本": 0.0, "标签": "其他"},
            {"基金代码": "000850", "持仓份额": 1030.03, "持仓成本": 0.0, "标签": "医药"},
            {"基金代码": "023754", "持仓份额": 3140.10, "持仓成本": 0.0, "标签": "其他"},
            {"基金代码": "015945", "持仓份额": 1940.53, "持仓成本": 0.0, "标签": "港股"},
            {"基金代码": "015790", "持仓份额": 10564.00, "持仓成本": 0.0, "标签": "白酒"},
            {"基金代码": "020425", "持仓份额": 2521.00, "持仓成本": 0.0, "标签": "红利"},
            {"基金代码": "004253", "持仓份额": 4515.00, "持仓成本": 0.0, "标签": "黄金"}
        ]
        df = pd.DataFrame(default_data)

    required_cols = {"基金代码": str, "持仓份额": float, "持仓成本": float, "标签": str}
    for col, dtype in required_cols.items():
        if col not in df.columns:
            df[col] = "未分类" if dtype == str else 0.0
        df[col] = df[col].astype(dtype)
    return df


def save_holdings(df):
    df.to_json(DATA_FILE, orient="records", force_ascii=False)


# --- 3. 基础函数：基金行情 ---
def get_fund_data(code):
    timestamp = int(time.time() * 1000)
    url = f"http://fundgz.1234567.com.cn/js/{code}.js?rt={timestamp}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=2)
        match = re.search(r'jsonpgz\((.*?)\);', response.text)
        if match:
            data = json.loads(match.group(1))
            dwjz = float(data['dwjz']) if data['dwjz'] else 0.0
            gszzl = float(data['gszzl']) if data['gszzl'] else 0.0
            return {
                "name": data['name'],
                "dwjz": dwjz,
                "gszzl": gszzl,
                "time": data['gztime']
            }
    except:
        return None
    return None


# --- 4. 进阶函数：历史走势 ---
@st.cache_data(ttl=3600)
def get_fund_history(code):
    url = f"http://fund.eastmoney.com/pingzhongdata/{code}.js"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        match = re.search(r'var Data_netWorthTrend = (\[.*?\]);', response.text)
        if match:
            data_list = json.loads(match.group(1))
            df = pd.DataFrame(data_list)
            df['日期'] = pd.to_datetime(df['x'], unit='ms')
            df['净值'] = df['y']
            df.set_index('日期', inplace=True)
            return df[['净值']]
    except:
        pass
    return None


# --- 🌟 5. 高级函数：重仓股与技术分析 (已修复) ---

@st.cache_data(ttl=86400)
def get_top_holdings(fund_code):
    """
    【修复版】使用天天基金 APP 接口获取持仓，稳定性更高。
    同时自动过滤非A股代码，防止报错。
    """
    url = "https://fundmobapi.eastmoney.com/FundMNewApi/FundMNInverstPosition"
    params = {
        "FCODE": fund_code,
        "deviceid": "Wap",
        "plat": "Wap",
        "product": "EFund",
        "version": "6.6.0",
    }
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, params=params, headers=headers, timeout=3)
        data = response.json()

        stocks = []
        if data and "Datas" in data and data["Datas"]:
            for item in data["Datas"]:
                code = str(item['GPDM'])  # 股票代码
                name = str(item['GPJC'])  # 股票名称

                # 🛠️ 关键过滤逻辑：只保留 A 股 (6开头沪市, 0/3开头深市)
                # 过滤掉港股(5位代码) 或 美股(字母代码)
                if len(code) == 6 and (code.startswith('6') or code.startswith('0') or code.startswith('3')):
                    market = 'sh' if code.startswith('6') else 'sz'
                    stocks.append({"market": market, "code": code, "name": name})

        return stocks
    except Exception as e:
        print(f"Fetching holdings error: {e}")
        return []


def get_stock_kline(market, code):
    """获取股票K线并计算RSI"""
    secid = f"1.{code}" if market == 'sh' else f"0.{code}"
    url = f"http://push2his.eastmoney.com/api/qt/stock/kline/get?secid={secid}&fields1=f1&fields2=f51,f52,f53,f54,f55&klt=101&fqt=1&end=20500101&lmt=30"

    try:
        res = requests.get(url, timeout=2).json()
        if res['data'] and res['data']['klines']:
            klines = res['data']['klines']
            closes = [float(x.split(',')[2]) for x in klines]

            rsi = calculate_rsi(np.array(closes))
            current_price = closes[-1]
            last_day_change = (closes[-1] - closes[-2]) / closes[-2] * 100

            return {
                "price": current_price,
                "pct": last_day_change,
                "rsi": rsi
            }
    except:
        pass
    return None


def calculate_rsi(prices, period=14):
    if len(prices) < period + 1: return 50
    deltas = np.diff(prices)
    seed = deltas[:period + 1]
    up = seed[seed >= 0].sum() / period
    down = -seed[seed < 0].sum() / period
    rs = up / down if down != 0 else 0
    rsi = np.zeros_like(prices)
    rsi[:period] = 100. - 100. / (1. + rs)

    for i in range(period, len(prices)):
        delta = deltas[i - 1]
        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta

        up = (up * (period - 1) + upval) / period
        down = (down * (period - 1) + downval) / period
        rs = up / down if down != 0 else 0
        rsi[i] = 100. - 100. / (1. + rs)
    return rsi[-1]


# --- 6. 辅助函数 ---
def mask_number(value, is_hidden, fmt="{:,.2f}"):
    return "****" if is_hidden else fmt.format(value)


# --- 7. 页面侧边栏 ---
with st.sidebar:
    st.title("📡 基金实盘助手 v5.1")
    privacy_mode = st.toggle("🙈 隐私模式", value=False)

    st.divider()
    df_holdings = load_holdings()
    edited_df = st.data_editor(
        df_holdings,
        num_rows="dynamic",
        column_config={
            "基金代码": st.column_config.TextColumn(help="6位代码"),
            "持仓份额": st.column_config.NumberColumn(format="%.2f"),
            "持仓成本": st.column_config.NumberColumn(format="%.4f"),
            "标签": st.column_config.SelectboxColumn(
                options=["美股", "黄金", "白酒", "科技", "医药", "债券", "宽基", "港股", "红利", "其他"],
                required=True
            )
        },
        key="editor"
    )

    if not edited_df.equals(df_holdings):
        save_holdings(edited_df)
        st.toast("✅ 数据已保存")
        time.sleep(0.5)
        st.rerun()

    if st.button("🔄 刷新行情"):
        st.rerun()
    auto_refresh = st.checkbox("60s 自动刷新")

# --- 8. 主逻辑 ---
if edited_df.empty:
    st.info("👈 请添加持仓")
    st.stop()

fund_list = []
total_daily_profit = 0
total_accum_profit = 0
total_asset = 0

bar = st.progress(0, text="正在同步行情...")
for index, row in edited_df.iterrows():
    code = row["基金代码"].strip()
    if not code: continue
    info = get_fund_data(code)
    share = row["持仓份额"]
    cost = row["持仓成本"]
    tag = row["标签"]

    if info:
        curr_price = info['dwjz'] * (1 + info['gszzl'] / 100)
        daily_profit = info['dwjz'] * (info['gszzl'] / 100) * share
        curr_asset = curr_price * share
        accum_profit = (curr_price - cost) * share if cost > 0 else 0

        fund_list.append({
            "基金名称": info['name'],
            "代码": code,
            "标签": tag,
            "当前净值": curr_price,
            "涨跌幅": info['gszzl'],
            "持仓份额": share,
            "持仓成本": cost,
            "持有市值": curr_asset,
            "今日盈亏": daily_profit,
            "累计盈亏": accum_profit
        })
        total_daily_profit += daily_profit
        total_accum_profit += accum_profit
        total_asset += curr_asset
    bar.progress((index + 1) / len(edited_df))
bar.empty()

# --- 9. 看板 ---
k1, k2, k3, k4 = st.columns(4)
display_asset = mask_number(total_asset, privacy_mode, "¥ {:,.0f}")
display_daily = mask_number(total_daily_profit, privacy_mode, "¥ {:+.2f}")
display_accum = mask_number(total_accum_profit, privacy_mode, "¥ {:+.0f}")

k1.metric("预估总资产", display_asset)
daily_pct = (total_daily_profit / total_asset * 100) if total_asset > 0 else 0
k2.metric("今日盈亏", display_daily, f"{daily_pct:+.2f}%", delta_color="inverse")
k3.metric("累计盈亏", display_accum, delta_color="inverse" if total_accum_profit != 0 else "off")
k4.metric("红盘数量", f"{len([x for x in fund_list if x['今日盈亏'] > 0])} / {len(fund_list)}")

st.divider()

# --- 10. 核心视图区 ---
tab_list, tab_history, tab_alert = st.tabs(["📋 持仓明细", "📈 净值走势", "⚠️ 智能预警(A股专用)"])

with tab_list:
    if fund_list:
        df = pd.DataFrame(fund_list)
        df.sort_values(by="今日盈亏", ascending=False, inplace=True)
        display_df = df.copy()
        if privacy_mode:
            for col in ["持有市值", "今日盈亏", "累计盈亏", "持仓份额", "持仓成本"]:
                display_df[col] = "****"
        st.dataframe(
            display_df.style.map(
                lambda x: 'color: #d62728' if isinstance(x, (int, float)) and x > 0 else 'color: #2ca02c' if isinstance(
                    x, (int, float)) and x < 0 else '', subset=['涨跌幅']),
            column_order=("基金名称", "代码", "标签", "涨跌幅", "今日盈亏", "持有市值", "累计盈亏", "当前净值"),
            use_container_width=True, hide_index=True
        )

with tab_history:
    st.caption("🔎 查看基金历史走势")
    if fund_list:
        c1, c2 = st.columns([1, 3])
        with c1:
            options = [f"{f['基金名称']} ({f['代码']})" for f in fund_list]
            selected_option = st.selectbox("选择基金", options)
            selected_code = re.search(r'\((.*?)\)', selected_option).group(1)
            time_range = st.radio("时间", ["近3月", "近1年", "历史全量"], index=1)
        with c2:
            hist_df = get_fund_history(selected_code)
            if hist_df is not None and not hist_df.empty:
                if time_range == "近3月":
                    plot_df = hist_df.tail(66)
                elif time_range == "近1年":
                    plot_df = hist_df.tail(252)
                else:
                    plot_df = hist_df
                st.line_chart(plot_df, color="#d62728")
            else:
                st.warning("暂无历史数据")

# --- 🌟 智能预警模块 (RSI分析) ---
with tab_alert:
    st.subheader("⚠️ 重仓股 RSI 超卖监控")
    st.info(
        "💡 提示：该功能仅支持分析【A股持仓】。如果选中【QDII/美股/黄金】基金，系统将自动跳过或显示为空，因为无法获取海外股票的实时K线数据。")

    # 过滤掉明显的 QDII 标签，提升体验
    valid_funds = [f for f in fund_list if f['标签'] not in ['美股', '黄金', 'QDII', '债券']]
    alert_options = [f"{f['基金名称']} ({f['代码']})" for f in valid_funds]

    if not alert_options:
        st.warning("当前没有检测到明确的A股权益类基金，无法分析。请检查侧边栏的【标签】设置。")
    else:
        target_fund = st.selectbox("选择基金 (A股)", alert_options, key="alert_select")
        target_code = re.search(r'\((.*?)\)', target_fund).group(1)

        if st.button("🚀 开始分析重仓股"):
            with st.status(f"正在深度扫描 {target_fund} ...", expanded=True) as status:

                # 1. 获取重仓股 (使用修复后的 APP 接口)
                st.write("正在从官方数据库获取前十大重仓股...")
                stocks = get_top_holdings(target_code)

                if not stocks:
                    status.update(label="未获取到A股重仓数据 (可能是QDII/新基)", state="error")
                    st.error(
                        "分析中止：未找到该基金的 A 股重仓数据。这通常是因为该基金是 QDII、ETF联接(黄金/美股) 或 新发基金。")
                    st.stop()

                # 2. 获取K线
                st.write(f"正在计算 {len(stocks)} 只股票的 RSI 指标...")
                stock_data = []
                progress = st.progress(0)

                for i, s in enumerate(stocks):
                    k_data = get_stock_kline(s['market'], s['code'])
                    if k_data:
                        signal = "⚪ 观望"
                        score = 0
                        if k_data['rsi'] < 20:
                            signal = "🔴 极度超卖"
                            score = 2
                        elif k_data['rsi'] < 30:
                            signal = "🟠 超卖区域"
                            score = 1
                        elif k_data['rsi'] > 70:
                            signal = "🟢 超买 (止盈?)"
                            score = -1

                        stock_data.append({
                            "股票名称": s['name'],
                            "代码": s['code'],
                            "最新价": k_data['price'],
                            "涨跌幅": f"{k_data['pct']:.2f}%",
                            "RSI(14)": f"{k_data['rsi']:.1f}",
                            "信号参考": signal,
                            "score": score
                        })
                    progress.progress((i + 1) / len(stocks))

                status.update(label="分析完成！", state="complete")

                # 3. 结果展示
                if stock_data:
                    res_df = pd.DataFrame(stock_data)
                    res_df = res_df.sort_values(by="RSI(14)", ascending=True)

                    st.divider()
                    st.write(f"📊 **{target_fund} 前十大重仓股信号**")


                    def highlight_signal(val):
                        if "🔴" in val: return "color: red; font-weight: bold"
                        if "🟠" in val: return "color: orange; font-weight: bold"
                        if "🟢" in val: return "color: green"
                        return ""


                    st.dataframe(
                        res_df.style.map(highlight_signal, subset=["信号参考"]),
                        column_order=("股票名称", "代码", "最新价", "涨跌幅", "RSI(14)", "信号参考"),
                        use_container_width=True,
                        hide_index=True
                    )

                    # 汇总建议
                    oversold_count = len(res_df[res_df['score'] > 0])
                    if oversold_count >= 3:
                        st.success(f"🔥 **加仓机会？** 发现 {oversold_count} 只重仓股处于超卖状态，基金短期可能反弹。")
                    else:
                        st.info("☁️ **情绪平稳**：重仓股暂无极端信号。")