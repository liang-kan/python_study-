import matplotlib.pyplot as plt
import matplotlib.patches as patches
from datetime import datetime, timedelta
import matplotlib.font_manager as fm
import platform


# --- 1. 字体设置 (保持不变) ---
def set_chinese_font():
    system = platform.system()
    font_path = None
    if system == "Windows":
        font_paths = ["C:/Windows/Fonts/msyh.ttf", "C:/Windows/Fonts/simhei.ttf"]
    elif system == "Darwin":
        font_paths = ["/System/Library/Fonts/PingFang.ttc", "/Library/Fonts/Arial Unicode.ttf"]
    else:
        font_paths = ["/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"]

    for path in font_paths:
        try:
            open(path, 'r')
            return fm.FontProperties(fname=path)
        except:
            continue
    return fm.FontProperties()


zh_font = set_chinese_font()
zh_font_bold = zh_font.copy()
zh_font_bold.set_weight('bold')


# --- 2. 核心绘图逻辑 ---

def draw_network_chart_with_data(start_date_str="2025-12-18", periods=16):
    # --- 配置参数 ---
    line_color = '#004d60'
    task_color = 'black'  # 任务线颜色
    text_color = 'black'

    # 行高配置
    row_heights = {
        'week_num': 1.2, 'weekday': 1.2,
        'drawing_area': 10.0,  # 稍微加高一点绘图区以便放下更多任务
        'day': 1.2, 'month': 1.2, 'ruler': 1.2
    }

    # 计算Y轴布局
    y_cursor = 0
    y_ranges = {}
    order = ['week_num', 'weekday', 'drawing_area', 'day', 'month', 'ruler']
    for key in order:
        h = row_heights[key]
        y_ranges[key] = (y_cursor, y_cursor + h)
        y_cursor += h

    total_height = y_cursor
    header_width = 3.5
    col_width = 1.5

    # 标尺单位换算: 假设 1 col_width = 10 标尺单位 (例如天数)
    # 则 X坐标 = header_width + (val / 10) * col_width
    def val_to_x(val):
        return header_width + (val / 10.0) * col_width

    # 绘图区内部 Y 坐标映射 (将绘图区分为 num_rows 层)
    draw_y_bottom, draw_y_top = y_ranges['drawing_area']
    draw_height = draw_y_top - draw_y_bottom

    def get_task_y(row_idx, total_rows=8):
        # row_idx: 从下往上数，0是主要路径
        # 为了美观，留出上下边距
        margin = 1.0
        available_h = draw_height - 2 * margin
        step = available_h / (total_rows - 1)
        return draw_y_bottom + margin + row_idx * step

    # --- 初始化画布 ---
    fig, ax = plt.subplots(figsize=(16, 10), dpi=120)
    ax.set_xlim(0, header_width + periods * col_width)
    ax.set_ylim(0, total_height)
    ax.axis('off')

    # 辅助绘图函数
    def draw_rect(x, y, w, h, color=line_color, lw=1.0, ls='-'):
        rect = patches.Rectangle((x, y), w, h, linewidth=lw, edgecolor=color, facecolor='none', linestyle=ls)
        ax.add_patch(rect)

    def draw_text(x, y, text, font=zh_font, size=10, ha='center', va='center', color=text_color, bg=None):
        t = ax.text(x, y, text, color=color, fontproperties=font, fontsize=size, ha=ha, va=va)
        if bg: t.set_bbox(dict(facecolor=bg, alpha=0.7, edgecolor='none', pad=1))

    # ==========================================
    # PART 1: 绘制背景网格 (简化版，逻辑同上一个脚本)
    # ==========================================

    # 1.1 标题栏
    headers = {'week_num': "工程周", 'weekday': "星期", 'day': "日", 'month': "月", 'ruler': "工程标尺"}
    for key, label in headers.items():
        yb, yt = y_ranges[key]
        draw_rect(0, yb, header_width, yt - yb)
        draw_text(header_width / 2, (yb + yt) / 2, label, font=zh_font_bold, size=12)

    # 1.2 时间轴循环
    curr_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    months = []
    month_start_x = header_width
    curr_m_str = f"{curr_date.year}.{curr_date.month}"

    for i in range(periods):
        x = header_width + i * col_width

        # 日 & 星期
        yb_d, yt_d = y_ranges['day']
        draw_rect(x, yb_d, col_width, yt_d - yb_d, lw=0.5)
        draw_text(x + col_width / 2, (yb_d + yt_d) / 2, str(curr_date.day))

        yb_w, yt_w = y_ranges['weekday']
        wk_str = ["一", "二", "三", "四", "五", "六", "日"][curr_date.weekday()]
        draw_rect(x, yb_w, col_width, yt_w - yb_w, lw=0.5)
        draw_text(x + col_width / 2, (yb_w + yt_w) / 2, wk_str)

        # 工程周 (每2格=1周)
        if i % 2 == 0:
            yb_wk, yt_wk = y_ranges['week_num']
            draw_rect(x, yb_wk, col_width * 2, yt_wk - yb_wk, lw=0.5)
            draw_text(x + col_width, (yb_wk + yt_wk) / 2, str(i // 2 + 1))

        # 标尺刻度 (每格画线)
        yb_r, yt_r = y_ranges['ruler']
        plt.plot([x, x], [yb_r, yb_r + 0.4], color=line_color, lw=0.8)  # 大刻度
        # 标尺数值
        draw_text(x, yb_r + 0.7, str(i * 10), size=9)  # 假设1格=10单位
        # 子刻度
        for sub in range(1, 5):
            xs = x + sub * (col_width / 5)
            plt.plot([xs, xs], [yb_r, yb_r + 0.2], color=line_color, lw=0.5)

        # 月份处理
        next_date = curr_date + timedelta(days=3)
        next_m_str = f"{next_date.year}.{next_date.month}"
        if next_m_str != curr_m_str or i == periods - 1:
            w = (x + col_width) - month_start_x
            months.append((curr_m_str, month_start_x, w))
            # 画跨越绘图区的虚线
            if i != periods - 1:
                plt.plot([x + col_width, x + col_width], [draw_y_bottom, draw_y_top],
                         ls='--', color='gray', lw=0.8, alpha=0.5)
            month_start_x = x + col_width
            curr_m_str = next_m_str

        curr_date = next_date

    # 1.3 绘制合并后的月份
    yb_m, yt_m = y_ranges['month']
    for m_txt, mx, mw in months:
        draw_rect(mx, yb_m, mw, yt_m - yb_m)
        draw_text(mx + mw / 2, (yb_m + yt_m) / 2, m_txt, font=zh_font_bold)

    # 1.4 绘图区外框
    draw_rect(header_width, draw_y_bottom, periods * col_width, draw_height, lw=1.5)

    # 标尺区外框
    yb_r, yt_r = y_ranges['ruler']
    draw_rect(header_width, yb_r, periods * col_width, yt_r - yb_r)

    # ==========================================
    # PART 2: 绘制内置测试数据 (Tasks)
    # ==========================================

    # --- 测试数据定义 ---
    # 格式: (任务名称, 开始值, 持续值, 行索引[0-5], 节点编号[始, 终])
    # 注意：这里的数值对应标尺上的数值 (例如 0-10 是第一格)
    tasks = [
        # (Name, Start, Duration, Row_Index, Nodes)
        ("进场准备", 0, 10, 3, (1, 2)),
        ("场地平整", 10, 15, 3, (2, 3)),
        ("测量放线", 25, 5, 3, (3, 4)),

        # 分支任务
        ("临时设施搭建", 10, 20, 5, (2, 5)),  # 并行任务
        ("材料采购", 10, 30, 1, (2, 6)),  # 并行任务

        # 汇聚
        ("土方开挖", 30, 20, 3, (4, 7)),

        # 下一阶段
        ("边坡支护", 50, 30, 4, (7, 8)),
        ("基础垫层", 50, 20, 2, (7, 9)),

        ("基础钢筋", 70, 20, 2, (9, 10)),
        ("基础浇筑", 90, 30, 2, (10, 11)),
    ]

    # 虚工作/依赖关系 (Start_Node_Pos, End_Node_Pos)
    # 我们需要先计算出每个节点的位置才能画虚线
    # 这里为了简单，手动定义虚线的坐标逻辑: (start_val, row_start, row_end)
    dummy_links = [
        (30, 5, 3),  # 临时设施 -> 土方开挖前 (模拟逻辑)
        (40, 1, 3),  # 材料采购 -> 土方开挖 (模拟逻辑，假设有延迟)
        (80, 4, 2),  # 边坡 -> 基础某阶段
    ]

    # --- 绘图函数 ---

    # 1. 画节点 (Circle)
    def draw_node(val, row_idx, node_num):
        cx, cy = val_to_x(val), get_task_y(row_idx)
        # 圆圈
        circle = patches.Circle((cx, cy), 0.3, facecolor='white', edgecolor='black', zorder=10)
        ax.add_patch(circle)
        # 节点编号
        draw_text(cx, cy, str(node_num), size=9, font=zh_font)
        return cx, cy

    # 2. 画实任务 (Arrow/Line)
    for name, start, dur, row, nodes in tasks:
        end = start + dur
        y = get_task_y(row)
        x_start = val_to_x(start)
        x_end = val_to_x(end)

        # 画线 (实线箭头)
        # 使用 annotate 画带箭头的线，比 arrow 更平滑
        ax.annotate("", xy=(x_end, y), xytext=(x_start, y),
                    arrowprops=dict(arrowstyle="->", lw=2, color=task_color))

        # 任务名称 (在线上方)
        draw_text((x_start + x_end) / 2, y + 0.35, name, size=10, bg='white')

        # 持续时间 (在线下方)
        draw_text((x_start + x_end) / 2, y - 0.35, f"{dur}d", size=9, color='gray')

        # 画节点
        draw_node(start, row, nodes[0])
        draw_node(end, row, nodes[1])

    # 3. 画虚工作 (Dummy/Links) - 垂直虚线箭头
    for val, r_start, r_end in dummy_links:
        x = val_to_x(val)
        y1 = get_task_y(r_start)
        y2 = get_task_y(r_end)

        # 稍微偏移一点以免遮挡节点文字
        ax.annotate("", xy=(x, y2), xytext=(x, y1),
                    arrowprops=dict(arrowstyle="->", lw=1, color='red', linestyle='--'))

    # --- 收尾 ---
    plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    filename = 'network_chart_with_data.png'
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"带数据的网络图已生成: {filename}")
    plt.show()


if __name__ == "__main__":
    # 模拟数据范围：0 - 160 (约16列)
    draw_network_chart_with_data(start_date_str="2025-12-18", periods=16)