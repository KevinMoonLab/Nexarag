from pydantic import BaseModel, Field
from typing import List, Dict, Any, Set
from .persistence import Author

class NodeModel(BaseModel):
    uid: str = Field(..., title="Unique Id")
    labels: List[str] = Field(..., title="Node Labels")
    properties: Dict[str, Any] = Field(..., title="Node Properties")

class EdgeModel(BaseModel):
    start: str = Field(..., title="Source Id")
    end: str = Field(..., title="Target Id")
    type: str = Field(..., title="Relationship Type")
    properties: Dict[str, Any] = Field({}, title="Relationship Properties")

class GraphModel(BaseModel):
    nodes: List[NodeModel] = Field([], title="Nodes in Graph")
    edges: List[EdgeModel] = Field([], title="Edges in Graph")
    _node_set: Set[str] = set()
    _edge_set: Set[str] = set()

    def add_node(self, node: NodeModel):
        if node.uid not in self._node_set:
            self.nodes.append(node)
            self._node_set.add(node.uid)

    def add_nodes(self, nodes: List[NodeModel]):
        for node in nodes:
            self.add_node(node)

    def add_edge(self, edge: EdgeModel):
        edge_key = (edge.start, edge.end, edge.type)
        if edge_key not in self._edge_set:
            self.edges.append(edge)
            self._edge_set.add(edge_key)

    def add_edges(self, edges: List[EdgeModel]):
        for edge in edges:
            self.add_edge(edge)

class GraphDomain:
    @staticmethod
    def to_node(persistent_node):
        return NodeModel(
            uid=persistent_node.uid,
            labels=[persistent_node.__class__.__name__],
            properties={k: v for k, v in persistent_node.__properties__.items()}
        )

    @staticmethod
    def to_edge(start, end, rel, rel_type):
        return EdgeModel(
            start=start.uid,
            end=end.uid,
            type=rel_type,
            properties={k: v for k, v in rel.__properties__.items()}
        )
    
class KnowledgeGraph():
    async def get_authors()->list[Author]:
        authors = await Author.nodes.all()
        results = []
        for author in authors:
            papers = await author.authored.all()
            results.append(Author.from_dict({
                "author": author.name,
                "papers": [paper.title for paper in papers]
            }))
        return results