# functions.py
from collections import deque

# ============================================================
# [Common Helper] UI(String) <-> Algo(Integer)
# ============================================================

def _binary_search(sorted_arr, target):
    """
    [Core Algorithm] 문자열 리스트에서 target의 인덱스를 O(log N)으로 찾음
    딕셔너리(Hash) 대신 사용하여 과제 제약을 준수함.
    """
    left, right = 0, len(sorted_arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if sorted_arr[mid] == target:
            return mid
        elif sorted_arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1  # Not found

def _create_mapping_list(nodes):
    """노드명 리스트 정렬 및 중복 제거"""
    unique_nodes = []
    for node in nodes:
        exists = False
        for n in unique_nodes:
            if n == node:
                exists = True
                break
        if not exists:
            unique_nodes.append(node)
    
    # Selection Sort
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
    """
    리스트와 이진 탐색만으로 인접 리스트 구축
    reverse=True일 경우 역방향 그래프(Transpose Graph) 생성 (SCC용)
    """
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
    
    # 정렬 (Selection Sort) for deterministic behavior
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
# 1. BFS Implementation (Queue 명시)
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

        # [Fix] algo_style="BFS" 추가
        steps.append(_make_snapshot_bfs_dfs(sorted_nodes_map, visited, global_visit_order, list(queue), [], levels, {}, comp_count, 
                                    f"🚀 컴포넌트 #{comp_count} 시작 (Root: {sorted_nodes_map[root]})", algo_style="BFS"))

        while queue:
            curr = queue.popleft()
            if curr not in global_visit_order: global_visit_order.append(curr)
            
            steps.append(_make_snapshot_bfs_dfs(sorted_nodes_map, visited, global_visit_order, list(queue), [], levels, {}, comp_count,
                                        f"📍 방문: {sorted_nodes_map[curr]} (L{levels[curr]})", algo_style="BFS"))

            for neighbor in adj[curr]:
                if not visited[neighbor]:
                    visited[neighbor] = True
                    levels[neighbor] = levels[curr] + 1
                    queue.append(neighbor)
                    steps.append(_make_snapshot_bfs_dfs(sorted_nodes_map, visited, global_visit_order, list(queue), [(curr, neighbor)], levels, {}, comp_count,
                                                f"  🔎 발견: {sorted_nodes_map[neighbor]} -> Queue", algo_style="BFS"))
    
    steps.append(_make_snapshot_bfs_dfs(sorted_nodes_map, visited, global_visit_order, [], [], levels, {}, comp_count, "✅ BFS 탐색 종료", algo_style="BFS"))
    return steps

# ============================================================
# 2. DFS Implementation (Stack 명시)
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
        
        # [Fix] algo_style="DFS" 추가
        steps.append(_make_snapshot_bfs_dfs(sorted_nodes_map, colors, global_visit_order, stack, [], depths, edge_types_list, comp_count,
                                        f"🚀 컴포넌트 #{comp_count} 시작 (Root: {sorted_nodes_map[root]})", algo_style="DFS"))

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

                if colors[v] == 0: # Tree Edge
                    edge_types_list.append((ekey, "tree"))
                    colors[v] = 1 
                    depths[v] = d + 1
                    global_visit_order.append(v)
                    stack.append([v, 0, d + 1])
                    steps.append(_make_snapshot_bfs_dfs(sorted_nodes_map, colors, global_visit_order, stack, [(u, v)], depths, edge_types_list, comp_count,
                                                    f"  Tree Edge: {u_str}->{v_str}", algo_style="DFS"))
                elif colors[v] == 1: # Back Edge
                    is_parent = (not is_directed and len(stack) >= 2 and stack[-2][0] == v)
                    if not is_parent and existing_type is None:
                        edge_types_list.append((ekey, "back"))
                        steps.append(_make_snapshot_bfs_dfs(sorted_nodes_map, colors, global_visit_order, stack, [(u, v)], depths, edge_types_list, comp_count,
                                                        f"  🔄 Back Edge: {u_str}->{v_str}", algo_style="DFS"))
                elif colors[v] == 2: # Cross/Forward
                    if is_directed and existing_type is None:
                        edge_types_list.append((ekey, "cross"))
                        steps.append(_make_snapshot_bfs_dfs(sorted_nodes_map, colors, global_visit_order, stack, [(u, v)], depths, edge_types_list, comp_count,
                                                        f"  Cross/Forward: {u_str}->{v_str}", algo_style="DFS"))
            else:
                stack.pop()
                colors[u] = 2
                steps.append(_make_snapshot_bfs_dfs(sorted_nodes_map, colors, global_visit_order, stack, [], depths, edge_types_list, comp_count,
                                                f"🔙 백트래킹: {sorted_nodes_map[u]} 완료", algo_style="DFS"))

    steps.append(_make_snapshot_bfs_dfs(sorted_nodes_map, colors, global_visit_order, [], [], depths, edge_types_list, comp_count, "✅ DFS 탐색 종료", algo_style="DFS"))
    return steps

# ======================================================================
# 3. Topological Sort Simulation (DFS + finishing time + pop based)
# ======================================================================
def run_topological_sort_simulation(nodes, edges, is_directed=True):
    # 1) 매핑 및 인접 리스트 생성
    node_map = _create_mapping_list(nodes)
    n = len(node_map)
    adj = _build_adj_list_indices_no_dict(n, edges, node_map, is_directed)

    visited = [0] * n  # 0:미방문, 1:방문중, 2:완료
    stack = []         # finishing time push
    steps = []         # UI snapshot
    global_visit_order = [] 
    comp_count = 0     

    # 전체 노드를 0..n-1 순서로 탐색
    for root in range(n):
        if visited[root] != 0: continue

        comp_count += 1
        
        # 스냅샷: 컴포넌트 시작
        steps.append(_make_snapshot_topo(
            node_map, visited, global_visit_order, stack, None, comp_count,
            f"🚀 Component #{comp_count} 시작 (Root: {node_map[root]})"
        ))

        # --- DFS (Recursive Closure) ---
        try:
            def dfs(u):
                visited[u] = 1 # Gray
                global_visit_order.append(u)
                steps.append(_make_snapshot_topo(
                    node_map, visited, global_visit_order, stack, None, comp_count,
                    f"➡ Visit {node_map[u]}"
                ))

                for v in adj[u]:
                    if visited[v] == 0:
                        dfs(v)
                    elif visited[v] == 1:
                        # Cycle Detected
                        steps.append(_make_snapshot_topo(
                            node_map, visited, global_visit_order, stack, (u, v), comp_count,
                            f"❌ Cycle 발견: {node_map[u]} → {node_map[v]}"
                        ))
                        raise ValueError("CYCLE")

                visited[u] = 2 # Black
                stack.append(u) # Finishing time push
                steps.append(_make_snapshot_topo(
                    node_map, visited, global_visit_order, stack, None, comp_count,
                    f"📌 Finishing: {node_map[u]} push"
                ))

            dfs(root)

        except ValueError:
            steps.append(_make_snapshot_topo(
                node_map, visited, global_visit_order, stack, None, comp_count,
                "⛔ 사이클로 인해 Topological Sort 불가능"
            ))
            return steps # Return steps immediately on error

    # --- 스택 pop으로 ordering 생성 (UI Visualization)
    ordering = []
    # 시각화를 위해 스택을 복사해서 하나씩 팝하는 척 연출
    temp_stack = list(stack)
    
    steps.append(_make_snapshot_topo(
        node_map, visited, global_visit_order, stack, None, comp_count,
        "🔄 DFS 종료. 스택에서 Pop하여 정렬 순서 생성 시작"
    ))

    while temp_stack:
        node_idx = temp_stack.pop()
        ordering.append(node_idx)
        # UI에 보여줄 때는, 현재까지 팝 된 순서를 visit_order 자리에 대신 보여주거나 별도 처리가능
        # 여기서는 Topo Sort 결과를 강조하기 위해 log에 기록
        steps.append(_make_snapshot_topo(
            node_map, visited, ordering, temp_stack, None, comp_count,
            f"🔽 Pop: {node_map[node_idx]} (Rank {len(ordering)})"
        ))

    steps.append(_make_snapshot_topo(
        node_map, visited, ordering, [], None, comp_count,
        "✅ 위상 정렬 완료"
    ))

    return steps

# ============================================================
# 4. SCC (Kosaraju) + UI Simulation
# ============================================================
def run_scc_kosaraju_ui(nodes, edges, is_directed=True):
    steps = []
    node_map = _create_mapping_list(nodes)
    n = len(node_map)

    # 정방향 & 역방향 인접 리스트
    adj  = _build_adj_list_indices_no_dict(n, edges, node_map, is_directed, reverse=False)
    radj = _build_adj_list_indices_no_dict(n, edges, node_map, is_directed, reverse=True)

    # --- Phase 1: DFS to fill stack ---
    colors = [0] * n
    visit_order = []
    order_stack = []

    def dfs1(u):
        colors[u] = 1
        visit_order.append(u)
        steps.append(_make_snapshot_scc(
            phase=1, description=f"➡ DFS1 방문: {node_map[u]}",
            node_map=node_map, colors=colors, visit_order=visit_order,
            order_stack=order_stack, scc_groups=[], current_scc=[]
        ))

        for v in adj[u]:
            if colors[v] == 0:
                dfs1(v)

        colors[u] = 2
        order_stack.append(u)
        steps.append(_make_snapshot_scc(
            phase=1, description=f"⬆ 완료(push): {node_map[u]}",
            node_map=node_map, colors=colors, visit_order=visit_order,
            order_stack=order_stack, scc_groups=[], current_scc=[]
        ))

    for i in range(n):
        if colors[i] == 0:
            dfs1(i)

    # --- Phase 2: DFS on Transpose Graph ---
    colors = [0] * n # Reset colors for Phase 2
    scc_groups = []  # List of List [[idx, idx], [idx]]

    def dfs2(u, current_scc):
        colors[u] = 1
        current_scc.append(u)
        steps.append(_make_snapshot_scc(
            phase=2, description=f"➡ DFS2(역방향) 방문: {node_map[u]}",
            node_map=node_map, colors=colors, visit_order=visit_order,
            order_stack=order_stack, scc_groups=scc_groups, current_scc=current_scc
        ))

        for v in radj[u]:
            if colors[v] == 0:
                dfs2(v, current_scc)
        colors[u] = 2

    steps.append(_make_snapshot_scc(
        phase=2, description="🔄 Phase 2: 스택 Pop & 역방향 DFS 시작",
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
            phase=2, description=f"📦 SCC 발견 #{len(scc_groups)}: {[node_map[x] for x in new_scc]}",
            node_map=node_map, colors=colors, visit_order=visit_order,
            order_stack=order_stack, scc_groups=scc_groups, current_scc=new_scc
        ))

    steps.append(_make_snapshot_scc(
        phase=2, description="🏁 SCC 탐색 종료",
        node_map=node_map, colors=colors, visit_order=visit_order,
        order_stack=order_stack, scc_groups=scc_groups, current_scc=[]
    ))

    return steps

# ============================================================
# Snapshot Helpers (Updated)
# ============================================================
def _make_snapshot_bfs_dfs(node_map, visited_arr, order_indices, structure_list, active_tuple_list, levels_arr, edge_types_list, comp_cnt, log, algo_style="BFS"):
    # Edge Types List -> Dict 변환
    edge_types_dict = {}
    if isinstance(edge_types_list, list):
        for k, t in edge_types_list:
            edge_types_dict[k] = t
    
    # 구조체(큐/스택) 내부 데이터 평탄화 (Flat List)
    flat_structure = []
    for item in structure_list:
        if isinstance(item, list): # DFS stack [node, idx, depth]
            flat_structure.append(node_map[item[0]])
        else: # BFS queue or simple list
            flat_structure.append(node_map[item])

    # [핵심 수정] algo_style에 따라 'queue' 혹은 'stack' 키 중 하나만 포함시켜야 함
    snapshot = {
        "visited": [node_map[i] for i, v in enumerate(visited_arr) if v and (isinstance(v, bool) or v > 0)],
        "visit_order": [node_map[i] for i in order_indices],
        "active_edges": [(node_map[u], node_map[v]) for u, v in active_tuple_list],
        "levels": {node_map[i]: l for i, l in enumerate(levels_arr) if l != -1},
        "edge_types": edge_types_dict,
        "component_count": comp_cnt,
        "log": log
    }

    # 키(Key)가 존재하느냐 마느냐로 app.py가 UI를 결정하므로, 선택적으로 키를 추가합니다.
    if algo_style == "BFS":
        snapshot["queue"] = flat_structure
    else:
        snapshot["stack"] = flat_structure

    return snapshot

def _make_snapshot_topo(node_map, colors, visit_order, stack, edge, comp_count, message):
    # Topo Sort 스냅샷 -> app.py 호환 변환
    visited_nodes = [node_map[i] for i, c in enumerate(colors) if c > 0]
    stack_nodes = [node_map[i] for i in stack]
    active_e = []
    if edge:
        active_e.append((node_map[edge[0]], node_map[edge[1]]))
    
    # visit_order가 정수 리스트이므로 변환
    visit_order_str = [node_map[i] for i in visit_order]

    return {
        "visited": visited_nodes,
        "visit_order": visit_order_str, # 정렬 결과 혹은 방문 순서
        "stack": stack_nodes,
        "active_edges": active_e,
        "log": message,
        "component_count": comp_count,
        "levels": {}, # Topo에서는 레벨 표시 생략 가능
        "edge_types": {}
    }

def _make_snapshot_scc(phase, description, node_map, colors, visit_order, order_stack, scc_groups, current_scc):
    # SCC 스냅샷 -> app.py 호환 변환
    # scc_groups (List[List[int]]) -> dict {node_str: group_id}
    scc_dict = {}
    for gid, group in enumerate(scc_groups):
        for nid in group:
            scc_dict[node_map[nid]] = gid
    
    # 현재 형성 중인 SCC는 임시 ID 부여 (시각화 구분용)
    temp_id = len(scc_groups)
    for nid in current_scc:
        scc_dict[node_map[nid]] = temp_id

    # UI에서는 colors 배열을 visited로 인식
    visited_nodes = [node_map[i] for i, c in enumerate(colors) if c > 0]
    
    return {
        "visited": visited_nodes,
        "stack": [node_map[i] for i in order_stack],
        "scc_groups": scc_dict, # app.py에서 색상 처리에 사용
        "log": description,
        "active_edges": [],
        "levels": {}, # Kosaraju에서는 Low-link 사용 안함
        "visit_order": [node_map[i] for i in visit_order],
        "edge_types": {}
    }

# ============================================================
# View Helpers
# ============================================================
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
