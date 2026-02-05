import streamlit as st
import requests
import re
import pandas as pd
import time
import json
import os

# --- 1. 配置与常量 ---
DATA_FILE = "my_funds.json"
st.set_page_config(page_title="基金实盘助手 v3.0", layout="wide", page_icon="🦁")


# --- 2. 核心函数：数据存取与升级 ---
def load_holdings():
    """读取数据，并自动处理旧版本数据的兼容性"""
    df = pd.DataFrame()

    # 尝试读取本地文件
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                df = pd.DataFrame(json.load(f))
        except:
            pass

    # 如果文件不存在，或者读取为空，加载内置默认数据
    if df.empty:
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

    # --- 关键：数据结构清洗与补全 ---
    # 确保所有列都存在，防止旧文件没有“标签”列导致报错
    required_cols = {
        "基金代码": str,
        "持仓份额": float,
        "持仓成本": float,
        "标签": str
    }

    for col, dtype in required_cols.items():
        if col not in df.columns:
            # 如果缺列，给默认值
            default_val = "未分类" if dtype == str else 0.0
            df[col] = default_val
        # 强制转换类型
        df[col] = df[col].astype(dtype)

    return df


def save_holdings(df):
    df.to_json(DATA_FILE, orient="records", force_ascii=False)


# --- 3. 核心函数：网络请求 ---
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


# --- 4. 辅助函数：隐私打码 ---
def mask_number(value, is_hidden, fmt="{:,.2f}"):
    if is_hidden:
        return "****"
    return fmt.format(value)


# --- 5. 侧边栏：控制台 ---
with st.sidebar:
    st.title("🦁 基金实盘助手")

    # 隐私模式开关
    privacy_mode = st.toggle("🙈 隐私模式 (隐藏金额)", value=False)

    st.divider()
    st.subheader("💼 持仓管理")

    df_holdings = load_holdings()

    # 编辑器配置
    edited_df = st.data_editor(
        df_holdings,
        num_rows="dynamic",
        column_config={
            "基金代码": st.column_config.TextColumn(help="6位代码"),
            "持仓份额": st.column_config.NumberColumn(format="%.2f"),
            "持仓成本": st.column_config.NumberColumn(format="%.4f"),
            "标签": st.column_config.SelectboxColumn(
                help="用于资产分布分析",
                options=["美股", "黄金", "白酒", "科技", "医药", "债券", "宽基", "港股", "红利", "其他", "未分类"],
                required=True
            )
        },
        key="editor"
    )

    if not edited_df.equals(df_holdings):
        save_holdings(edited_df)
        st.toast("✅ 持仓已更新")
        time.sleep(0.5)
        st.rerun()

    st.divider()
    if st.button("🔄 刷新行情", type="primary"):
        st.rerun()

    auto_refresh = st.checkbox("60s 自动刷新")

# --- 6. 主逻辑计算 ---
if edited_df.empty:
    st.info("👈 请在左侧添加持仓数据")
    st.stop()

fund_list = []
total_daily_profit = 0
total_accum_profit = 0
total_asset = 0
failed_count = 0

# 进度条
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
    else:
        failed_count += 1

    bar.progress((index + 1) / len(edited_df))

bar.empty()

# --- 7. 数据可视化看板 ---

# (A) 核心指标卡片
k1, k2, k3, k4 = st.columns(4)

# 动态决定显示什么内容
display_asset = mask_number(total_asset, privacy_mode, "¥ {:,.0f}")
display_daily = mask_number(total_daily_profit, privacy_mode, "¥ {:+.2f}")
display_accum = mask_number(total_accum_profit, privacy_mode, "¥ {:+.0f}")

k1.metric("预估总资产", display_asset)

# 今日盈亏 (涨跌百分比始终显示，金额受隐私模式控制)
daily_pct = (total_daily_profit / total_asset * 100) if total_asset > 0 else 0
k2.metric("今日盈亏", display_daily, f"{daily_pct:+.2f}%", delta_color="inverse")

# 累计盈亏
k3.metric("累计盈亏", display_accum, help="需输入持仓成本", delta_color="inverse" if total_accum_profit != 0 else "off")

# 盈利家数
profit_num = len([x for x in fund_list if x['今日盈亏'] > 0])
k4.metric("红盘数量", f"{profit_num} / {len(fund_list)}")

st.divider()

# (B) 分页视图：列表 vs 分析
tab_list, tab_analysis = st.tabs(["📋 持仓明细", "📊 资产分析"])

with tab_list:
    if fund_list:
        df = pd.DataFrame(fund_list)
        df.sort_values(by="今日盈亏", ascending=False, inplace=True)

        # 准备展示的数据，处理隐私模式
        display_df = df.copy()
        if privacy_mode:
            # 如果开启隐私模式，把敏感列变成星号
            for col in ["持有市值", "今日盈亏", "累计盈亏", "持仓份额", "持仓成本"]:
                display_df[col] = "****"
        else:
            # 正常模式下的格式化
            pass  # Streamlit dataframe format 会处理


        # 样式配置
        def highlight(row):
            val = row['涨跌幅']  # 即使在隐私模式下，涨跌幅也是可见的
            color = '#d62728' if val > 0 else '#2ca02c' if val < 0 else ''
            return [f'color: {color}' for _ in row]


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
                "累计盈亏": st.column_config.TextColumn() if privacy_mode else st.column_config.NumberColumn(
                    format="%+.0f"),
            },
            use_container_width=True,
            hide_index=True,
            height=len(df) * 38 + 38
        )
    else:
        st.warning("暂无数据")

with tab_analysis:
    if fund_list:
        col_pie, col_bar = st.columns(2)

        df_analysis = pd.DataFrame(fund_list)

        # 1. 资产分布 (饼图)
        with col_pie:
            st.subheader("资产分布 (按标签)")
            # 按标签分组求和
            tag_group = df_analysis.groupby("标签")["持有市值"].sum().reset_index()

            # 使用 Streamlit 原生图表 (简单版)
            # 如果想更漂亮，可以用 plotly，但为了无需额外安装库，这里用 altair
            import altair as alt

            chart = alt.Chart(tag_group).mark_arc(innerRadius=50).encode(
                theta=alt.Theta(field="持有市值", type="quantitative"),
                color=alt.Color(field="标签", type="nominal"),
                tooltip=["标签", "持有市值"]
            )
            st.altair_chart(chart, use_container_width=True)

            # 这里的金额是否隐藏取决于隐私模式
            if not privacy_mode:
                st.dataframe(tag_group.sort_values("持有市值", ascending=False), hide_index=True)

        # 2. 盈亏贡献 (柱状图)
        with col_bar:
            st.subheader("今日贡献 Top 5")
            # 取绝对值最大的前5名
            df_analysis['盈亏绝对值'] = df_analysis['今日盈亏'].abs()
            top5 = df_analysis.sort_values('盈亏绝对值', ascending=False).head(5)

            st.bar_chart(
                top5.set_index("基金名称")["今日盈亏"],
                color="#d62728"  # 统一红色，反正负数会向下
            )
    else:
        st.info("暂无数据")

if failed_count > 0:
    st.error(f"有 {failed_count} 只基金数据获取失败。")

if auto_refresh:
    time.sleep(60)
    st.rerun()