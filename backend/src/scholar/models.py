from dataclasses import dataclass, field
from typing import List, Optional
from dataclasses_json import dataclass_json
from marshmallow import EXCLUDE

@dataclass_json(undefined=EXCLUDE)
@dataclass
class PartialAuthor:
    name: str
    author_id: Optional[str] = None

@dataclass_json(undefined=EXCLUDE)
@dataclass
class Author:
    author_id: str
    name: str
    url: Optional[str] = None
    affiliations: Optional[List[str]] = field(default_factory=list)
    homepage: Optional[str] = None
    paperCount: Optional[int] = 0
    citationCount: Optional[int] = 0
    hIndex: Optional[int] = 0

@dataclass_json(undefined=EXCLUDE)
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

@dataclass_json(undefined=EXCLUDE)
@dataclass
class Journal:
    name: Optional[str] = None
    pages: Optional[str] = None
    volume: Optional[str] = None

@dataclass_json(undefined=EXCLUDE)
@dataclass
class PartialPaper:
    id: str
    authorsYear: Optional[str] = None
    title: Optional[str] = None

@dataclass_json(undefined=EXCLUDE)
@dataclass
class PaperRelevanceResult:
    paper_id: str
    title: str
    authors: List[PartialAuthor] = field(default_factory=list)
    year: Optional[int] = None


@dataclass_json(undefined=EXCLUDE)
@dataclass
class Citation:
    paper_id: str
    title: str

@dataclass_json(undefined=EXCLUDE)
@dataclass
class Paper:
    paper_id: str
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