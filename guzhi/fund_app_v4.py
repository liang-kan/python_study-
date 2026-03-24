import streamlit as st
import requests
import re
import pandas as pd
import time
import json
import os
import datetime

# --- 1. 配置与常量 ---
DATA_FILE = "my_funds.json"
st.set_page_config(page_title="基金实盘助手 v4.0", layout="wide", page_icon="📈")


# --- 2. 核心函数：数据存取 ---
def load_holdings():
    """读取数据，自动兼容升级"""
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

    # 补全缺失列
    required_cols = {"基金代码": str, "持仓份额": float, "持仓成本": float, "标签": str}
    for col, dtype in required_cols.items():
        if col not in df.columns:
            df[col] = "未分类" if dtype == str else 0.0
        df[col] = df[col].astype(dtype)
    return df


def save_holdings(df):
    df.to_json(DATA_FILE, orient="records", force_ascii=False)


# --- 3. 核心函数：网络请求 (实时数据) ---
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


# --- 🌟 新增函数：获取历史走势 (缓存优化) ---
@st.cache_data(ttl=3600)  # 缓存1小时，避免频繁请求
def get_fund_history(code):
    """获取基金历史净值数据"""
    # 这个接口包含基金所有的历史净值
    url = f"http://fund.eastmoney.com/pingzhongdata/{code}.js"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers, timeout=5)
        # 接口返回的是 JS 变量赋值，我们需要正则提取 Data_netWorthTrend
        # 格式：var Data_netWorthTrend = [{"x":1698249600000,"y":1.234,"equityReturn":0.5}, ...];
        match = re.search(r'var Data_netWorthTrend = (\[.*?\]);', response.text)

        if match:
            json_str = match.group(1)
            data_list = json.loads(json_str)

            # 转换为 DataFrame
            df = pd.DataFrame(data_list)
            # x 是毫秒级时间戳，y 是单位净值
            df['日期'] = pd.to_datetime(df['x'], unit='ms')
            df['净值'] = df['y']
            df.set_index('日期', inplace=True)
            return df[['净值']]
    except Exception as e:
        print(f"History error: {e}")
        return None
    return None


# --- 4. 辅助函数 ---
def mask_number(value, is_hidden, fmt="{:,.2f}"):
    return "****" if is_hidden else fmt.format(value)


# --- 5. 侧边栏 ---
with st.sidebar:
    st.title("🦁 基金实盘助手 Pro")
    privacy_mode = st.toggle("🙈 隐私模式", value=False)

    st.divider()
    st.subheader("💼 持仓管理")

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

# --- 6. 主逻辑计算 ---
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

    # 基础数据
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

# --- 7. 看板展示 ---
k1, k2, k3, k4 = st.columns(4)

display_asset = mask_number(total_asset, privacy_mode, "¥ {:,.0f}")
display_daily = mask_number(total_daily_profit, privacy_mode, "¥ {:+.2f}")
display_accum = mask_number(total_accum_profit, privacy_mode, "¥ {:+.0f}")

k1.metric("预估总资产", display_asset)
daily_pct = (total_daily_profit / total_asset * 100) if total_asset > 0 else 0
k2.metric("今日盈亏", display_daily, f"{daily_pct:+.2f}%", delta_color="inverse")
k3.metric("累计盈亏", display_accum, delta_color="inverse" if total_accum_profit != 0 else "off")
profit_num = len([x for x in fund_list if x['今日盈亏'] > 0])
k4.metric("红盘数量", f"{profit_num} / {len(fund_list)}")

st.divider()

# --- 8. 核心视图区 (新增：走势分析) ---
tab_list, tab_analysis, tab_history = st.tabs(["📋 持仓明细", "📊 资产分析", "📈 净值走势"])

# Tab 1: 列表
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
            column_config={
                "当前净值": st.column_config.NumberColumn(format="%.4f"),
                "涨跌幅": st.column_config.NumberColumn(format="%+.2f%%"),
                "今日盈亏": st.column_config.TextColumn() if privacy_mode else st.column_config.NumberColumn(
                    format="%+.2f"),
                "持有市值": st.column_config.TextColumn() if privacy_mode else st.column_config.NumberColumn(
                    format="%.0f"),
            },
            use_container_width=True,
            hide_index=True
        )

# Tab 2: 分析
with tab_analysis:
    if fund_list:
        c1, c2 = st.columns(2)
        df_analysis = pd.DataFrame(fund_list)

        with c1:
            st.caption("资产分布")
            tag_group = df_analysis.groupby("标签")["持有市值"].sum().reset_index()
            import altair as alt

            chart = alt.Chart(tag_group).mark_arc(innerRadius=50).encode(
                theta=alt.Theta(field="持有市值", type="quantitative"),
                color=alt.Color(field="标签", type="nominal"),
                tooltip=["标签", "持有市值"]
            )
            st.altair_chart(chart, use_container_width=True)

        with c2:
            st.caption("今日贡献 Top 5")
            df_analysis['盈亏绝对值'] = df_analysis['今日盈亏'].abs()
            top5 = df_analysis.sort_values('盈亏绝对值', ascending=False).head(5)
            st.bar_chart(top5.set_index("基金名称")["今日盈亏"], color="#d62728")

# Tab 3: 🌟 历史走势 (新功能)
with tab_history:
    st.subheader("🔎 基金净值走势查看")

    if fund_list:
        # 1. 构造选择器选项： "名称 (代码)"
        options = [f"{f['基金名称']} ({f['代码']})" for f in fund_list]
        selected_option = st.selectbox("选择要查看的基金", options)

        # 2. 提取选中的代码
        selected_code = re.search(r'\((.*?)\)', selected_option).group(1)

        # 3. 过滤器：时间范围
        time_range = st.radio("时间范围", ["近1月", "近3月", "近6月", "近1年", "今年以来", "历史全量"], horizontal=True,
                              index=3)

        # 4. 获取并绘图
        with st.spinner(f"正在加载 {selected_code} 的历史数据..."):
            hist_df = get_fund_history(selected_code)

            if hist_df is not None and not hist_df.empty:
                # 根据时间过滤
                if time_range == "近1月":
                    plot_df = hist_df.tail(22)
                elif time_range == "近3月":
                    plot_df = hist_df.tail(66)
                elif time_range == "近6月":
                    plot_df = hist_df.tail(130)
                elif time_range == "近1年":
                    plot_df = hist_df.tail(252)
                elif time_range == "今年以来":
                    current_year = datetime.datetime.now().year
                    plot_df = hist_df[hist_df.index.year == current_year]
                else:
                    plot_df = hist_df  # 全量

                # 画图
                st.line_chart(plot_df, color="#d62728")

                # 显示最高最低统计
                min_val = plot_df['净值'].min()
                max_val = plot_df['净值'].max()
                curr_val = plot_df['净值'].iloc[-1]

                c1, c2, c3 = st.columns(3)
                c1.metric("区间最低", f"{min_val:.4f}")
                c2.metric("区间最高", f"{max_val:.4f}")
                c3.metric("最新净值", f"{curr_val:.4f}")

            else:
                st.warning("暂未获取到历史数据（可能是新发基金或网络原因）")
    else:
        st.info("请先添加持仓基金")

if auto_refresh:
    time.sleep(60)
    st.rerun()