# app.py
import streamlit as st
import graphviz
import pandas as pd # Matrix 시각화용

# --- Local Modules ---
import data_manager 
import functions 

# [Project Architecture Note]
# 이 파일(app.py)은 'Presentation Layer'입니다.
# 알고리즘의 핵심 로직(Backend)은 'functions.py'에서 수행되며,
# 이곳에서는 시각화 라이브러리(Streamlit, Graphviz) 호환성을 위해 
# 표준 자료구조(List, Dict, Set)를 사용하여 렌더링 성능을 최적화합니다.

# --- 1. Visualization Helper ---
def render_graph(nodes, edges, step_state, algo_type, is_directed):
    """
    Graphviz 렌더링: Directed 여부와 Edge Type 반영
    """
    # [핵심] 유향(Digraph) vs 무향(Graph) 선택
    if is_directed:
        dot = graphviz.Digraph(engine='neato')
    else:
        dot = graphviz.Graph(engine='neato')
    
    # 캔버스 사이즈 및 스타일 (6:4 비율에 최적화)
    dot.attr(size='5.5,4.5!', ratio='fill', bgcolor='transparent')
    dot.attr('node', shape='circle', style='filled', 
             fontname='Helvetica', fontsize='10', fixedsize='true', width='0.5')
    
    # 기본 엣지 스타일 (화살표 크기 등)
    dot.attr('edge', color='#BDC3C7', penwidth='1.2', arrowsize='0.6')

    # [Rendering Optimization]
    # 시각화 렌더링 시 O(1) 조회를 위해 Backend 데이터를 Set/Dict로 변환하여 사용
    visited_set = set(step_state.get("visited", []))
    current_node = step_state.get("current_node", None)
    active_edges = step_state.get("active_edges", [])
    edge_types = step_state.get("edge_types", {}) 
    
    levels = step_state.get("levels", {})
    depths = step_state.get("depths", {})
    in_structure = set(step_state.get("queue", []) + step_state.get("stack", []))

    # --- Node Rendering ---
    for node in nodes:
        fillcolor = "#FFFFFF"
        fontcolor = "#000000"
        penwidth = "1"
        color = "#7F8C8D"
        
        label_text = node
        # BFS Level / DFS Depth 표시
        if algo_type.startswith("BFS") and node in levels:
            label_text = f"{node}\nL{levels[node]}"
        elif algo_type.startswith("DFS") and node in depths:
            label_text = f"{node}\nD{depths[node]}"

        # 상태별 색상 적용
        if node in visited_set:
            fillcolor = "#D5F5E3" # 민트 (방문 완료)
            color = "#2ECC71"
        
        if node in in_structure:
            fillcolor = "#D6EAF8" # 파랑 (대기 중)
            color = "#3498DB"
            # BFS의 경우 큐에 있을 때도 레벨 표시
            if algo_type.startswith("BFS") and node in levels:
                label_text = f"{node}\nL{levels[node]}"
            
        if node == current_node:
            fillcolor = "#F9E79F" # 노랑 (현재 노드)
            color = "#F1C40F"
            penwidth = "2.5"

        dot.node(node, label=label_text, fillcolor=fillcolor, color=color, penwidth=penwidth, fontcolor=fontcolor)

    # --- Edge Rendering ---
    active_edge_set = set(active_edges)
    
    for u, v in edges:
        # 무향 그래프일 경우 (u, v)와 (v, u)를 동일하게 취급하기 위한 Key 정렬
        edge_key = tuple(sorted((u, v))) if not is_directed else (u, v)
        
        e_color = "#BDC3C7"
        e_style = "solid"
        e_penwidth = "1.2"
        
        # 1. 활성화된 엣지 (탐색 경로)
        if (u, v) in active_edge_set or (not is_directed and (v, u) in active_edge_set):
            e_color = "#E74C3C" 
            e_penwidth = "2.5"
        
        # 2. 알고리즘적 분류 (Tree, Back, Cross)
        elif edge_key in edge_types:
            e_type = edge_types[edge_key]
            if e_type == "tree":
                e_color = "#3498DB" # 파랑
                e_penwidth = "2.0"
            elif e_type == "back":
                e_color = "#E74C3C" # 빨강
                e_style = "dashed"  # 점선
                e_penwidth = "2.0"
            elif e_type == "cross":
                e_color = "#95A5A6" # 회색
                e_style = "dotted"  # 점선
        
        dot.edge(u, v, color=e_color, style=e_style, penwidth=e_penwidth)

    return dot

