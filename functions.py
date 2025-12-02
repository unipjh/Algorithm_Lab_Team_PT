from collections import deque

# ============================================================
# [PM's Note] Bridge Layer (No Dictionary Version)
# UI(String)와 Algo(Integer) 간의 데이터 변환을 담당합니다.
# 과제 제약사항(No dict/set) 준수를 위해 '이진 탐색'을 사용합니다.
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
    """
    노드명을 정렬된 리스트로 변환 (Index가 곧 정수 ID가 됨)
    Returns: ['A', 'B', 'C', ...] (이 리스트 자체가 int_to_str 역할)
    """
    # 입력이 set일 수 있으므로 list로 변환 후 정렬
    return sorted(list(nodes))

def _build_adj_list_indices_no_dict(n, edges, sorted_nodes, is_directed):
    """
    [핵심 자료구조] 딕셔너리 없이 리스트와 이진 탐색만으로 인접 리스트 구축
    """
    adj = [[] for _ in range(n)]
    
    for u, v in edges:
        # 딕셔너리 참조(O(1)) 대신 이진 탐색(O(log N)) 사용
        u_idx = _binary_search(sorted_nodes, u)
        v_idx = _binary_search(sorted_nodes, v)
        
        if u_idx != -1 and v_idx != -1:
            adj[u_idx].append(v_idx)
            if not is_directed:
                adj[v_idx].append(u_idx)
    
    # 순서 일관성을 위해 내부 정렬
    for neighbors in adj:
        neighbors.sort()
    return adj

# ============================================================
# 1. BFS Implementation (List/Array + Binary Search Based)
# ============================================================
def run_bfs_simulation(nodes, edges, start_node, is_directed=False):
    # 1. Mapping (List Only)
    sorted_nodes_map = _create_mapping_list(nodes) # ['A', 'B', ...]
    n = len(sorted_nodes_map)
    
    # 이진 탐색으로 시작 노드 인덱스 찾기
    start_idx = _binary_search(sorted_nodes_map, start_node)
    
    # 그래프 구축
    adj = _build_adj_list_indices_no_dict(n, edges, sorted_nodes_map, is_directed)

    # 2. State Arrays
    visited = [False] * n
    levels = [-1] * n
    queue = deque()

    # 3. Simulation Storage
    steps = []
    comp_count = 0
    global_visit_order = [] 

    # [Outer Loop] Disconnected Components
    # start_idx를 맨 앞으로, 나머지는 순서대로
    search_sequence = []
    if start_idx != -1:
        search_sequence.append(start_idx)
    for i in range(n):
        if i != start_idx:
            search_sequence.append(i)

    for root in search_sequence:
        if visited[root]: continue
        
        comp_count += 1
        visited[root] = True
        levels[root] = 0
        queue.append(root)

        # Snapshot: Start
        # sorted_nodes_map 자체가 int -> str 변환기 역할을 함 (O(1) Access)
        steps.append(_make_snapshot(sorted_nodes_map, visited, global_visit_order, list(queue), [], levels, [], comp_count, 
                                    f"🚀 컴포넌트 #{comp_count} 시작 (Root: {sorted_nodes_map[root]})"))

        while queue:
            curr = queue.popleft()
            
            if curr not in global_visit_order: global_visit_order.append(curr)
            
            # Snapshot: Visit
            steps.append(_make_snapshot(sorted_nodes_map, visited, global_visit_order, list(queue), [], levels, [], comp_count,
                                        f"📍 방문: {sorted_nodes_map[curr]} (L{levels[curr]})"))

            for neighbor in adj[curr]:
                if not visited[neighbor]:
                    visited[neighbor] = True
                    levels[neighbor] = levels[curr] + 1
                    queue.append(neighbor)
                    
                    # Snapshot: Enqueue
                    steps.append(_make_snapshot(sorted_nodes_map, visited, global_visit_order, list(queue), [(curr, neighbor)], levels, [], comp_count,
                                                f"  🔎 발견: {sorted_nodes_map[neighbor]} -> Queue"))

    # Final Snapshot
    steps.append(_make_snapshot(sorted_nodes_map, visited, global_visit_order, [], [], levels, [], comp_count, "✅ BFS 탐색 종료"))
    return steps

