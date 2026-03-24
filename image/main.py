import sys
import uuid
import re
from io import BytesIO
from typing import List, Dict, Tuple, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
import graphviz


# ================= 1. 核心业务逻辑 (复用之前的代码) =================
class MindmapTheme:
    # 预定义主题配置
    THEMES = {
        "SKY_BLUE": {
            "root_fill": "#009CE0", "root_font": "#FFFFFF", "root_border": "#007bb3",
            "branch_fill": "#E0F7FA", "branch_font": "#006064", "branch_border": "#B2EBF2",
            "leaf_fill": "#FFFFFF", "leaf_font": "#37474F", "leaf_border": "#CFD8DC",
            "edge_color": "#78909C"
        },
        "DARK": {
            "root_fill": "#424242", "root_font": "#FFFFFF", "root_border": "#212121",
            "branch_fill": "#757575", "branch_font": "#FFFFFF", "branch_border": "#616161",
            "leaf_fill": "#BDBDBD", "leaf_font": "#212121", "leaf_border": "#9E9E9E",
            "edge_color": "#E0E0E0"
        }
    }


class MindmapGeneratorService:
    def __init__(self):
        # 简单适配字体
        if sys.platform.startswith('win'):
            self.default_font = "Microsoft YaHei"
        elif sys.platform.startswith('darwin'):
            self.default_font = "PingFang SC"
        else:
            self.default_font = "WenQuanYi Micro Hei"

    def generate(self, text: str, theme_name: str = "SKY_BLUE", font_family: str = None) -> bytes:
        # 获取主题配置，默认 SKY_BLUE
        theme = MindmapTheme.THEMES.get(theme_name, MindmapTheme.THEMES["SKY_BLUE"])
        font = font_family if font_family else self.default_font

        dot = graphviz.Digraph(comment='Mindmap', format='png', engine='dot')
        dot.attr(rankdir='LR', splines='curved', nodesep='0.2', ranksep='0.5', bgcolor='transparent')
        dot.attr('node', shape='rect', style='filled,rounded', fontname=font, margin='0.15,0.1')
        dot.attr('edge', arrowsize='0.5', color=theme['edge_color'], dir='none')

        nodes, edges = self._parse_text(text)

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

        for parent_id, child_id in edges:
            dot.edge(parent_id, child_id, penwidth='1.2')

        try:
            return dot.pipe()
        except graphviz.backend.ExecutableNotFound:
            raise RuntimeError("Graphviz executable not found on server path.")

    def _parse_text(self, text: str) -> Tuple[Dict, List[Tuple]]:
        lines = text.splitlines()
        nodes = {}
        edges = []
        stack = []
        root_processed = False

        # 简单的 ID 生成器
        def gen_id():
            return str(uuid.uuid4()).replace('-', '')

        for line in lines:
            stripped = line.strip()
            if not stripped: continue

            if stripped.startswith('#'):
                label = re.sub(r'^#+\s*', '', stripped).strip()
                node_id = gen_id()
                nodes[node_id] = {'label': label, 'level': 0}
                stack = [(-1, node_id)]
                root_processed = True
                continue

            if not root_processed: continue

            expanded = line.replace('\t', '    ')
            indent = len(expanded) - len(expanded.lstrip())
            content = expanded.strip()
            if content.startswith(('-', '*')):
                content = content[1:].strip()

            node_id = gen_id()
            while stack and stack[-1][0] >= indent:
                stack.pop()

            if stack:
                parent_id = stack[-1][1]
                parent_level = nodes[parent_id]['level']
                nodes[node_id] = {'label': content, 'level': parent_level + 1}
                edges.append((parent_id, node_id))
                stack.append((indent, node_id))
        return nodes, edges


# ================= 3. 流程图核心逻辑 (Flowchart) =================

class FlowchartTheme:
    # 定义流程图主题
    THEMES = {
        "WHITE_BLACK": {
            "node_fill": "#FFFFFF", "node_border": "#333333", "node_font": "#333333",
            "edge_color": "#333333", "font_name": "Microsoft YaHei"
        },
        "COLORFUL": {
            "node_fill": "#E3F2FD", "node_border": "#2196F3", "node_font": "#0D47A1",
            "decision_fill": "#FFF3E0", "decision_border": "#FF9800",
            "edge_color": "#607D8B", "font_name": "Microsoft YaHei"
        }
    }


