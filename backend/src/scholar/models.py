from typing import List, Optional, Any, Dict
from dataclasses import dataclass, field

@dataclass
class ScholarAuthor:
    author_id: str
    url: str
    name: str
    affiliations: Optional[List[str]]
    homepage: Optional[str]
    paper_count: Optional[int]
    citation_count: Optional[int]
    h_index: Optional[int]

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            author_id=data.get("authorId"),
            url=data.get("url", ""),
            name=data.get("name", "Unknown Author"),
            affiliations=data.get("affiliations", []),
            homepage=data.get("homepage"),
            paper_count=data.get("paperCount", 0),
            citation_count=data.get("citationCount", 0),
            h_index=data.get("hIndex", 0),
        )

    @classmethod
    def from_list(cls, data: List[dict]):
        return [cls.from_dict(item) for item in data]

@dataclass
class ScholarPaper:
    paper_id: str
    url: str
    title: str
    abstract: Optional[str]
    venue: Optional[str]
    publication_venue: Optional[Dict[str, Any]]
    year: Optional[int]
    reference_count: Optional[int]
    citation_count: int
    influential_citation_count: Optional[int]
    fields_of_study: List[str]
    publication_types: List[str]
    publication_date: str
    journal: Optional[Dict[str, Any]]
    authors: List["ScholarAuthor"] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict):
        authors = [ScholarAuthor.from_dict(author) for author in data.get("authors", [])]
        return cls(
            paper_id=data.get("paperId") or data.get("id") or "",
            url=data.get("url", ""),
            title=data.get("title", ""),
            abstract=data.get("abstract", ""),
            venue=data.get("venue"),
            publication_venue=data.get("publicationVenue", {}),
            year=data.get("year"),
            reference_count=data.get("referenceCount", 0),
            citation_count=data.get("citationCount", 0),
            influential_citation_count=data.get("influentialCitationCount", 0),
            fields_of_study=data.get("fieldsOfStudy", []),
            publication_types=data.get("publicationTypes", []),
            publication_date=data.get("publicationDate", ""),
            journal=data.get("journal", {}),
            authors=authors
        )
    
    @classmethod
    def from_list(cls, data: List[dict]):
        return [cls.from_dict(item) for item in data]
