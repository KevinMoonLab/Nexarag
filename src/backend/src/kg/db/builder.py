from kg.db.models import Paper, PublicationVenue, Journal, Author, Project
from typing import List
from scholar.api import enrich_papers, enrich_authors, get_citations, get_references
from scholar.util import retry
from kg.llm.embeddings import create_abstract_embedding

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_paper_graph(paper_ids: List[str], project_id: str = None):
    paper_dicts = []
    author_dicts = {}
    journal_dicts = {}
    venue_dicts = {}
    paper_author_relations = []
    paper_journal_relations = []
    paper_venue_relations = []

    # Filter out papers that already exist
    existing_paper_ids = [paper.paper_id for paper in await Paper.nodes.filter(paper_id__in=paper_ids)]
    new_paper_ids = list(set(paper_ids) - set(existing_paper_ids))
    new_paper_ids = list(map(str, new_paper_ids))

    if not new_paper_ids:
        return
    
    # Enrich papers
    papers = retry(enrich_papers, new_paper_ids)
    all_author_ids = set()
    for paper_data in papers:
        abstract_embedding = create_abstract_embedding(paper_data.abstract) if paper_data.abstract else None

        paper_dicts.append({
            "paper_id": paper_data.paperId,
            "title": paper_data.title.strip() if paper_data.title else "Untitled Paper",
            "abstract": paper_data.abstract,
            "year": paper_data.year,
            "reference_count": paper_data.referenceCount,
            "citation_count": paper_data.citationCount,
            "influential_citation_count": paper_data.influentialCitationCount,
            "publication_types": paper_data.publicationTypes,
            "publication_date": paper_data.publicationDate,
            "abstract_embedding": abstract_embedding,
        })

        for author in paper_data.authors:
            all_author_ids.add(author.authorId)
            paper_author_relations.append((paper_data.paperId, author.authorId))

        if paper_data.journal and paper_data.journal.name:
            journal_name = paper_data.journal.name.strip()
            if journal_name not in journal_dicts:
                journal_dicts[journal_name] = {
                    "name": journal_name,
                    "pages": paper_data.journal.pages,
                    "volume": paper_data.journal.volume,
                }
            paper_journal_relations.append((paper_data.paperId, journal_name))

        if paper_data.publicationVenue and paper_data.publicationVenue.id:
            venue_id = paper_data.publicationVenue.id
            if venue_id not in venue_dicts:
                venue_dicts[venue_id] = {
                    "venue_id": venue_id,
                    "name": paper_data.publicationVenue.name,
                    "type": paper_data.publicationVenue.type,
                    "alternate_names": paper_data.publicationVenue.alternate_names,
                    "issn": paper_data.publicationVenue.issn,
                    "alternate_issns": paper_data.publicationVenue.alternate_issns,
                    "url": paper_data.publicationVenue.url,
                    "alternate_urls": paper_data.publicationVenue.alternate_urls,
                }
            paper_venue_relations.append((paper_data.paperId, venue_id))

    # Enrich authors once for all unique author IDs
    enriched_authors = retry(enrich_authors, list(all_author_ids))
    for author_data in enriched_authors:
        author_dicts[author_data.authorId] = {
            "author_id": author_data.authorId,
            "name": author_data.name,
            "url": author_data.url,
            "affiliations": author_data.affiliations,
            "homepage": author_data.homepage,
            "citation_count": author_data.citationCount,
            "paper_count": author_data.paperCount,
            "h_index": author_data.hIndex,
        }

    try:
        await Paper.create_or_update(*paper_dicts)
        await Author.create_or_update(*author_dicts.values())
        await Journal.create_or_update(*journal_dicts.values())
        await PublicationVenue.create_or_update(*venue_dicts.values())
    except:
        logger.error("Error creating or updating nodes in the graph database")

    for paper_id, author_id in paper_author_relations:
        try:
            paper = await Paper.nodes.get_or_none(paper_id=paper_id)
            author = await Author.nodes.get_or_none(author_id=author_id)
            if paper and author:
                await author.papers.connect(paper)
        except:
            logger.error(f"Error connecting author {author_id} to paper {paper_id}")

    for paper_id, journal_name in paper_journal_relations:
        try:
            paper = await Paper.nodes.get_or_none(paper_id=paper_id)
            journal = await Journal.nodes.get_or_none(name=journal_name)
            if paper and journal:
                await paper.journal.connect(journal)
        except:
            logger.error(f"Error connecting journal {journal_name} to paper {paper_id}")

    for paper_id, venue_id in paper_venue_relations:
        try:
            paper = await Paper.nodes.get_or_none(paper_id=paper_id)
            venue = await PublicationVenue.nodes.get_or_none(venue_id=venue_id)
            if paper and venue:
                await paper.publication_venue.connect(venue)
        except:
            logger.error(f"Error connecting venue {venue_id} to paper {paper_id}")


async def add_citations(paper_ids):
    await create_paper_graph(paper_ids)

    paper_dict = {}

    all_citations = []
    for paper_id in paper_ids:
        citations = retry(get_citations, paper_id)
        citation_ids = [reference.paperId for reference in citations]
        all_citations.extend(citation_ids)

        for citation_id in citation_ids:
            if citation_id not in paper_dict:
                paper_dict[citation_id] = paper_id
    
    await create_paper_graph(all_citations)

    for paper_id, citation_id in paper_dict.items():
        paper = await Paper.nodes.get_or_none(paper_id=paper_id)
        reference = await Paper.nodes.get_or_none(paper_id=citation_id)
        if paper and reference:
            await paper.citations.connect(reference)
    
    return list(paper_dict.keys())

async def add_references(paper_ids):
    await create_paper_graph(paper_ids)

    paper_dict = {}

    for paper_id in paper_ids:
        references = get_references(paper_id)
        reference_ids = [reference.paperId for reference in references]
        
        await create_paper_graph(reference_ids)

        for reference_id in reference_ids:
            if reference_id not in paper_dict:
                paper_dict[reference_id] = paper_id
    
    for paper_id, reference_id in paper_dict.items():
        paper = await Paper.nodes.get(paper_id=paper_id)
        reference = await Paper.nodes.get(paper_id=reference_id)
        if paper and reference:
            await paper.references.connect(reference)

    return list(paper_dict.keys())