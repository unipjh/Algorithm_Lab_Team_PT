# app.py
import streamlit as st
import graphviz
import pandas as pd 

# --- Local Modules ---
import data_manager 
import functions 

# --- 1. Visualization Helper ---
def render_graph(nodes, edges, step_state, algo_type, is_directed):
    # [설정] 그래프 엔진 설정
    if is_directed:
        dot = graphviz.Digraph(engine='neato')
    else:
        dot = graphviz.Graph(engine='neato')
    
    dot.attr(size='5.5,4.5!', ratio='fill', bgcolor='transparent')
    dot.attr('node', shape='circle', style='filled', fontname='Helvetica', fontsize='10', fixedsize='true', width='0.5')
    dot.attr('edge', color='#BDC3C7', penwidth='1.2', arrowsize='0.6')

    # [State Unpacking]
    visited_set = set(step_state.get("visited", []))
    current_node = step_state.get("current_node", None)
    active_edges = step_state.get("active_edges", [])
    
    # 알고리즘별 데이터 키 처리
    levels = step_state.get("levels", {})
    visit_order = step_state.get("visit_order", [])
    
    # 큐/스택 처리 (키가 없으면 빈 리스트)
    in_structure = set(step_state.get("queue", []) + step_state.get("stack", []))
    
    # SCC 그룹 정보
    scc_groups = step_state.get("scc_groups", {}) 
    scc_colors = ["#FFCDD2", "#C8E6C9", "#BBDEFB", "#FFF9C4", "#E1BEE7", "#FFECB3"]

    # --- Node Rendering ---
    for node in nodes:
        fillcolor = "#FFFFFF"
        fontcolor = "#000000"
        penwidth = "1"
        color = "#7F8C8D"
        label_text = node

        # 1. Labeling & Basic Coloring
        if algo_type.startswith("BFS") and node in levels:
            label_text = f"{node}\nL{levels[node]}"
        
        # 2. Status Coloring
        # (A) SCC Coloring (최우선)
        if algo_type.startswith("SCC") and node in scc_groups:
            group_id = scc_groups[node]
            fillcolor = scc_colors[group_id % len(scc_colors)]
            color = "#555555"
            label_text = f"{node}\nG{group_id}"
            
        # (B) Visited / Topological Result
        elif node in visited_set:
            fillcolor = "#D5F5E3" # 민트
            color = "#2ECC71"
            
            # 위상 정렬: 결과 리스트에 들어간 경우 순서 표시
            if algo_type == "Topological Sort" and node in visit_order:
                order_idx = visit_order.index(node) + 1
                label_text = f"{node}\n#{order_idx}"

        # (C) In Queue/Stack (Processing)
        if node in in_structure:
            fillcolor = "#D6EAF8" # 파랑
            color = "#3498DB"

        # (D) Current Node (Highlight)
        if node == current_node:
            fillcolor = "#F9E79F"
            color = "#F1C40F"
            penwidth = "2.5"

        dot.node(node, label=label_text, fillcolor=fillcolor, color=color, penwidth=penwidth, fontcolor=fontcolor)

    # --- Edge Rendering ---
    active_edge_set = set(active_edges)
    edge_types = step_state.get("edge_types", {})

    for u, v in edges:
        edge_key = tuple(sorted((u, v))) if not is_directed else (u, v)
        
        e_color = "#BDC3C7"
        e_style = "solid"
        e_penwidth = "1.2"
        
        # 1. Active (Current Step)
        if (u, v) in active_edge_set or (not is_directed and (v, u) in active_edge_set):
            e_color = "#E74C3C" 
            e_penwidth = "2.5"
        
        # 2. Classified Edges (Tree/Back/Cross)
        elif edge_key in edge_types:
            e_type = edge_types[edge_key]
            if e_type == "tree":
                e_color = "#3498DB"
                e_penwidth = "2.0"
            elif e_type == "back":
                e_color = "#E74C3C"
                e_style = "dashed"
                e_penwidth = "2.0"
            elif e_type == "cross":
                e_color = "#95A5A6"
                e_style = "dotted"
        
        dot.edge(u, v, color=e_color, style=e_style, penwidth=e_penwidth)

    return dot

