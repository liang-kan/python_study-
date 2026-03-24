"""
最小可执行方案：工程网络图生成器
用法：
  python network_diagram.py                          # 使用内置示例数据
  python network_diagram.py input.json output.png    # 自定义数据
"""

import json
import sys
import os
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from collections import defaultdict


# ==============================
# 1. CPM 关键路径计算
# ==============================
def calculate_cpm(activities):
    act_map = {a['id']: a for a in activities}

    # 构建后继表 + 入度
    successors = defaultdict(list)
    in_degree = {a['id']: 0 for a in activities}
    for a in activities:
        for p in (a.get('predecessors') or []):
            successors[p].append(a['id'])
            in_degree[a['id']] += 1

    # 拓扑排序 (Kahn)
    queue = [aid for aid, deg in in_degree.items() if deg == 0]
    order = []
    while queue:
        n = queue.pop(0)
        order.append(n)
        for s in successors[n]:
            in_degree[s] -= 1
            if in_degree[s] == 0:
                queue.append(s)

    # 前向传递
    for aid in order:
        a = act_map[aid]
        preds = a.get('predecessors') or []
        es = max((act_map[p]['ef'] for p in preds), default=0)
        a['es'] = es
        a['ef'] = es + a['duration']

    project_duration = max(a['ef'] for a in activities)

    # 后向传递
    for aid in reversed(order):
        a = act_map[aid]
        succs = successors[aid]
        a['lf'] = min((act_map[s]['ls'] for s in succs), default=project_duration)
        a['ls'] = a['lf'] - a['duration']
        a['tf'] = a['ls'] - a['es']
        a['critical'] = (a['tf'] == 0)

    return activities, project_duration


# ==============================
# 2. 网络图绘制
# ==============================
def draw_network(activities, project_duration, output_path):
    act_map = {a['id']: a for a in activities}

    # 构建 networkx 有向图
    G = nx.DiGraph()
    for a in activities:
        G.add_node(a['id'])
        for p in (a.get('predecessors') or []):
            G.add_edge(p, a['id'])

    # ---------- 分层布局（按 ES 分组） ----------
    layers = defaultdict(list)
    for a in activities:
        layers[a['es']].append(a['id'])

    sorted_keys = sorted(layers.keys())
    num_layers = len(sorted_keys)

    pos = {}
    for i, key in enumerate(sorted_keys):
        nodes = layers[key]
        x = i * 3  # 水平间距
        n = len(nodes)
        for j, nid in enumerate(nodes):
            y = (n - 1) / 2.0 - j  # 垂直居中
            pos[nid] = (x, y * 2.5)

    # ---------- 画图 ----------
    fig, ax = plt.subplots(figsize=(max(14, num_layers * 3.5), max(8, len(activities) * 1.2)))
    fig.patch.set_facecolor('#FAFBFC')
    ax.set_facecolor('#FAFBFC')

    # 画边
    for u, v in G.edges():
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        is_crit = act_map[u]['critical'] and act_map[v]['critical']
        color = '#E74C3C' if is_crit else '#B0B0B0'
        lw = 2.5 if is_crit else 1.2
        ls = '-' if is_crit else '--'

        ax.annotate('',
                    xy=(x1 - 0.6, y1), xytext=(x0 + 0.6, y0),
                    arrowprops=dict(arrowstyle='-|>', color=color,
                                    lw=lw, linestyle=ls,
                                    connectionstyle='arc3,rad=0.15',
                                    mutation_scale=18))

    # 画节点
    box_w, box_h = 1.2, 1.6
    for a in activities:
        x, y = pos[a['id']]
        fc = '#E74C3C' if a['critical'] else '#3498DB'
        ec = '#C0392B' if a['critical'] else '#2471A3'

        rect = mpatches.FancyBboxPatch(
            (x - box_w / 2, y - box_h / 2), box_w, box_h,
            boxstyle="round,pad=0.1",
            facecolor=fc, edgecolor=ec, linewidth=2, alpha=0.92)
        ax.add_patch(rect)

        # 节点文本
        lines = [
            f"{a['id']}: {a['name']}",
            f"Dur={a['duration']}",
            f"ES={a['es']}  EF={a['ef']}",
            f"LS={a['ls']}  LF={a['lf']}",
            f"TF={a['tf']}"
        ]
        text = '\n'.join(lines)
        ax.text(x, y, text, ha='center', va='center',
                fontsize=8, color='white',
                fontweight='bold' if a['critical'] else 'normal',
                linespacing=1.4)

    # 标题
    crit_ids = [a['id'] for a in activities if a['critical']]
    ax.set_title(
        f"Engineering Network Diagram  |  Project Duration = {project_duration} days\n"
        f"Critical Path: {' → '.join(crit_ids)}",
        fontsize=15, fontweight='bold', color='#2C3E50', pad=18)

    # 图例
    legend_handles = [
        mpatches.Patch(color='#E74C3C', label='Critical Activity'),
        mpatches.Patch(color='#3498DB', label='Non-Critical Activity'),
    ]
    ax.legend(handles=legend_handles, loc='lower right',
              fontsize=10, framealpha=0.9, edgecolor='#ccc')

    # 隐藏坐标轴，留边距
    ax.set_xlim(min(x for x, y in pos.values()) - 1.5,
                max(x for x, y in pos.values()) + 1.5)
    ax.set_ylim(min(y for x, y in pos.values()) - 1.8,
                max(y for x, y in pos.values()) + 1.8)
    ax.axis('off')

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close()
    print(f"[OK] 图片已保存: {output_path}")


