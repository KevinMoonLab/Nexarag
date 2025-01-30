from neomodel import (
    AsyncStructuredNode, StringProperty, IntegerProperty, UniqueIdProperty,
    JSONProperty, AsyncRelationshipTo, AsyncRelationshipFrom
)

class Journal(AsyncStructuredNode):
    uid = UniqueIdProperty()
    name = StringProperty(unique_index=True, required=True)
    pages = StringProperty()
    volume = StringProperty()
    
    papers = AsyncRelationshipFrom("Paper", "PUBLISHED_IN")

    @staticmethod
    def from_dict(data: dict):
        return Journal(
            name=data.get("name", "Unknown Journal"),
            pages=data.get("pages", ""),
            volume=data.get("volume", "")
        )

class Paper(AsyncStructuredNode):
    uid = UniqueIdProperty()
    paper_id = StringProperty(unique_index=True, required=True)
    url = StringProperty()
    title = StringProperty()
    abstract = StringProperty()
    venue = StringProperty()
    publication_venue = JSONProperty() 
    year = IntegerProperty()
    reference_count = IntegerProperty()
    citation_count = IntegerProperty()
    influential_citation_count = IntegerProperty()
    fields_of_study = JSONProperty() 
    publication_types = JSONProperty()
    publication_date = StringProperty()

    authors = AsyncRelationshipFrom("Author", "AUTHORED")
    workspace = AsyncRelationshipFrom("Workspace", "BELONGS_TO")
    journal = AsyncRelationshipTo("Journal", "PUBLISHED_IN")

    @staticmethod
    def from_dict(data: dict):
        paper = Paper(
            paper_id=data.get("paper_id") or data.get("id", ""),
            url=data.get("url", ""),
            title=data.get("title", ""),
            abstract=data.get("abstract", ""),
            venue=data.get("venue"),
            publication_venue=data.get("publication_venue", {}),
            year=data.get("year"),
            reference_count=data.get("reference_count", 0),
            citation_count=data.get("citation_count", 0),
            influential_citation_count=data.get("influential_citation_count", 0),
            fields_of_study=data.get("fields_of_study", []),
            publication_types=data.get("publication_types", []),
            publication_date=data.get("publication_date", ""),
        )

        # Create or get Journal
        if "journal" in data and data["journal"]:
            journal_data = data["journal"]
            journal = Journal.from_dict(journal_data)
            paper.journal.connect(journal)

        return paper



class Author(AsyncStructuredNode):
    uid = UniqueIdProperty()
    author_id = StringProperty(unique_index=True, required=True)
    name = StringProperty(unique_index=True, required=True)
    url = StringProperty()
    affiliations = JSONProperty()
    homepage = StringProperty()
    paper_count = IntegerProperty()
    citation_count = IntegerProperty()
    h_index = IntegerProperty()
    authored = AsyncRelationshipTo("Paper", "AUTHORED")

    @staticmethod
    def from_dict(data: dict):
        return Author(
            author_id=data.get("author_id"),
            name=data.get("name", "Unknown Author"),
            url=data.get("url", ""),
            affiliations=data.get("affiliations", []),
            homepage=data.get("homepage"),
            paper_count=data.get("paper_count", 0),
            citation_count=data.get("citation_count", 0),
            h_index=data.get("h_index", 0)
        )

class Workspace(AsyncStructuredNode):
    uid = UniqueIdProperty()
    name = StringProperty(unique_index=True, required=True)
    papers = AsyncRelationshipFrom("Paper", "BELONGS_TO")
    authors = AsyncRelationshipFrom("Author", "BELONGS_TO")