# --- 2. Streamlit Main App ---
def main():
    st.set_page_config(page_title="Graph Algo Viz", layout="wide", page_icon="🕸️")
    
    st.title("🕸️ Interactive Graph Visualizer")
    st.caption("Explainable Graph Traversal (BFS/DFS, Topological, SCC)")
    st.divider()

    # Session State Init
    if 'nodes' not in st.session_state: st.session_state.nodes = []
    if 'edges' not in st.session_state: st.session_state.edges = []
    if 'simulation_steps' not in st.session_state: st.session_state.simulation_steps = []
    if 'current_step_idx' not in st.session_state: st.session_state.current_step_idx = 0
    if 'is_simulating' not in st.session_state: st.session_state.is_simulating = False
    if 'algo_type' not in st.session_state: st.session_state.algo_type = "BFS"
    if 'is_directed' not in st.session_state: st.session_state.is_directed = False

    # --- Sidebar (Controls) ---
    with st.sidebar:
        st.header("1️⃣ Data Setting")
        
        is_directed = st.toggle("Directed Graph (유향)", value=st.session_state.is_directed)
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
                st.success(f"Loaded {len(nodes)} nodes")
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
        st.header("2️⃣ Algorithm Selection")
        
        # [수정] 메인 화면에 있던 알고리즘 선택을 사이드바로 확실히 이동
        if st.session_state.nodes:
            algo_options = ["BFS (Breadth-First)", "DFS (Depth-First)", "Topological Sort", "SCC (Kosaraju)"]
            algo = st.selectbox("Choose Algorithm", algo_options)
            
            # 시작 노드 선택 (Topo, SCC는 자동 순회하므로 비활성화 가능하지만, 로직상 무관하면 유지)
            # 여기서는 편의상 Topo/SCC일 때 시작 노드 선택을 숨기거나 비활성화
            use_start_node = algo in ["BFS (Breadth-First)", "DFS (Depth-First)"]
            start_node = st.selectbox("Start Node", st.session_state.nodes, disabled=not use_start_node)
            
            if st.button("🚀 Initialize Simulation", use_container_width=True):
                st.session_state.algo_type = algo
                steps = []

                # Backend Logic Call
                if algo.startswith("BFS"):
                    steps = functions.run_bfs_simulation(
                        st.session_state.nodes, st.session_state.edges, start_node, is_directed
                    )
                elif algo.startswith("DFS"):
                    steps = functions.run_dfs_simulation(
                        st.session_state.nodes, st.session_state.edges, start_node, is_directed
                    )
                elif algo == "Topological Sort":
                    if not is_directed:
                        st.error("Topological Sort requires a Directed Graph.")
                    else:
                        steps = functions.run_topological_sort_simulation(
                            st.session_state.nodes, st.session_state.edges, is_directed
                        )
                elif algo.startswith("SCC"):
                    if not is_directed:
                        st.error("SCC requires a Directed Graph.")
                    else:
                        steps = functions.run_scc_kosaraju_ui(
                            st.session_state.nodes, st.session_state.edges, is_directed
                        )
                
                if steps:
                    st.session_state.simulation_steps = steps
                    st.session_state.current_step_idx = 0
                    st.session_state.is_simulating = True
                    st.rerun()

    # --- Main Area ---
    if st.session_state.is_simulating and st.session_state.simulation_steps:
        steps = st.session_state.simulation_steps
        idx = st.session_state.current_step_idx
        current_state = steps[idx]
        algo_type = st.session_state.algo_type

        # Layout: Visualization (6) : Controls (4)
        col_viz, col_ctrl = st.columns([6, 4])
        
        # --- [Left] Visualization ---
        with col_viz:
            st.subheader(f"🖼️ {algo_type} View")
            dot_obj = render_graph(
                st.session_state.nodes, 
                st.session_state.edges, 
                current_state, 
                algo_type,
                st.session_state.is_directed
            )
            st.graphviz_chart(dot_obj, use_container_width=True)
            
            # 범례 표시
            if algo_type.startswith("SCC"):
                st.caption("🎨 Colors represent different SCC groups")
            else:
                st.caption("🟦 Blue: Tree Edge | 🟥 Red Dashed: Back Edge | ⬜ Gray Dotted: Cross/Forward")
            
        # --- [Right] Control & Dashboard ---
        with col_ctrl:
            st.subheader("🎮 Controls")
            
            # 1. Navigation
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
            
            # 2. Status Panel (Dynamic UI)
            # [수정] 알고리즘 타입에 따라 보여줄 정보를 다르게 구성
            
            # (A) Queue/Stack Status (공통: 있으면 보여줌)
            if "queue" in current_state:
                st.markdown("**📥 Queue (FIFO):**")
                st.code(str(current_state["queue"]), language="text")
            elif "stack" in current_state:
                st.markdown("**🥞 Stack (LIFO):**")
                st.code(str(current_state["stack"]), language="text")
            
            st.divider()

            # (B) Context-Aware Info Panel
            if algo_type in ["BFS (Breadth-First)", "DFS (Depth-First)"]:
                # --- BFS/DFS: Live Adjacency List ---
                st.markdown("**📂 Live Adjacency List:**")
                st.caption("Neighbors of discovered nodes only")
                
                curr_node = current_state.get("visited", [])[-1] if current_state.get("visited") else None
                active_edges = current_state.get("active_edges", [])
                active_neighbors = [v for u, v in active_edges if u == curr_node]
                
                # 인접 리스트 빌드 (참조용)
                adj_dict = {node: [] for node in st.session_state.nodes}
                for u, v in st.session_state.edges:
                    adj_dict[u].append(v)
                    if not st.session_state.is_directed:
                        adj_dict[v].append(u)
                
                discovered_nodes = set(current_state.get("visited", []))
                
                with st.container(height=200, border=True):
                    if not discovered_nodes:
                        st.info("No nodes discovered yet.")
                    else:
                        for node in sorted(list(discovered_nodes)):
                            neighbors = sorted(adj_dict[node])
                            display_strs = []
                            for n in neighbors:
                                if n not in discovered_nodes: continue # 아직 발견 안 된 이웃 숨김
                                if node == curr_node and n in active_neighbors:
                                    display_strs.append(f"**:red[{n}]**")
                                else:
                                    display_strs.append(str(n))
                            
                            st.markdown(f"**{node}** : [{', '.join(display_strs)}]")

            elif algo_type == "Topological Sort":
                # --- Topological Sort: Result Order ---
                st.markdown("**🔢 Topological Sort Order (Result):**")
                st.caption("Nodes are added here after they finish processing (pop).")
                
                visit_order = current_state.get("visit_order", [])
                
                if not visit_order:
                    st.info("Searching... No nodes sorted yet.")
                else:
                    # 결과를 예쁜 카드로 표시
                    st.success(f"**Current Order:** {' → '.join(visit_order)}")

            elif algo_type.startswith("SCC"):
                # --- SCC: Identified Groups ---
                st.markdown("**📦 Identified SCC Groups:**")
                
                scc_dict = current_state.get("scc_groups", {}) # {node: group_id}
                
                # Grouping invert: {group_id: [nodes]}
                groups = {}
                for node, gid in scc_dict.items():
                    if gid not in groups: groups[gid] = []
                    groups[gid].append(node)
                
                if not groups:
                    st.info("Searching... No SCCs completed yet.")
                else:
                    with st.container(height=200, border=True):
                        for gid in sorted(groups.keys()):
                            members = sorted(groups[gid])
                            st.success(f"**SCC #{gid+1}:** {members}")
            
            # 3. Execution Log (History)
            st.divider()
            st.markdown("**📜 Execution Log History:**")
            
            # 0부터 현재 idx까지의 모든 로그 수집
            history_logs = [s["log"] for s in steps[:idx+1]]
            
            # 스크롤 가능한 영역 생성 (높이 200px 고정)
            with st.container(height=200, border=True):
                # 최신 로그가 상단에 오도록 역순(reversed)으로 출력
                for i, msg in enumerate(reversed(history_logs)):
                    if i == 0:
                        # 현재 스텝 (가장 최신) 강조 표시
                        st.info(f"**[Current]** {msg}", icon="👉")
                    else:
                        # 지나간 과거 스텝 (회색 텍스트)
                        st.caption(f"• {msg}")
  
        # [수정 위치] col_viz, col_ctrl 컬럼 들여쓰기를 탈출하여, 맨 아래에 전체 너비로 작성
        st.divider()
        st.subheader("🔍 Internal Data Structures")
        
        with st.expander("View Adjacency Matrix & List (Click to Expand)", expanded=False):
            # functions.py의 헬퍼 함수를 사용하여 데이터 가져오기
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
            
            # 내부에서 2단으로 나누어 보여주기
            d_col1, d_col2 = st.columns(2)
            
            with d_col1:
                st.markdown("**1️⃣ Adjacency List (인접 리스트)**")
                st.caption("Storage: `O(V + E)`")
                st.code(adj_list_txt, language="text")
                
            with d_col2:
                st.markdown("**2️⃣ Adjacency Matrix (인접 행렬)**")
                st.caption("Storage: `O(V^2)`")
                # Pandas DataFrame을 사용하여 깔끔하게 렌더링
                st.dataframe(pd.DataFrame(matrix, columns=header_nodes, index=header_nodes))

        # --- (End of is_simulating block) ---

    else:
        # Initial Empty State
        st.info("👈 Select Algorithm from Sidebar and Click 'Initialize'")
        if st.session_state.nodes:
            # Preview (Static)
            is_d = st.session_state.is_directed
            dot = graphviz.Digraph(engine='neato') if is_d else graphviz.Graph(engine='neato')
            dot.attr(size='5.5,4.5!', ratio='fill', bgcolor='transparent') 
            dot.attr('node', shape='circle', style='filled', fillcolor='white', width='0.5', fontsize='10')
            
            for u, v in st.session_state.edges:
                dot.edge(u, v)
            st.graphviz_chart(dot, use_container_width=True)

if __name__ == "__main__":
    main()
