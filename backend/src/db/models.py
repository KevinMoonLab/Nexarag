from neomodel import (
    AsyncStructuredNode, StringProperty, IntegerProperty, UniqueIdProperty,
    JSONProperty, AsyncRelationshipTo, AsyncRelationshipFrom
)

class Author(AsyncStructuredNode):
    author_id = UniqueIdProperty()
    name = StringProperty(required=True)
    url = StringProperty()
    affiliations = JSONProperty(default=[])
    homepage = StringProperty()
    paper_count = IntegerProperty(default=0)
    citation_count = IntegerProperty(default=0)
    h_index = IntegerProperty(default=0)
    
    # Relationships
    papers = AsyncRelationshipTo("Paper", "AUTHORED")


class PublicationVenue(AsyncStructuredNode):
    venue_id = UniqueIdProperty()
    name = StringProperty(required=True)
    type = StringProperty()
    alternate_names = JSONProperty(default=[])
    alternate_issns = JSONProperty(default=[])
    issn = StringProperty()
    url = StringProperty()
    alternate_urls = JSONProperty(default=[])

    # Relationships
    papers = AsyncRelationshipFrom("Paper", "PUBLISHED_AT")


class Journal(AsyncStructuredNode):
    name = UniqueIdProperty()
    pages = StringProperty()
    volume = StringProperty()
    
    # Relationships
    papers = AsyncRelationshipFrom("Paper", "PUBLISHED_IN")

class Paper(AsyncStructuredNode):
    paper_id = UniqueIdProperty()
    title = StringProperty(required=True)
    abstract = StringProperty()
    year = IntegerProperty()
    reference_count = IntegerProperty()
    citation_count = IntegerProperty()
    influential_citation_count = IntegerProperty()
    publication_types = JSONProperty(default=[])
    publication_date = StringProperty()
    
    # Relationships
    references = AsyncRelationshipFrom("Paper", "CITES")
    citations = AsyncRelationshipTo("Paper", "CITES")
    authors = AsyncRelationshipFrom("Author", "AUTHORED")
    journal = AsyncRelationshipTo("Journal", "PUBLISHED_IN")
    publication_venue = AsyncRelationshipTo("PublicationVenue", "PUBLISHED_AT")

class Workspace(AsyncStructuredNode):
    uid = UniqueIdProperty()
    name = StringProperty(unique_index=True, required=True)
    papers = AsyncRelationshipFrom("Paper", "BELONGS_TO")
    authors = AsyncRelationshipFrom("Author", "BELONGS_TO")