class FlowchartService:
    def __init__(self):
        # 字体适配
        if sys.platform.startswith('win'):
            self.default_font = "Microsoft YaHei"
        elif sys.platform.startswith('darwin'):
            self.default_font = "PingFang SC"
        else:
            self.default_font = "WenQuanYi Micro Hei"

    def generate(self, mermaid_text: str, theme_name: str = "COLORFUL", font_family: str = None) -> bytes:
        theme = FlowchartTheme.THEMES.get(theme_name, FlowchartTheme.THEMES["COLORFUL"])
        font = font_family if font_family else self.default_font

        # 1. 解析
        spec = self._parse_mermaid(mermaid_text)

        # 2. 初始化 Graphviz
        dot = graphviz.Digraph(comment='Flowchart', format='png', engine='dot')

        # === 核心布局优化 ===
        # splines='ortho': 折线
        # nodesep='0.8': 增加水平间距，防止线条穿过节点
        # ranksep='0.6': 垂直间距
        # concentrate='true': 自动合并重叠的连线，减少混乱
        # newrank='true': 更好的层级对齐算法
        dot.attr(rankdir=spec['direction'], splines='ortho',
                 nodesep='0.8', ranksep='0.6',
                 concentrate='true', newrank='true',
                 bgcolor='transparent', dpi='150')

        # 全局字体
        dot.attr('node', fontname=font, fontsize='12')
        dot.attr('edge', fontname=font, fontsize='10', color=theme['edge_color'], arrowsize='0.7')

        # 3. 添加节点（强制统一宽度）
        for node_id, node_data in spec['nodes'].items():
            raw_label = node_data['label']
            shape_type = node_data['shape']

            # 1. 智能换行
            # 矩形每行约 10 个字，菱形每行约 8 个字
            wrap_width = 14 if shape_type == 'diamond' else 18
            wrapped_label, line_count = self._smart_wrap_html(raw_label, max_width=wrap_width)

            # 2. 样式定义
            fill = theme.get('node_fill', '#FFFFFF')
            border = theme.get('node_border', '#000000')
            font_color = theme.get('node_font', '#000000')

            attrs = {
                'style': 'filled',
                'fillcolor': fill,
                'color': border,
                'fontcolor': font_color,
                'margin': '0'  # 这里的 margin 设为 0，因为我们用 HTML cellpadding 控制
            }

            # === 3. 形状与尺寸控制 (关键优化) ===
            # width 是英寸，1 inch ≈ 96px
            # 强制所有节点拥有相同的最小宽度，保证垂直线对齐

            if shape_type == 'diamond':
                attrs['shape'] = 'diamond'
                attrs['width'] = '3'  # 菱形需要更宽才能包住文字
                attrs['height'] = '1.5'
                attrs['fixedsize'] = 'false'  # 允许根据内容撑大，但有基础宽度
                attrs['fillcolor'] = theme.get('decision_fill', '#FFF3E0')
                attrs['color'] = theme.get('decision_border', '#FF9800')

            elif shape_type == 'round_rect':
                attrs['shape'] = 'rect'
                attrs['style'] = 'filled,rounded'
                attrs['width'] = '2.5'  # 统一宽度
                attrs['fixedsize'] = 'false'

            else:  # 普通矩形
                attrs['shape'] = 'rect'
                attrs['style'] = 'filled'  # 直角矩形最整齐
                attrs['width'] = '2.5'  # 统一宽度 2.5英寸 ≈ 240px
                attrs['fixedsize'] = 'false'

            dot.node(node_id, label=wrapped_label, **attrs)

        # 4. 添加连线
        for edge in spec['edges']:
            src, dst, text = edge
            attrs = {}
            if text:
                attrs['xlabel'] = f" {text} "  # 使用 xlabel 而不是 label，让文字浮在旁边而不是切断线条
                attrs['decorate'] = 'false'
                attrs['fontcolor'] = theme['edge_color']

            dot.edge(src, dst, **attrs)

        try:
            # 移除 unflatten，保证对齐
            return dot.pipe()
        except graphviz.backend.ExecutableNotFound:
            raise RuntimeError("Graphviz executable not found.")

    def _smart_wrap_html(self, text: str, max_width: int) -> Tuple[str, int]:
        """
        生成 HTML 标签，返回 (HTML字符串, 行数)
        """
        lines = []
        current_line = ""
        current_len = 0

        for char in text:
            char_len = 2 if '\u4e00' <= char <= '\u9fff' else 1
            if current_len + char_len > max_width:
                lines.append(current_line)
                current_line = char
                current_len = char_len
            else:
                current_line += char
                current_len += char_len
        if current_line:
            lines.append(current_line)

        rows = "<BR/>".join(lines)
        # 适当增加 cellpadding 让文字呼吸
        html = f'<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="8"><TR><TD ALIGN="CENTER" BALIGN="MIDDLE">{rows}</TD></TR></TABLE>>'
        return html, len(lines)

    def _parse_mermaid(self, text: str) -> Dict:
        # (保持不变)
        lines = text.splitlines()
        direction = "TB"
        nodes = {}
        edges = []
        re_dir = re.compile(r'^\s*(?:graph|flowchart)\s+(TB|TD|BT|RL|LR)', re.IGNORECASE)
        for line in lines:
            line = line.strip()
            if not line: continue
            if line.startswith('```'): continue
            dir_match = re_dir.match(line)
            if dir_match:
                d = dir_match.group(1).upper()
                direction = "TB" if d == "TD" else d
                continue
            if '-->' in line:
                parts = line.split('-->')
                if len(parts) != 2: continue
                left_raw = parts[0].strip()
                right_raw = parts[1].strip()
                edge_label = None
                if ' -- ' in left_raw:
                    left_split = left_raw.rsplit(' -- ', 1)
                    left_raw = left_split[0].strip()
                    edge_label = left_split[1].strip()
                elif right_raw.startswith('|'):
                    end_bar = right_raw.find('|', 1)
                    if end_bar > 0:
                        edge_label = right_raw[1:end_bar].strip()
                        right_raw = right_raw[end_bar + 1:].strip()
                src_id = self._extract_node(left_raw, nodes)
                dst_id = self._extract_node(right_raw, nodes)
                edges.append((src_id, dst_id, edge_label))
            else:
                self._extract_node(line, nodes)
        return {"direction": direction, "nodes": nodes, "edges": edges}

    def _extract_node(self, text: str, nodes_dict: Dict) -> str:
        # (保持不变)
        text = text.strip()
        match = re.match(r'([a-zA-Z0-9_]+)\s*([\[\{\(])(.*?)([\]\}\)])', text)
        if match:
            node_id = match.group(1)
            shape_char = match.group(2)
            label = match.group(3)
            shape = 'rect'
            if shape_char == '{':
                shape = 'diamond'
            elif shape_char == '(':
                shape = 'round_rect'
            label = label.strip('"\'')
            nodes_dict[node_id] = {'label': label, 'shape': shape}
            return node_id
        else:
            node_id = text.split(' ')[0]
            if node_id not in nodes_dict:
                nodes_dict[node_id] = {'label': node_id, 'shape': 'rect'}
            return node_id
# ================= 2. API 定义 =================

app = FastAPI(title="Mindmap Generation API")
service = MindmapGeneratorService()


# 定义请求体结构
class GenerateRequest(BaseModel):
    text: str
    theme: Optional[str] = "SKY_BLUE"
    fontFamily: Optional[str] = None


@app.post("/api/mindmap/generate")
async def generate_mindmap(req: GenerateRequest):
    try:
        # 调用核心逻辑
        png_bytes = service.generate(req.text, req.theme, req.fontFamily)

        # 直接返回图片流
        return Response(content=png_bytes, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class FlowchartRequest(BaseModel):
    text: str
    theme: Optional[str] = "COLORFUL"
    fontFamily: Optional[str] = None

flowchart_service = FlowchartService()
@app.post("/api/flowchart/generate")
async def generate_flowchart(req: FlowchartRequest):
    try:
        png_bytes = flowchart_service.generate(req.text, req.theme, req.fontFamily)
        return Response(content=png_bytes, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
if __name__ == "__main__":
    import uvicorn

    # 启动服务在 8000 端口
    uvicorn.run(app, host="0.0.0.0", port=8001)