# --- 2. Streamlit Main App ---
def main():
    st.set_page_config(page_title="Graph Algo Viz", layout="wide", page_icon="🕸️")
    
    st.title("🕸️ Interactive Graph Visualizer")
    st.caption("Explainable Graph Traversal (Multi-Component, Directed/Undirected Support)")
    st.divider()

    # Session State Init
    if 'nodes' not in st.session_state: st.session_state.nodes = []
    if 'edges' not in st.session_state: st.session_state.edges = []
    if 'simulation_steps' not in st.session_state: st.session_state.simulation_steps = []
    if 'current_step_idx' not in st.session_state: st.session_state.current_step_idx = 0
    if 'is_simulating' not in st.session_state: st.session_state.is_simulating = False
    
    # 옵션
    if 'algo_type' not in st.session_state: st.session_state.algo_type = "BFS"
    if 'is_directed' not in st.session_state: st.session_state.is_directed = False

    # --- Sidebar ---
    with st.sidebar:
        st.header("1️⃣ Data Setting")
        
        is_directed = st.toggle("Directed Graph (유향 그래프)", value=False)
        st.session_state.is_directed = is_directed
        
        default_input = "A B\nA C\nB D\nC E\nC F\nE F" if not is_directed else "A B\nB C\nC A\nA D"
        
        tab1, tab2 = st.tabs(["Direct Input", "File Upload"])
        with tab1:
            raw_text = st.text_area("Edge List", value=default_input, height=150)
            if st.button("Load Text"):
                nodes, edges = data_manager.parse_edge_list(raw_text)
                st.session_state.nodes = nodes
                st.session_state.edges = edges
                st.session_state.is_simulating = False
                st.success(f"Loaded {len(nodes)} nodes ({'Directed' if is_directed else 'Undirected'})")
        with tab2:
            uploaded = st.file_uploader("Upload .txt", type="txt")
            if uploaded and st.button("Load File"):
                content = uploaded.getvalue().decode("utf-8")
                nodes, edges = data_manager.parse_edge_list(content)
                st.session_state.nodes = nodes
                st.session_state.edges = edges
                st.session_state.is_simulating = False
                st.success("File Loaded")

        st.divider()
        st.header("2️⃣ Algorithm")
        if st.session_state.nodes:
            algo = st.selectbox("Algorithm", ["BFS (Breadth-First)", "DFS (Depth-First)"])
            start = st.selectbox("Start Node", st.session_state.nodes)
            
            if st.button("🚀 Initialize", use_container_width=True):
                st.session_state.algo_type = algo
                
                # Backend Logic 호출
                if algo.startswith("BFS"):
                    steps = functions.run_bfs_simulation(
                        st.session_state.nodes, st.session_state.edges, start, is_directed
                    )
                else:
                    steps = functions.run_dfs_simulation(
                        st.session_state.nodes, st.session_state.edges, start, is_directed
                    )
                
                st.session_state.simulation_steps = steps
                st.session_state.current_step_idx = 0
                st.session_state.is_simulating = True
                st.rerun()

    # --- Main Area ---
    if st.session_state.is_simulating and st.session_state.simulation_steps:
        steps = st.session_state.simulation_steps
        idx = st.session_state.current_step_idx
        current_state = steps[idx]

        # Layout: Visualization (6) : Controls (4)
        col_viz, col_ctrl = st.columns([6, 4])
        
        # --- [Left] Visualization ---
        with col_viz:
            st.subheader("🖼️ Graph")
            dot_obj = render_graph(
                st.session_state.nodes, 
                st.session_state.edges, 
                current_state, 
                st.session_state.algo_type,
                st.session_state.is_directed
            )
            st.graphviz_chart(dot_obj, use_container_width=True)
            st.caption("🟦 Blue: Tree Edge | 🟥 Red Dashed: Back Edge | ⬜ Gray Dotted: Cross/Forward")
            
        # --- [Right] Control & Dashboard ---
        with col_ctrl:
            st.subheader("🎮 Controls & Status")
            
            # 1. Navigation Buttons
            c1, c2, c3 = st.columns([1, 2, 1])
            with c1:
                if st.button("⬅️ Prev", disabled=(idx==0), use_container_width=True):
                    st.session_state.current_step_idx -= 1
                    st.rerun()
            with c2:
                progress = (idx + 1) / len(steps)
                st.progress(progress)
                st.caption(f"Step {idx} / {len(steps)-1}")
            with c3:
                if st.button("Next ➡️", disabled=(idx==len(steps)-1), use_container_width=True):
                    st.session_state.current_step_idx += 1
                    st.rerun()

            st.divider()
            
            # 2. Queue/Stack Status
            if "queue" in current_state:
                st.markdown("**📥 Queue (FIFO):**")
                st.code(str(current_state["queue"]), language="text")
            elif "stack" in current_state:
                st.markdown("**🥞 Stack (LIFO):**")
                st.code(str(current_state["stack"]), language="text")
            
            st.divider()

            # 3. [New UX] Incremental Adjacency List (Strictly Expanded Only)
            st.markdown("**📂 Live Adjacency List:**")
            st.caption("Showing neighbors of *discovered* nodes only...")
            
            # --- UI Data Preparation ---
            curr_node = current_state.get("current_node", None)
            active_edges = current_state.get("active_edges", []) 
            
            # 현재 스텝에서 활성화된 이웃 찾기 (Highlight용)
            active_neighbors = []
            if curr_node and active_edges:
                for u, v in active_edges:
                    if u == curr_node:
                        active_neighbors.append(v)
            
            # [Core Logic] 원본 그래프 구조 (Reference)
            adj_dict = {node: [] for node in st.session_state.nodes}
            for u, v in st.session_state.edges:
                adj_dict[u].append(v)
                if not st.session_state.is_directed:
                    adj_dict[v].append(u)
            
            # [UX Fix] 필터링 조건 강화:
            # 1. Row Filter: 이미 확장된(Visit Order) 노드 + 현재 노드
            expanded_nodes = set(current_state.get("visit_order", []))
            if curr_node:
                expanded_nodes.add(curr_node)

            # 2. Neighbor Filter: 실제로 발견된(Visited - 큐에 들어감) 노드만 표시
            # 즉, 그래프상에서 색깔이 칠해진(Blue/Green/Gray/Black) 노드만 리스트에 뜸
            discovered_nodes = set(current_state.get("visited", []))
            
            # --- Rendering List ---
            with st.container(height=200, border=True):
                if not expanded_nodes:
                     st.info("No nodes expanded yet.")
                else:
                    # 확장된(Expanded) 노드들에 대해서만 리스트 출력
                    for node in sorted(list(expanded_nodes)):
                        neighbors = sorted(adj_dict[node])
                        
                        neighbor_display = []
                        for n in neighbors:
                            # [핵심 변경] 발견되지 않은 노드는 리스트에서 숨김 (???? 처리하거나 아예 안보임)
                            if n not in discovered_nodes:
                                continue 
                                
                            if node == curr_node and n in active_neighbors:
                                neighbor_display.append(f"**:red[{n}]**")
                            else:
                                neighbor_display.append(str(n))
                        
                        neighbors_str = ", ".join(neighbor_display)
                        
                        if node == curr_node:
                            st.markdown(f"👉 **:orange[{node}]** : [{neighbors_str}]")
                        else:
                            st.markdown(f"**{node}** : [{neighbors_str}]")

            # 4. Logs
            st.markdown("**📜 Logs:**")
            log_history = [s["log"] for s in steps[:idx+1]]
            st.text_area("Log Trace", value="\n".join(reversed(log_history)), height=150, label_visibility="collapsed")

        # --- Data Structure Inspection ---
        st.divider()
        st.subheader("🔍 Internal Data Structures")
        
        with st.expander("View Adjacency Matrix & List (Click to Expand)", expanded=False):
            header_nodes, matrix = functions.get_adjacency_matrix(
                st.session_state.nodes, 
                st.session_state.edges, 
                st.session_state.is_directed
            )
            adj_list_txt = functions.get_adjacency_list_text(
                st.session_state.nodes, 
                st.session_state.edges, 
                st.session_state.is_directed
            )
            
            d_col1, d_col2 = st.columns(2)
            
            with d_col1:
                st.markdown("**1️⃣ Adjacency List (인접 리스트)**")
                st.markdown("`O(V + E)` Space Complexity")
                st.code(adj_list_txt, language="text")
                
            with d_col2:
                st.markdown("**2️⃣ Adjacency Matrix (인접 행렬)**")
                st.markdown("`O(V^2)` Space Complexity")
                st.dataframe(pd.DataFrame(matrix, columns=header_nodes, index=header_nodes))

    else:
        st.info("👈 Please load data and initialize algorithm to start.")
        if st.session_state.nodes:
            # Preview (Static)
            is_d = st.session_state.is_directed
            dot = graphviz.Digraph(engine='neato') if is_d else graphviz.Graph(engine='neato')
            dot.attr(size='5.5,4.5!', ratio='fill', bgcolor='transparent') 
            dot.attr('node', shape='circle', style='filled', fillcolor='white', width='0.5', fontsize='10')
            dot.attr('edge', arrowsize='0.6')
            
            for u, v in st.session_state.edges:
                dot.edge(u, v)
            st.graphviz_chart(dot, use_container_width=True)

if __name__ == "__main__":
    main()