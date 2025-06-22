import uuid
from .types import BibTexPaper
from typing import List

def create_id():
    return str(uuid.uuid4())

def transform_for_cytoscape(data):
    nodes = []
    edges = []
    node_ids = set()

    for entry in data:
        # Always add source node
        start_node = entry["n"]
        if start_node["id"] not in node_ids:
            nodes.append({
                "id": start_node["id"],
                "label": start_node["labels"][0],
                "properties": start_node["properties"]
            })
            node_ids.add(start_node["id"])

        # Only add target and edge if they exist (not null)
        if entry.get("m") and entry.get("r"):
            end_node = entry["m"]
            if end_node["id"] not in node_ids:
                nodes.append({
                    "id": end_node["id"],
                    "label": end_node["labels"][0],
                    "properties": end_node["properties"]
                })
                node_ids.add(end_node["id"])

            relationship = entry["r"]
            edges.append({
                "source": start_node["id"],
                "target": end_node["id"],
                "type": relationship["type"],
                "properties": relationship["properties"]
            })

    return {"nodes": nodes, "edges": edges}

def transform_bibtex_for_cytoscape(data: List[BibTexPaper]):
    nodes = []

    for entry in data:
        node_id = create_id()
        nodes.append({
            "id": node_id,
            "label": 'Paper',
            "properties": {
                "title": entry.title,
                "year": entry.year
            }
        })

    return { "nodes": nodes, "edges": [] }