# data_manager.py

def parse_edge_list(file_content_str: str):
    """
    Parses raw string content (from text area or file) into nodes and edges.
    Expected Format: "NodeA NodeB" per line.
    """
    edges = []
    nodes = set()
    
    # Use splitlines() to handle different line endings (Windows/Linux) robustly
    lines = file_content_str.strip().splitlines()
    
    for line in lines:
        parts = line.strip().split()
        
        # Ensure at least two parts exist (Source, Target)
        if len(parts) >= 2:
            u, v = parts[0], parts[1]
            
            # Validation: Ignore empty strings
            if u and v:
                edges.append((u, v))
                nodes.add(u)
                nodes.add(v)
                
    # Return sorted nodes for consistent ordering in UI
    return sorted(list(nodes)), edges
