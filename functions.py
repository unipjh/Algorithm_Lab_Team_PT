# functions.py (전체 코드 업데이트)
from collections import deque

# ... (Helper 함수들은 그대로 유지) ...
def _binary_search(sorted_arr, target):
    left, right = 0, len(sorted_arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if sorted_arr[mid] == target:
            return mid
        elif sorted_arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1

def _create_mapping_list(nodes):
    unique_nodes = []
    for node in nodes:
        exists = False
        for n in unique_nodes:
            if n == node:
                exists = True
                break
        if not exists:
            unique_nodes.append(node)
    
    n = len(unique_nodes)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if unique_nodes[j] < unique_nodes[min_idx]:
                min_idx = j
        if min_idx != i:
            unique_nodes[i], unique_nodes[min_idx] = unique_nodes[min_idx], unique_nodes[i]
    return unique_nodes

def _build_adj_list_indices_no_dict(n, edges, sorted_nodes, is_directed, reverse=False):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        u_idx = _binary_search(sorted_nodes, u)
        v_idx = _binary_search(sorted_nodes, v)
        if u_idx != -1 and v_idx != -1:
            src, dst = (v_idx, u_idx) if reverse else (u_idx, v_idx)
            if dst not in adj[src]: 
                adj[src].append(dst)
            if not is_directed and not reverse:
                if src not in adj[dst]:
                    adj[dst].append(src)
    for neighbors in adj:
        m = len(neighbors)
        for i in range(m):
            min_idx = i
            for j in range(i + 1, m):
                if neighbors[j] < neighbors[min_idx]:
                    min_idx = j
            if min_idx != i:
                neighbors[i], neighbors[min_idx] = neighbors[min_idx], neighbors[i]
    return adj

# ============================================================
# 1. BFS
# ============================================================
def run_bfs_simulation(nodes, edges, start_node, is_directed=False):
    sorted_nodes_map = _create_mapping_list(nodes)
    n = len(sorted_nodes_map)
    start_idx = _binary_search(sorted_nodes_map, start_node)
    adj = _build_adj_list_indices_no_dict(n, edges, sorted_nodes_map, is_directed)

    visited = [False] * n
    levels = [-1] * n
    queue = deque()
    steps = []
    comp_count = 0
    global_visit_order = [] 
    
    # [추가] BFS에서도 간선 타입을 추적하기 위한 리스트
    edge_types_list = []

    search_sequence = []
    if start_idx != -1: search_sequence.append(start_idx)
    for i in range(n):
        if i != start_idx: search_sequence.append(i)

    for root in search_sequence:
        if visited[root]: continue
        comp_count += 1
        visited[root] = True
        levels[root] = 0
        queue.append(root)

        # [수정] edge_types_list 전달
        steps.append(_make_snapshot_bfs_dfs(sorted_nodes_map, visited, global_visit_order, list(queue), [], levels, edge_types_list, comp_count, 
                                    f"🚀 Start Component #{comp_count} (Root: {sorted_nodes_map[root]})", algo_style="BFS"))

        while queue:
            curr = queue.popleft()
            if curr not in global_visit_order: global_visit_order.append(curr)
            
            steps.append(_make_snapshot_bfs_dfs(sorted_nodes_map, visited, global_visit_order, list(queue), [], levels, edge_types_list, comp_count,
                                        f"📍 Visit: {sorted_nodes_map[curr]} (L{levels[curr]})", algo_style="BFS"))

            for neighbor in adj[curr]:
                if not visited[neighbor]:
                    visited[neighbor] = True
                    levels[neighbor] = levels[curr] + 1
                    
                    # [핵심 추가] BFS Tree Edge 기록
                    u_str, v_str = sorted_nodes_map[curr], sorted_nodes_map[neighbor]
                    ekey = (u_str, v_str) if is_directed else (tuple(sorted((u_str, v_str))))
                    edge_types_list.append((ekey, "tree"))
                    
                    queue.append(neighbor)
                    
                    steps.append(_make_snapshot_bfs_dfs(sorted_nodes_map, visited, global_visit_order, list(queue), [(curr, neighbor)], levels, edge_types_list, comp_count,
                                                f"  🔎 Discovered (Tree Edge): {sorted_nodes_map[neighbor]} -> Queue", algo_style="BFS"))
    
    steps.append(_make_snapshot_bfs_dfs(sorted_nodes_map, visited, global_visit_order, [], [], levels, edge_types_list, comp_count, 
                                        f"✅ BFS Traversal Complete. (Total Components: {comp_count})", algo_style="BFS"))
    return steps

# ============================================================
# 2. DFS
# ============================================================
def run_dfs_simulation(nodes, edges, start_node, is_directed=False):
    sorted_nodes_map = _create_mapping_list(nodes)
    n = len(sorted_nodes_map)
    start_idx = _binary_search(sorted_nodes_map, start_node)
    adj = _build_adj_list_indices_no_dict(n, edges, sorted_nodes_map, is_directed)

    colors = [0] * n 
    depths = [-1] * n
    steps = []
    comp_count = 0
    global_visit_order = []
    edge_types_list = [] 

    search_sequence = []
    if start_idx != -1: search_sequence.append(start_idx)
    for i in range(n):
        if i != start_idx: search_sequence.append(i)

    for root in search_sequence:
        if colors[root] != 0: continue
        comp_count += 1
        stack = [[root, 0, 0]]
        colors[root] = 1 
        global_visit_order.append(root)
        depths[root] = 0
        
        steps.append(_make_snapshot_bfs_dfs(sorted_nodes_map, colors, global_visit_order, stack, [], depths, edge_types_list, comp_count,
                                        f"🚀 Start Component #{comp_count} (Root: {sorted_nodes_map[root]})", algo_style="DFS"))
      
        while stack:
            u, iter_idx, d = stack[-1]
            neighbors = adj[u]

            if iter_idx < len(neighbors):
                v = neighbors[iter_idx]
                stack[-1][1] += 1
                u_str, v_str = sorted_nodes_map[u], sorted_nodes_map[v]
                ekey = (u_str, v_str) if is_directed else (tuple(sorted((u_str, v_str))))
                existing_type = None
                for k, t in edge_types_list:
                    if k == ekey: existing_type = t; break

                if colors[v] == 0: 
                    edge_types_list.append((ekey, "tree"))
                    colors[v] = 1 
                    depths[v] = d + 1
                    global_visit_order.append(v)
                    stack.append([v, 0, d + 1])
                    steps.append(_make_snapshot_bfs_dfs(sorted_nodes_map, colors, global_visit_order, stack, [(u, v)], depths, edge_types_list, comp_count,
                                                    f"  Tree Edge: {u_str}->{v_str}", algo_style="DFS"))
                elif colors[v] == 1: 
                    is_parent = (not is_directed and len(stack) >= 2 and stack[-2][0] == v)
                    if not is_parent and existing_type is None:
                        edge_types_list.append((ekey, "back"))
                        steps.append(_make_snapshot_bfs_dfs(sorted_nodes_map, colors, global_visit_order, stack, [(u, v)], depths, edge_types_list, comp_count,
                                                        f"  🔄 Back Edge: {u_str}->{v_str}", algo_style="DFS"))
                elif colors[v] == 2:
                    if is_directed and existing_type is None:
                        edge_types_list.append((ekey, "cross"))
                        steps.append(_make_snapshot_bfs_dfs(sorted_nodes_map, colors, global_visit_order, stack, [(u, v)], depths, edge_types_list, comp_count,
                                                        f"  Cross/Forward: {u_str}->{v_str}", algo_style="DFS"))
            else:
                stack.pop()
                colors[u] = 2
                steps.append(_make_snapshot_bfs_dfs(sorted_nodes_map, colors, global_visit_order, stack, [], depths, edge_types_list, comp_count,
                                                f"🔙 Backtrack: Finished {sorted_nodes_map[u]}", algo_style="DFS"))

    # [수정] 마지막 로그에 총 개수 포함
    steps.append(_make_snapshot_bfs_dfs(sorted_nodes_map, colors, global_visit_order, [], [], depths, edge_types_list, comp_count, 
                                        f"✅ DFS Traversal Complete. (Total Components: {comp_count})", algo_style="DFS"))
    return steps

# ============================================================
# 3. Topological Sort
# ============================================================
def run_topological_sort_simulation(nodes, edges, start_node=None, is_directed=True):
    node_map = _create_mapping_list(nodes)
    n = len(node_map)
    adj = _build_adj_list_indices_no_dict(n, edges, node_map, is_directed)

    visited = [0] * n 
    stack = []         
    steps = []         
    global_visit_order = [] 
    comp_count = 0     

    start_idx = _binary_search(node_map, start_node) if start_node else -1
    search_sequence = []
    if start_idx != -1: search_sequence.append(start_idx)
    for i in range(n):
        if i != start_idx: search_sequence.append(i)

    for root in search_sequence:
        if visited[root] != 0: continue

        comp_count += 1
        steps.append(_make_snapshot_topo(
            node_map, visited, global_visit_order, stack, None, comp_count,
            f"🚀 Start Component #{comp_count} (Root: {node_map[root]})"
        ))

        try:
            def dfs(u):
                visited[u] = 1 
                global_visit_order.append(u)
                steps.append(_make_snapshot_topo(
                    node_map, visited, global_visit_order, stack, None, comp_count,
                    f"➡ Visit {node_map[u]}"
                ))

                for v in adj[u]:
                    if visited[v] == 0:
                        dfs(v)
                    elif visited[v] == 1:
                        steps.append(_make_snapshot_topo(
                            node_map, visited, global_visit_order, stack, (u, v), comp_count,
                            f"❌ Cycle Detected: {node_map[u]} → {node_map[v]}"
                        ))
                        raise ValueError("CYCLE")

                visited[u] = 2 
                stack.append(u) 
                steps.append(_make_snapshot_topo(
                    node_map, visited, global_visit_order, stack, None, comp_count,
                    f"📌 Finishing: {node_map[u]} push"
                ))

            dfs(root)

        except ValueError:
            steps.append(_make_snapshot_topo(
                node_map, visited, global_visit_order, stack, None, comp_count,
                "⛔ Topological Sort Failed (Cycle Detected)"
            ))
            return steps 

    ordering = []
    temp_stack = list(stack)
    
    steps.append(_make_snapshot_topo(
        node_map, visited, global_visit_order, stack, None, comp_count,
        "🔄 DFS Finished. Pop from stack to generate order."
    ))

    while temp_stack:
        node_idx = temp_stack.pop()
        ordering.append(node_idx)
        steps.append(_make_snapshot_topo(
            node_map, visited, ordering, temp_stack, None, comp_count,
            f"🔽 Pop: {node_map[node_idx]} (Rank {len(ordering)})"
        ))

    # [수정] 마지막 로그에 총 개수 포함 (TopoSort는 컴포넌트 개념이 약하지만 DFS 기반이므로 표시 가능)
    steps.append(_make_snapshot_topo(
        node_map, visited, ordering, [], None, comp_count,
        f"✅ Topological Sort Complete. (Processed {comp_count} Components)"
    ))

    return steps

# ============================================================
# 4. SCC
# ============================================================
def run_scc_kosaraju_ui(nodes, edges, start_node=None, is_directed=True):
    steps = []
    node_map = _create_mapping_list(nodes)
    n = len(node_map)

    adj  = _build_adj_list_indices_no_dict(n, edges, node_map, is_directed, reverse=False)
    radj = _build_adj_list_indices_no_dict(n, edges, node_map, is_directed, reverse=True)

    start_idx = _binary_search(node_map, start_node) if start_node else -1
    search_sequence = []
    if start_idx != -1: search_sequence.append(start_idx)
    for i in range(n):
        if i != start_idx: search_sequence.append(i)

    # --- Phase 1 ---
    colors = [0] * n
    visit_order = []
    order_stack = []

    def dfs1(u):
        colors[u] = 1
        visit_order.append(u)
        steps.append(_make_snapshot_scc(
            phase=1, description=f"➡ DFS1 Visit: {node_map[u]}",
            node_map=node_map, colors=colors, visit_order=visit_order,
            order_stack=order_stack, scc_groups=[], current_scc=[]
        ))

        for v in adj[u]:
            if colors[v] == 0:
                dfs1(v)

        colors[u] = 2
        order_stack.append(u)
        steps.append(_make_snapshot_scc(
            phase=1, description=f"⬆ Finished (push): {node_map[u]}",
            node_map=node_map, colors=colors, visit_order=visit_order,
            order_stack=order_stack, scc_groups=[], current_scc=[]
        ))

    for i in search_sequence:
        if colors[i] == 0:
            dfs1(i)

    # --- Phase 2 ---
    colors = [0] * n 
    scc_groups = []  

    def dfs2(u, current_scc):
        colors[u] = 1
        current_scc.append(u)
        steps.append(_make_snapshot_scc(
            phase=2, description=f"➡ DFS2 (Reverse) Visit: {node_map[u]}",
            node_map=node_map, colors=colors, visit_order=visit_order,
            order_stack=order_stack, scc_groups=scc_groups, current_scc=current_scc
        ))

        for v in radj[u]:
            if colors[v] == 0:
                dfs2(v, current_scc)
        colors[u] = 2

    steps.append(_make_snapshot_scc(
        phase=2, description="🔄 Phase 2: Pop Stack & Start Reverse DFS",
        node_map=node_map, colors=colors, visit_order=visit_order,
        order_stack=order_stack, scc_groups=scc_groups, current_scc=[]
    ))

    while order_stack:
        start = order_stack.pop()
        if colors[start] != 0:
            continue
        
        new_scc = []
        dfs2(start, new_scc)
        scc_groups.append(new_scc)

        steps.append(_make_snapshot_scc(
            phase=2, description=f"📦 SCC Found #{len(scc_groups)}: {[node_map[x] for x in new_scc]}",
            node_map=node_map, colors=colors, visit_order=visit_order,
            order_stack=order_stack, scc_groups=scc_groups, current_scc=new_scc
        ))

    # [수정] 마지막 로그에 총 개수 포함
    steps.append(_make_snapshot_scc(
        phase=2, description=f"🏁 SCC Search Complete. (Total SCCs: {len(scc_groups)})",
        node_map=node_map, colors=colors, visit_order=visit_order,
        order_stack=order_stack, scc_groups=scc_groups, current_scc=[]
    ))

    return steps

# ============================================================
# Snapshot Helpers
# ============================================================
def _make_snapshot_bfs_dfs(node_map, visited_arr, order_indices, structure_list, active_tuple_list, levels_arr, edge_types_list, comp_cnt, log, algo_style="BFS"):
    edge_types_dict = {}
    if isinstance(edge_types_list, list):
        for k, t in edge_types_list:
            edge_types_dict[k] = t
    
    flat_structure = []
    for item in structure_list:
        if isinstance(item, list): 
            flat_structure.append(node_map[item[0]])
        else: 
            flat_structure.append(node_map[item])

    snapshot = {
        "visited": [node_map[i] for i, v in enumerate(visited_arr) if v and (isinstance(v, bool) or v > 0)],
        "visit_order": [node_map[i] for i in order_indices],
        "active_edges": [(node_map[u], node_map[v]) for u, v in active_tuple_list],
        "levels": {node_map[i]: l for i, l in enumerate(levels_arr) if l != -1},
        "edge_types": edge_types_dict,
        "component_count": comp_cnt, # 이미 포함되어 있음
        "log": log
    }

    if algo_style == "BFS":
        snapshot["queue"] = flat_structure
    else:
        snapshot["stack"] = flat_structure

    return snapshot

def _make_snapshot_topo(node_map, colors, visit_order, stack, edge, comp_count, message):
    visited_nodes = [node_map[i] for i, c in enumerate(colors) if c > 0]
    stack_nodes = [node_map[i] for i in stack]
    active_e = []
    if edge:
        active_e.append((node_map[edge[0]], node_map[edge[1]]))
    
    visit_order_str = [node_map[i] for i in visit_order]

    return {
        "visited": visited_nodes,
        "visit_order": visit_order_str, 
        "stack": stack_nodes,
        "active_edges": active_e,
        "log": message,
        "component_count": comp_count, # 이미 포함되어 있음
        "levels": {}, 
        "edge_types": {}
    }

def _make_snapshot_scc(phase, description, node_map, colors, visit_order, order_stack, scc_groups, current_scc):
    scc_dict = {}
    for gid, group in enumerate(scc_groups):
        for nid in group:
            scc_dict[node_map[nid]] = gid
    
    temp_id = len(scc_groups)
    for nid in current_scc:
        scc_dict[node_map[nid]] = temp_id

    visited_nodes = [node_map[i] for i, c in enumerate(colors) if c > 0]
    
    return {
        "visited": visited_nodes,
        "stack": [node_map[i] for i in order_stack],
        "scc_groups": scc_dict, 
        "log": description,
        "active_edges": [],
        "levels": {}, 
        "visit_order": [node_map[i] for i in visit_order],
        "edge_types": {},
        # [수정] SCC에서도 component_count를 전달해야 app.py가 통일된 키로 읽을 수 있음
        "component_count": len(scc_groups)
    }

# View Helpers (생략 - 위와 동일)
def get_adjacency_matrix(nodes, edges, is_directed=False):
    sorted_nodes = _create_mapping_list(nodes)
    n = len(sorted_nodes)
    matrix = [[0] * n for _ in range(n)]
    for u, v in edges:
        u_idx = _binary_search(sorted_nodes, u)
        v_idx = _binary_search(sorted_nodes, v)
        if u_idx != -1 and v_idx != -1:
            matrix[u_idx][v_idx] = 1
            if not is_directed:
                matrix[v_idx][u_idx] = 1
    return sorted_nodes, matrix

def get_adjacency_list_text(nodes, edges, is_directed=False):
    sorted_nodes = _create_mapping_list(nodes)
    n = len(sorted_nodes)
    adj = _build_adj_list_indices_no_dict(n, edges, sorted_nodes, is_directed)
    lines = []
    for i in range(n):
        neighbors = [sorted_nodes[v] for v in adj[i]]
        lines.append(f"{sorted_nodes[i]} -> {neighbors}")
    return "\n".join(lines)
