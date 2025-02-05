from db.models import Paper, PublicationVenue, Journal, Author
from scholar.models import Paper as ScholarPaper
from typing import List
from neomodel import adb
from scholar.api import enrich_papers, enrich_authors, get_citations, get_references

async def create_paper_graph(paper_ids: List[str]):
    paper_dicts = []
    author_dicts = {}
    journal_dicts = {}
    venue_dicts = {}
    paper_author_relations = []
    paper_journal_relations = []
    paper_venue_relations = []

    existing_paper_ids = [paper.paper_id for paper in await Paper.nodes.filter(paper_id__in=paper_ids)]
    new_paper_ids = set(paper_ids) - set(existing_paper_ids)
    new_paper_ids = list(map(str, new_paper_ids))

    if len(new_paper_ids) == 0:
        return

    papers = enrich_papers(new_paper_ids)

    await adb.begin()
    try:
        for paper_data in papers:
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
            })

            # Create Author dict & relationships
            author_ids = [author.authorId for author in paper_data.authors]
            authors = enrich_authors(author_ids)
            for author_data in authors:
                if author_data.authorId not in author_dicts:
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
                paper_author_relations.append((paper_data.paperId, author_data.authorId))

            # Create Journal dict & relationships
            if paper_data.journal and paper_data.journal.name:
                journal_name = paper_data.journal.name.strip()
                if journal_name not in journal_dicts:
                    journal_dicts[journal_name] = {
                        "name": journal_name,
                        "pages": paper_data.journal.pages,
                        "volume": paper_data.journal.volume,
                    }
                paper_journal_relations.append((paper_data.paperId, journal_name))

            # Create Publication Venue dict & relationships
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

        # Create nodes
        await Paper.create_or_update(*paper_dicts)
        await Author.create_or_update(*author_dicts.values())
        await Journal.create_or_update(*journal_dicts.values())
        await PublicationVenue.create_or_update(*venue_dicts.values())

        # Create author relationships
        for paper_id, author_id in paper_author_relations:
            paper = await Paper.nodes.get(paper_id=paper_id)
            author = await Author.nodes.get(author_id=author_id)
            await paper.authors.connect(author)

        # Create journal relationships
        for paper_id, journal_name in paper_journal_relations:
            paper = await Paper.nodes.get(paper_id=paper_id)
            journal = await Journal.nodes.get(name=journal_name)
            await paper.journal.connect(journal)

        # Create venue relationships
        for paper_id, venue_id in paper_venue_relations:
            paper = await Paper.nodes.get(paper_id=paper_id)
            venue = await PublicationVenue.nodes.get(venue_id=venue_id)
            await paper.publication_venue.connect(venue)
        
        # Commit
        await adb.commit()
    except Exception as e:
        await adb.rollback()
        raise e


async def add_citations(paper_ids):
    # Create paper graph
    await create_paper_graph(paper_ids)

    paper_dict = {}

    # Add references to paper
    for paper_id in paper_ids:
        citations = get_citations(paper_id)
        citation_ids = [reference.paperId for reference in citations]
        
        # Add to graph
        await create_paper_graph(citation_ids)

        for citation_id in citation_ids:
            if citation_id not in paper_dict:
                paper_dict[citation_id] = paper_id
    
    # Add relationships
    for paper_id, citation_id in paper_dict.items():
        paper = Paper.get(id=paper_id)
        reference = Paper.get(id=citation_id)
        paper.citations.add(reference)

async def add_references(paper_ids):
    # Create paper graph
    await create_paper_graph(paper_ids)

    paper_dict = {}

    # Add citations to paper
    for paper_id in paper_ids:
        references = get_references(paper_id)
        reference_ids = [reference.paperId for reference in references]
        
        # Add to graph
        await create_paper_graph(reference_ids)

        for reference_id in reference_ids:
            if reference_id not in paper_dict:
                paper_dict[reference_id] = paper_id
    
    # Add relationships
    for paper_id, reference_id in paper_dict.items():
        paper = Paper.get(id=paper_id)
        reference = Paper.get(id=reference_id)
        paper.references.add(reference)