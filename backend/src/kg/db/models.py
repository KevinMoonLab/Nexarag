from neomodel import (
    AsyncStructuredNode, StringProperty, IntegerProperty, UniqueIdProperty,
    JSONProperty, AsyncRelationshipTo, AsyncRelationshipFrom, ZeroOrOne, ZeroOrMore,
    ArrayProperty, FloatProperty, VectorIndex
)

class Author(AsyncStructuredNode):
    uid = UniqueIdProperty()
    author_id = StringProperty(unique_index=True, required=True)
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
    uid = UniqueIdProperty()
    venue_id = StringProperty(unique_index=True, required=True)
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

class Tag(AsyncStructuredNode):
    uid = UniqueIdProperty()
    name = StringProperty(unique_index=True, required=True)
    
    # Relationships
    papers = AsyncRelationshipFrom("Paper", "TAGGED_WITH")
    documents = AsyncRelationshipFrom("Document", "TAGGED_WITH")

class Paper(AsyncStructuredNode):
    uid = UniqueIdProperty()
    paper_id = StringProperty(unique_index=True, required=True)
    title = StringProperty(required=True)
    abstract = StringProperty()
    year = IntegerProperty()
    reference_count = IntegerProperty()
    citation_count = IntegerProperty()
    influential_citation_count = IntegerProperty()
    publication_types = JSONProperty(default=[])
    publication_date = StringProperty()
    abstract_embedding = ArrayProperty(
        FloatProperty(),
        vector_index=VectorIndex(dimensions=768, similarity_function='cosine')
    )
    
    # Relationships
    references = AsyncRelationshipFrom("Paper", "CITES")
    citations = AsyncRelationshipTo("Paper", "CITES")
    authors = AsyncRelationshipFrom("Author", "AUTHORED")
    journal = AsyncRelationshipTo("Journal", "PUBLISHED_IN")
    publication_venue = AsyncRelationshipTo("PublicationVenue", "PUBLISHED_AT")
    documents = AsyncRelationshipTo("Document", "BELONGS_TO")
    tags = AsyncRelationshipTo("Tag", "TAGGED_WITH", cardinality=ZeroOrMore)

class Document(AsyncStructuredNode):
    uid = UniqueIdProperty()
    document_id = StringProperty(unique_index=True, required=True)
    path = StringProperty()
    name = StringProperty()
    og_path = StringProperty()
    paper = AsyncRelationshipFrom("Paper", "BELONGS_TO", cardinality=ZeroOrOne)
    tags = AsyncRelationshipTo("Tag", "TAGGED_WITH", cardinality=ZeroOrMore)

class Chat(AsyncStructuredNode):
    chat_id = UniqueIdProperty()
    messages = AsyncRelationshipTo("ChatMessage", "BELONGS_TO")
    
class ChatMessage(AsyncStructuredNode):
    message_id = UniqueIdProperty()
    message = StringProperty()
    response = AsyncRelationshipFrom("ChatResponse", "RESPONSE_TO")

class ChatResponse(AsyncStructuredNode):
    response_id = UniqueIdProperty()
    message = StringProperty()
    response_to = AsyncRelationshipTo("ChatMessage", "RESPONSE_TO")

class Chunk(AsyncStructuredNode):
    uid = UniqueIdProperty()
    chunkId = StringProperty(unique_index=True, required=True)
    paper_id = StringProperty()
    source = StringProperty()
    text = StringProperty()
    textEmbedding = ArrayProperty(
        FloatProperty(),
        vector_index=VectorIndex(dimensions=768, similarity_function='cosine')
    )
    
    # Relationships
    paper = AsyncRelationshipTo("Paper", "BELONGS_TO_PAPER")
    project = AsyncRelationshipTo("Project", "BELONGS_TO")
    next_chunk = AsyncRelationshipTo("Chunk", "NEXT")
    previous_chunk = AsyncRelationshipFrom("Chunk", "NEXT")

class Project(AsyncStructuredNode):
    uid = UniqueIdProperty()
    name = StringProperty(unique_index=True, required=True)
    papers = AsyncRelationshipFrom("Paper", "BELONGS_TO", cardinality=ZeroOrMore)
    authors = AsyncRelationshipFrom("Author", "BELONGS_TO", cardinality=ZeroOrMore)
    documents = AsyncRelationshipFrom("Document", "BELONGS_TO", cardinality=ZeroOrMore)
    tags = AsyncRelationshipFrom("Tag", "BELONGS_TO", cardinality=ZeroOrMore)
    journals = AsyncRelationshipFrom("Journal", "BELONGS_TO", cardinality=ZeroOrMore)
    publicationVenues = AsyncRelationshipFrom("PublicationVenue", "BELONGS_TO", cardinality=ZeroOrMore)