# ==============================
# 3. 内置示例数据
# ==============================
DEMO_DATA = [
    {"id": "A", "name": "SitePrep",     "duration": 3, "predecessors": []},
    {"id": "B", "name": "Foundation",    "duration": 5, "predecessors": ["A"]},
    {"id": "C", "name": "Procurement",   "duration": 4, "predecessors": ["A"]},
    {"id": "D", "name": "Structure",     "duration": 8, "predecessors": ["B"]},
    {"id": "E", "name": "Installation",  "duration": 6, "predecessors": ["B", "C"]},
    {"id": "F", "name": "Decoration",    "duration": 4, "predecessors": ["D"]},
    {"id": "G", "name": "Commissioning", "duration": 3, "predecessors": ["E", "F"]},
]


# ==============================
# 4. 主函数
# ==============================
def main():
    if len(sys.argv) >= 3:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        with open(input_file, 'r', encoding='utf-8') as f:
            activities = json.load(f)
    else:
        activities = DEMO_DATA
        output_file = 'network_diagram.png'
        print("[INFO] 未指定参数，使用内置示例数据")

    # 计算
    activities, project_duration = calculate_cpm(activities)

    # 打印计算结果
    print(f"\n{'='*60}")
    print(f"  项目总工期: {project_duration} 天")
    print(f"{'='*60}")
    print(f"{'ID':<4} {'Name':<14} {'Dur':>4} {'ES':>4} {'EF':>4} {'LS':>4} {'LF':>4} {'TF':>4} {'Crit'}")
    print(f"{'-'*60}")
    for a in activities:
        mark = ' ★' if a['critical'] else ''
        print(f"{a['id']:<4} {a['name']:<14} {a['duration']:>4} "
              f"{a['es']:>4} {a['ef']:>4} {a['ls']:>4} {a['lf']:>4} {a['tf']:>4}{mark}")
    print(f"{'-'*60}")
    crit = [a['id'] for a in activities if a['critical']]
    print(f"  关键路径: {' → '.join(crit)}")
    print(f"{'='*60}\n")

    # 画图
    draw_network(activities, project_duration, output_file)

    # 输出JSON（供Java解析stdout）
    result = {
        "projectDuration": project_duration,
        "criticalPath": crit,
        "outputPath": os.path.abspath(output_file)
    }
    print("__JSON__" + json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()