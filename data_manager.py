# data_manager.py
# (데이터 전처리 및 파싱 담당)

def parse_edge_list(file_content_str: str):
    """
    업로드된 파일(.txt)을 파싱하여 노드와 엣지 리스트를 반환합니다.
    Format:
    A B
    A C
    ...
    """
    edges = []
    nodes = set()
    
    # 윈도우/리눅스 개행문자 호환을 위해 splitlines() 사용 권장
    lines = file_content_str.strip().splitlines()
    
    for line in lines:
        parts = line.strip().split()
        if len(parts) >= 2:
            u, v = parts[0], parts[1]
            # 자기 자신으로의 루프나 빈 데이터 방지 로직 추가 가능
            if u and v:
                edges.append((u, v))
                nodes.add(u)
                nodes.add(v)
                
    # 노드 리스트는 정렬하여 반환 (시각적 일관성)
    return sorted(list(nodes)), edges