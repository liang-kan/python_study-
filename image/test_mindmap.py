import sys
import os
import re
import uuid
from io import BytesIO
from typing import List, Dict, Tuple, Optional

# 尝试导入 graphviz，如果没有安装给出友好提示
try:
    import graphviz
except ImportError:
    print("错误: 未找到 graphviz Python 库。")
    print("请运行: pip install graphviz")
    sys.exit(1)


# ================= 核心服务类 (MindmapService) =================

class MindmapTheme:
    """定义配色主题"""
    SKY_BLUE = {
        "root_fill": "#009CE0", "root_font": "#FFFFFF", "root_border": "#007bb3",
        "branch_fill": "#E0F7FA", "branch_font": "#006064", "branch_border": "#B2EBF2",
        "leaf_fill": "#FFFFFF", "leaf_font": "#37474F", "leaf_border": "#CFD8DC",
        "edge_color": "#78909C"
    }


class MindmapGeneratorService:
    def __init__(self):
        # 根据操作系统自动选择合适的中文字体，防止中文乱码
        if sys.platform.startswith('win'):
            self.default_font = "Microsoft YaHei"
        elif sys.platform.startswith('darwin'):
            self.default_font = "PingFang SC"
        else:
            self.default_font = "WenQuanYi Micro Hei"  # Linux 常见字体

    def generate_mindmap_png_stream(self, text: str, theme: Dict = MindmapTheme.SKY_BLUE) -> BytesIO:
        """
        生成思维导图 PNG 流
        """
        # 1. 初始化 Graphviz 对象
        dot = graphviz.Digraph(comment='Mindmap', format='png', engine='dot')

        # 布局设置
        dot.attr(rankdir='LR')  # 从左到右布局
        dot.attr(splines='curved')  # 使用平滑曲线
        dot.attr(nodesep='0.2')  # 节点垂直间距
        dot.attr(ranksep='0.5')  # 层级水平间距
        dot.attr(bgcolor='transparent')

        # 全局样式
        dot.attr('node', shape='rect', style='filled,rounded', fontname=self.default_font, margin='0.15,0.1')
        dot.attr('edge', arrowsize='0.5', color=theme['edge_color'], dir='none')

        # 2. 解析文本
        nodes, edges = self._parse_text(text)

        # 3. 添加节点
        for node_id, data in nodes.items():
            level = data['level']
            label = data['label']

            if level == 0:
                dot.node(node_id, label, fontsize='20', height='0.6',
                         fillcolor=theme['root_fill'], fontcolor=theme['root_font'], color=theme['root_border'],
                         penwidth='2.0')
            elif level == 1:
                dot.node(node_id, label, fontsize='15', height='0.5',
                         fillcolor=theme['branch_fill'], fontcolor=theme['branch_font'], color=theme['branch_border'],
                         penwidth='1.5')
            else:
                dot.node(node_id, label, fontsize='12', height='0.4',
                         fillcolor=theme['leaf_fill'], fontcolor=theme['leaf_font'], color=theme['leaf_border'],
                         penwidth='1.0')

        # 4. 添加连线
        for parent_id, child_id in edges:
            dot.edge(parent_id, child_id, penwidth='1.2')

        # 5. 渲染
        try:
            return BytesIO(dot.pipe())
        except graphviz.backend.ExecutableNotFound:
            raise RuntimeError("系统未找到 Graphviz 可执行文件 (dot)。请安装 Graphviz 软件并添加到 PATH 环境变量。")

    def _parse_text(self, text: str) -> Tuple[Dict, List[Tuple]]:
        lines = text.splitlines()
        nodes = {}
        edges = []
        stack = []  # [(indent, uuid)]

        root_processed = False

        for line in lines:
            stripped = line.strip()
            if not stripped: continue

            # Root
            if stripped.startswith('#'):
                label = re.sub(r'^#+\s*', '', stripped).strip()
                node_id = self._generate_id()
                nodes[node_id] = {'label': label, 'level': 0}
                stack = [(-1, node_id)]
                root_processed = True
                continue

            if not root_processed: continue

            # Children
            expanded = line.replace('\t', '    ')
            indent = len(expanded) - len(expanded.lstrip())

            content = expanded.strip()
            if content.startswith(('-', '*')):
                content = content[1:].strip()

            node_id = self._generate_id()

            # 找爸爸
            while stack and stack[-1][0] >= indent:
                stack.pop()

            if stack:
                parent_id = stack[-1][1]
                parent_level = nodes[parent_id]['level']
                nodes[node_id] = {'label': content, 'level': parent_level + 1}
                edges.append((parent_id, node_id))
                stack.append((indent, node_id))

        return nodes, edges

    def _generate_id(self):
        return str(uuid.uuid4()).replace('-', '')


# ================= 测试运行入口 =================

if __name__ == "__main__":
    # 1. 准备测试数据 (Markdown 格式)
    test_text = """
# 芋道源码架构重构
- 基础设施
    * MySQL (主从)
    * Redis (集群)
    * RocketMQ
- 后端服务 (Spring Boot)
    * 系统模块
        - 用户管理
        - 角色权限
        - 部门管理
    * 业务模块
        - 订单系统
        - 支付网关
            * 微信支付
            * 支付宝
- 前端应用
    * 管理后台 (Vue3)
    * 移动端 (UniApp)
"""

    print("正在生成思维导图...")
    service = MindmapGeneratorService()
    output_filename = "result_mindmap.png"

    try:
        # 2. 调用生成服务
        png_stream = service.generate_mindmap_png_stream(test_text, theme=MindmapTheme.SKY_BLUE)

        # 3. 保存文件
        with open(output_filename, "wb") as f:
            f.write(png_stream.getvalue())

        print(f"✅ 成功！文件已保存至: {os.path.abspath(output_filename)}")

        # 4. 尝试自动打开图片 (仅限 Windows/Mac)
        if sys.platform.startswith('win'):
            os.startfile(output_filename)
        elif sys.platform.startswith('darwin'):
            os.system(f"open {output_filename}")

    except RuntimeError as e:
        print(f"❌ 运行错误: {e}")
    except Exception as e:
        print(f"❌ 未知错误: {e}")