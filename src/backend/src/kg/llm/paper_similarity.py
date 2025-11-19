from typing import List, Tuple
from langchain.schema import Document

VIS_QUERY = """
    MATCH (p:Paper)
    WHERE p.abstract IS NOT NULL
    AND p.abstract <> ''
    AND p.abstract_embedding IS NOT NULL
    AND size(p.abstract_embedding) > 0
    WITH p, vector.similarity.cosine(p.abstract_embedding, $embedding) AS score
    ORDER BY score DESC
    LIMIT $k
    RETURN
    p.abstract           AS text,
    score                AS score,
    p.abstract_embedding AS embedding,
    p.citation_count     AS citation_count,
    p.publication_date   AS publication_date,
    p.paper_id           AS paper_id
"""


class Neo4jPaperVectorStore:
    def __init__(self, kg, embedder):
        self.kg = kg
        self.embedder = embedder

    def similarity_search_with_score(self, query: str, k: int = 10) -> List[Tuple[Document, float]]:
        embedding = self.embedder.embed_query(query)
        rows = self.kg.query(VIS_QUERY, {"embedding": embedding, "k": k})
        results: List[Tuple[Document, float]] = []
        for row in rows:
            metadata = {
                "paper_id": row["paper_id"],
                "citation_count": row["citation_count"],
                "publication_date": row["publication_date"],
                "abstract_embedding": row["embedding"],
            }
            doc = Document(page_content=row["text"], metadata=metadata)
            results.append((doc, row["score"]))

        return results