# ============================================================
# 2. DFS Implementation (List/Array + Binary Search Based)
# ============================================================
def run_dfs_simulation(nodes, edges, start_node, is_directed=False):
    # 1. Mapping
    sorted_nodes_map = _create_mapping_list(nodes)
    n = len(sorted_nodes_map)
    start_idx = _binary_search(sorted_nodes_map, start_node)
    adj = _build_adj_list_indices_no_dict(n, edges, sorted_nodes_map, is_directed)

    # 2. State Arrays
    colors = [0] * n 
    depths = [-1] * n
    
    # 3. Simulation Storage
    steps = []
    comp_count = 0
    global_visit_order = []
    # Edge Types: 딕셔너리 대신 리스트에 튜플로 저장 [((u_str, v_str), type), ...]
    # 검색 효율은 떨어지지만 과제 제약상 List 사용
    edge_types_list = [] 

    search_sequence = []
    if start_idx != -1:
        search_sequence.append(start_idx)
    for i in range(n):
        if i != start_idx:
            search_sequence.append(i)

    for root in search_sequence:
        if colors[root] != 0: continue
        
        comp_count += 1
        stack = [[root, 0, 0]]
        
        colors[root] = 1 
        global_visit_order.append(root)
        depths[root] = 0

        steps.append(_make_snapshot_dfs(sorted_nodes_map, colors, global_visit_order, stack, [], depths, edge_types_list, comp_count,
                                        f"🚀 컴포넌트 #{comp_count} 시작 (Root: {sorted_nodes_map[root]})"))

        while stack:
            u, iter_idx, d = stack[-1]
            neighbors = adj[u]

            if iter_idx < len(neighbors):
                v = neighbors[iter_idx]
                stack[-1][1] += 1
                
                # Edge Key (String Tuple)
                u_str, v_str = sorted_nodes_map[u], sorted_nodes_map[v]
                if not is_directed:
                    # 문자열 비교로 정렬
                    ekey = (u_str, v_str) if u_str < v_str else (v_str, u_str)
                else:
                    ekey = (u_str, v_str)

                # Edge Type Check Helper (Linear Search in List)
                existing_type = None
                for k, t in edge_types_list:
                    if k == ekey:
                        existing_type = t
                        break

                if colors[v] == 0: # Tree Edge
                    edge_types_list.append((ekey, "tree"))
                    colors[v] = 1 
                    depths[v] = d + 1
                    global_visit_order.append(v)
                    stack.append([v, 0, d + 1])
                    
                    steps.append(_make_snapshot_dfs(sorted_nodes_map, colors, global_visit_order, stack, [(u, v)], depths, edge_types_list, comp_count,
                                                    f"  Tree Edge: {u_str}->{v_str}"))
                
                elif colors[v] == 1: # Back Edge
                    is_direct_parent = False
                    if not is_directed and len(stack) >= 2 and stack[-2][0] == v:
                        is_direct_parent = True
                    
                    if not is_direct_parent and existing_type is None:
                        edge_types_list.append((ekey, "back"))
                        steps.append(_make_snapshot_dfs(sorted_nodes_map, colors, global_visit_order, stack, [(u, v)], depths, edge_types_list, comp_count,
                                                        f"  🔄 Back Edge: {u_str}->{v_str}"))

                elif colors[v] == 2: # Cross/Forward
                    if is_directed and existing_type is None:
                        edge_types_list.append((ekey, "cross"))
                        steps.append(_make_snapshot_dfs(sorted_nodes_map, colors, global_visit_order, stack, [(u, v)], depths, edge_types_list, comp_count,
                                                        f"  Cross/Forward: {u_str}->{v_str}"))
            else:
                stack.pop()
                colors[u] = 2
                steps.append(_make_snapshot_dfs(sorted_nodes_map, colors, global_visit_order, stack, [], depths, edge_types_list, comp_count,
                                                f"🔙 백트래킹: {sorted_nodes_map[u]} 완료"))

    steps.append(_make_snapshot_dfs(sorted_nodes_map, colors, global_visit_order, [], [], depths, edge_types_list, comp_count, "✅ DFS 탐색 종료"))
    return steps


# ============================================================
# 3. Snapshot Helpers (Int State -> UI Dict State)
# [Note] UI로 보낼 때는 dict 변환 허용 (최종 산출물이므로)
# ============================================================
def _make_snapshot(node_map, visited_arr, order_indices, queue_indices, active_tuple_list, levels_arr, edge_types_list, comp_cnt, log):
    # edge_types_list: [((u,v), type), ...] -> dict로 변환하여 UI 전달
    edge_types_dict = {}
    if isinstance(edge_types_list, list):
        for k, t in edge_types_list:
            edge_types_dict[k] = t
            
    return {
        "visited": [node_map[i] for i, v in enumerate(visited_arr) if v],
        "visit_order": [node_map[i] for i in order_indices],
        "queue": [node_map[i] for i in queue_indices],
        "active_edges": [(node_map[u], node_map[v]) for u, v in active_tuple_list],
        "levels": {node_map[i]: l for i, l in enumerate(levels_arr) if l != -1},
        "edge_types": edge_types_dict,
        "component_count": comp_cnt,
        "log": log
    }

def _make_snapshot_dfs(node_map, colors_arr, order_indices, stack_struct, active_tuple_list, depths_arr, edge_types_list, comp_cnt, log):
    edge_types_dict = {}
    if isinstance(edge_types_list, list):
        for k, t in edge_types_list:
            edge_types_dict[k] = t

    return {
        "visited": [node_map[i] for i, c in enumerate(colors_arr) if c > 0],
        "visit_order": [node_map[i] for i in order_indices],
        "stack": [node_map[item[0]] for item in stack_struct],
        "active_edges": [(node_map[u], node_map[v]) for u, v in active_tuple_list],
        "depths": {node_map[i]: d for i, d in enumerate(depths_arr) if d != -1},
        "edge_types": edge_types_dict,
        "component_count": comp_cnt,
        "log": log
    }

# ============================================================
# 4. Data Structure View Helpers
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