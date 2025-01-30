def transform_for_cytoscape(data):
    nodes = []
    edges = []
    node_ids = set()

    for entry in data:
        # Source node
        start_node = entry["n"]
        if start_node["id"] not in node_ids:
            nodes.append({
                "id": start_node["id"],
                "label": start_node["labels"][0],
                "properties": start_node["properties"]
            })
            node_ids.add(start_node["id"])

        # Target node
        end_node = entry["m"]
        if end_node["id"] not in node_ids:
            nodes.append({
                "id": end_node["id"],
                "label": end_node["labels"][0],
                "properties": end_node["properties"]
            })
            node_ids.add(end_node["id"])

        # Edge
        relationship = entry["r"]
        edges.append({
            "source": start_node["id"],
            "target": end_node["id"],
            "type": relationship["type"],
            "properties": relationship["properties"]
        })

    return {"nodes": nodes, "edges": edges}