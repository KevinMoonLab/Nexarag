import uuid

from api.types import BibTexPaper
from api import util


def test_create_id_returns_valid_unique_uuid_strings():
    first = util.create_id()
    second = util.create_id()

    assert first != second
    assert str(uuid.UUID(first)) == first
    assert str(uuid.UUID(second)) == second


def test_transform_for_cytoscape_deduplicates_nodes_and_preserves_edge_data():
    graph = [
        {
            "n": {"id": "n1", "labels": ["Paper"], "properties": {"title": "A"}},
            "r": {"type": "CITES", "properties": {"weight": 1}},
            "m": {"id": "n2", "labels": ["Paper"], "properties": {"title": "B"}},
        },
        {
            "n": {"id": "n1", "labels": ["Paper"], "properties": {"title": "A"}},
            "r": {"type": "CITES", "properties": {"weight": 2}},
            "m": {"id": "n2", "labels": ["Paper"], "properties": {"title": "B"}},
        },
    ]

    transformed = util.transform_for_cytoscape(graph)

    assert len(transformed["nodes"]) == 2
    assert transformed["edges"] == [
        {"source": "n1", "target": "n2", "type": "CITES", "properties": {"weight": 1}},
        {"source": "n1", "target": "n2", "type": "CITES", "properties": {"weight": 2}},
    ]


def test_transform_for_cytoscape_skips_missing_target_or_relationship():
    graph = [
        {"n": {"id": "n1", "labels": ["Paper"], "properties": {}}},
        {
            "n": {"id": "n2", "labels": ["Paper"], "properties": {}},
            "m": {"id": "n3", "labels": ["Author"], "properties": {}},
        },
    ]

    transformed = util.transform_for_cytoscape(graph)

    assert len(transformed["nodes"]) == 2
    assert transformed["edges"] == []


def test_transform_bibtex_for_cytoscape_builds_paper_nodes(monkeypatch):
    ids = iter(["id-1", "id-2"])
    monkeypatch.setattr(util, "create_id", lambda: next(ids))

    papers = [
        BibTexPaper(title="T1", author="A1", journal="J1", year=2020),
        BibTexPaper(title="T2", author="A2", journal="J2", year=2021),
    ]

    transformed = util.transform_bibtex_for_cytoscape(papers)

    assert transformed == {
        "nodes": [
            {"id": "id-1", "label": "Paper", "properties": {"title": "T1", "year": 2020}},
            {"id": "id-2", "label": "Paper", "properties": {"title": "T2", "year": 2021}},
        ],
        "edges": [],
    }


def test_transform_bibtex_for_cytoscape_handles_empty_input():
    assert util.transform_bibtex_for_cytoscape([]) == {"nodes": [], "edges": []}
