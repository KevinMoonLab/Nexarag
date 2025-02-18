from dataclasses import dataclass, field
from typing import List, Optional
from dataclasses_json import dataclass_json

@dataclass_json
@dataclass
class PartialAuthor:
    name: str
    authorId: Optional[str] = None

@dataclass_json
@dataclass
class Author:
    authorId: str
    name: str
    url: Optional[str] = None
    affiliations: Optional[List[str]] = field(default_factory=list)
    homepage: Optional[str] = None
    paperCount: Optional[int] = 0
    citationCount: Optional[int] = 0
    hIndex: Optional[int] = 0

@dataclass_json
@dataclass
class PublicationVenue:
    id: str
    name: str
    type: Optional[str] = None
    alternate_names: Optional[List[str]] = field(default_factory=list)
    issn: Optional[str] = None
    alternate_issns: Optional[List[str]] = field(default_factory=list) 
    url: Optional[str] = None
    alternate_urls: Optional[List[str]] = field(default_factory=list)

@dataclass_json
@dataclass
class Journal:
    name: Optional[str] = None
    pages: Optional[str] = None
    volume: Optional[str] = None

@dataclass_json
@dataclass
class PartialPaper:
    id: str
    authorsYear: Optional[str] = None
    title: Optional[str] = None

@dataclass_json
@dataclass
class PaperRelevanceResult:
    paperId: str
    title: str
    authors: List[PartialAuthor] = field(default_factory=list)
    year: Optional[int] = None


@dataclass_json
@dataclass
class Citation:
    paperId: str
    title: str

@dataclass_json
@dataclass
class Paper:
    paperId: str
    title: str
    venue: str
    referenceCount: int
    citationCount: int
    influentialCitationCount: int
    abstract: Optional[str]
    year: Optional[int] = None
    publicationTypes: Optional[List[str]] = field(default_factory=list)
    publicationDate: Optional[str] = None
    journal: Optional[Journal] = None
    publicationVenue: Optional[PublicationVenue] = None
    authors: List[PartialAuthor] = field(default_factory=list)