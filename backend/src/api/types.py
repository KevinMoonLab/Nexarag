from dataclasses import dataclass

@dataclass
class BibTexPaper:
    title: str
    author: str
    journal: str
    year: int

@dataclass
class BibTexRequest:
    bibtex: str