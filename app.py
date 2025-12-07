import streamlit as st
import graphviz
import pandas as pd 

# --- Local Modules ---
import data_manager 
import functions 

# --- 1. Visualization Helper ---
def render_graph(nodes, edges, step_state, algo_type, is_directed):
    """
    Renders the graph state using Graphviz based on the current step snapshot.
    Handles node coloring (SCC, Visited, Queue) and edge styling (Tree, Back, Cross).
    """
    if is_directed:
        dot = graphviz.Digraph(engine='neato')
    else:
        dot = graphviz.Graph(engine='neato')
    
    # Global Attributes
    dot.attr(size='5.5,4.5!', ratio='fill', bgcolor='transparent')
    dot.attr('node', shape='circle', style='filled', fontname='Helvetica', fontsize='10', fixedsize='true', width='0.5')
    dot.attr('edge', color='#BDC3C7', penwidth='1.2', arrowsize='0.6')

    # Unpack State
    visited_set = set(step_state.get("visited", []))
    current_node = step_state.get("current_node", None)
    active_edges = step_state.get("active_edges", [])
    
    levels = step_state.get("levels", {})
    visit_order = step_state.get("visit_order", [])
    in_structure = set(step_state.get("queue", []) + step_state.get("stack", []))
    
    # SCC Specifics
    scc_groups = step_state.get("scc_groups", {}) 
    scc_colors = ["#FFCDD2", "#C8E6C9", "#BBDEFB", "#FFF9C4", "#E1BEE7", "#FFECB3"]

    # --- Node Rendering ---
    for node in nodes:
        fillcolor = "#FFFFFF"
        fontcolor = "#000000"
        penwidth = "1"
        color = "#7F8C8D"
        label_text = node

        # Labeling: Show Level (BFS) or Depth (DFS)
        if node in levels:
            if algo_type.startswith("BFS"):
                label_text = f"{node}\nL{levels[node]}"
            elif algo_type.startswith("DFS"):
                label_text = f"{node}\nD{levels[node]}"
        
        # Priority 1: SCC Coloring
        if algo_type.startswith("SCC") and node in scc_groups:
            group_id = scc_groups[node]
            fillcolor = scc_colors[group_id % len(scc_colors)]
            color = "#555555"
            label_text = f"{node}\nG{group_id}"
            
        # Priority 2: Visited / Topo Result
        elif node in visited_set:
            fillcolor = "#D5F5E3" # Mint
            color = "#2ECC71"
            
            # Topological Sort Rank
            if algo_type == "Topological Sort" and node in visit_order:
                order_idx = visit_order.index(node) + 1
                label_text = f"{node}\n#{order_idx}"

        # Priority 3: In Queue/Stack
        if node in in_structure:
            fillcolor = "#D6EAF8" # Blue
            color = "#3498DB"

        # Highlight Current Node
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
        
        # 1. Active Edge (Current Step)
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

    # Session State Initialization
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
        
        default_input = "A B\nA C\nB D\nC E\nC F\nE F" if not is_directed else "A B\nB D\nB C\nC E\nE F"
        
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
        
        if st.session_state.nodes:
            algo_options = ["BFS (Breadth-First)", "DFS (Depth-First)", "Topological Sort", "SCC (Kosaraju)"]
            algo = st.selectbox("Choose Algorithm", algo_options)
            
            # Start Node selection (Enabled for all algos to define traversal order)
            start_node = st.selectbox("Start Node", st.session_state.nodes)
            
            if st.button("🚀 Initialize Simulation", use_container_width=True):
                st.session_state.algo_type = algo
                steps = []

                # Execute Backend Logic (Passing strict keyword arguments)
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
                            nodes=st.session_state.nodes, 
                            edges=st.session_state.edges, 
                            start_node=start_node, 
                            is_directed=is_directed
                        )
                elif algo.startswith("SCC"):
                    if not is_directed:
                        st.error("SCC requires a Directed Graph.")
                    else:
                        steps = functions.run_scc_kosaraju_ui(
                            nodes=st.session_state.nodes, 
                            edges=st.session_state.edges, 
                            start_node=start_node, 
                            is_directed=is_directed
                        )
                
                if steps:
                    st.session_state.simulation_steps = steps
                    st.session_state.current_step_idx = 0
                    st.session_state.is_simulating = True
                    st.rerun()

    # --- Main Visualization Area ---
    if st.session_state.is_simulating and st.session_state.simulation_steps:
        steps = st.session_state.simulation_steps
        idx = st.session_state.current_step_idx
        current_state = steps[idx]
        algo_type = st.session_state.algo_type

        # Layout: Visualization (60%) : Controls (40%)
        col_viz, col_ctrl = st.columns([6, 4])
        
        # --- [Left] Graph Visualization ---
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
            
            # Legend
            if algo_type.startswith("SCC"):
                st.caption("🎨 Colors represent different SCC groups")
            else:
                st.caption("🟦 Blue: Tree Edge | 🟥 Red Dashed: Back Edge | ⬜ Gray Dotted: Cross/Forward")
            
        # --- [Right] Dashboard & Metrics ---
        with col_ctrl:
            st.subheader("🎮 Controls")
            
            # 1. Navigation Controls
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
            
            # 2. Key Metrics (Components & Tree Edges)
            current_comp_count = current_state.get("component_count", 0)
            
            # Count Tree Edges
            edge_types = current_state.get("edge_types", {})
            tree_edge_count = 0
            if edge_types:
                for t in edge_types.values():
                    if t == "tree":
                        tree_edge_count += 1
            
            # Display Metrics
            m_col1, m_col2 = st.columns(2)
            with m_col1:
                label_comp = "📦 Found SCCs" if algo_type.startswith("SCC") else "🔗 Components"
                st.metric(label=label_comp, value=current_comp_count)
            with m_col2:
                if algo_type in ["BFS (Breadth-First)", "DFS (Depth-First)"]:
                    st.metric(label="🌲 Tree Edges", value=tree_edge_count)
                else:
                    visited_cnt = len(current_state.get("visited", []))
                    st.metric(label="👣 Visited", value=visited_cnt)

            st.divider()

            # 3. Dynamic Status Panel
            # Display Queue or Stack
            if "queue" in current_state:
                st.markdown("**📥 Queue (FIFO):**")
                st.code(str(current_state["queue"]), language="text")
            elif "stack" in current_state:
                st.markdown("**🥞 Stack (LIFO):**")
                st.code(str(current_state["stack"]), language="text")
            
            st.divider()

            # Context-Aware Information
            if algo_type in ["BFS (Breadth-First)", "DFS (Depth-First)"]:
                st.markdown("**📂 Live Adjacency List:**")
                st.caption("Neighbors of discovered nodes only")
                
                curr_node = current_state.get("visited", [])[-1] if current_state.get("visited") else None
                active_edges = current_state.get("active_edges", [])
                active_neighbors = [v for u, v in active_edges if u == curr_node]
                
                # Reconstruct full adj list for reference
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
                                if n not in discovered_nodes: continue
                                if node == curr_node and n in active_neighbors:
                                    display_strs.append(f"**:red[{n}]**")
                                else:
                                    display_strs.append(str(n))
                            st.markdown(f"**{node}** : [{', '.join(display_strs)}]")

            elif algo_type == "Topological Sort":
                st.markdown("**🔢 Topological Sort Order (Result):**")
                visit_order = current_state.get("visit_order", [])
                
                if not visit_order:
                    st.info("Searching... No nodes sorted yet.")
                else:
                    st.success(f"**Current Order:** {' → '.join(visit_order)}")

            elif algo_type.startswith("SCC"):
                st.markdown("**📦 Identified SCC Groups:**")
                scc_dict = current_state.get("scc_groups", {})
                
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
            
            # 4. Execution Logs
            st.divider()
            st.markdown("**📜 Execution Log History:**")
            
            history_logs = [s["log"] for s in steps[:idx+1]]
            
            with st.container(height=200, border=True):
                for i, msg in enumerate(reversed(history_logs)):
                    if i == 0:
                        st.info(f"**[Current]** {msg}", icon="👉")
                    else:
                        st.caption(f"• {msg}")
  
        # --- Internal Data Structures (Bottom) ---
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
                st.markdown("**1️⃣ Adjacency List**")
                st.caption("Storage: `O(V + E)`")
                st.code(adj_list_txt, language="text")
                
            with d_col2:
                st.markdown("**2️⃣ Adjacency Matrix**")
                st.caption("Storage: `O(V^2)`")
                st.dataframe(pd.DataFrame(matrix, columns=header_nodes, index=header_nodes))

    else:
        # Initial State (No Simulation)
        st.info("👈 Select Algorithm from Sidebar and Click 'Initialize'")
        if st.session_state.nodes:
            # Static Preview
            is_d = st.session_state.is_directed
            dot = graphviz.Digraph(engine='neato') if is_d else graphviz.Graph(engine='neato')
            dot.attr(size='5.5,4.5!', ratio='fill', bgcolor='transparent') 
            dot.attr('node', shape='circle', style='filled', fillcolor='white', width='0.5', fontsize='10')
            
            for u, v in st.session_state.edges:
                dot.edge(u, v)
            st.graphviz_chart(dot, use_container_width=True)

if __name__ == "__main__":
    main()
