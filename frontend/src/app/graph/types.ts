export type NodeLabel = 'Author' | 'Paper' | 'Journal' | 'PublicationVenue';

export type NodeProperties = AuthorData | PaperData | JournalData | PublicationVenueData;

// Base node type
export type KnowledgeNode = {
    id: string;
    label: NodeLabel;
    properties: NodeProperties;
};

// Author node properties
export type AuthorData = {
    citation_count: number;
    h_index: number;
    name: string;
    affiliations: string;
    author_id: string;
    url: string;
    homepage?: string;
    paper_count: number;
};

// Paper node properties
export type PaperData = {
    influential_citation_count: number;
    citation_count: number;
    publication_types: string;
    year: number;
    publication_date: string;
    abstract?: string;
    reference_count: number;
    title: string;
    paper_id: string;
};

// Journal node properties
export type JournalData = {
    volume?: string;
    pages?: string;
    name: string;
};

// PublicationVenue node properties
export type PublicationVenueData = {
    alternate_names: string;
    name: string;
    alternate_urls: string;
    type: string;
    alternate_issns?: string;
    url: string;
    venue_id: string;
};

export type EdgeType = 'AUTHORED' | 'PUBLISHED_IN' | 'PUBLISHED_AT';

// Graph edge type
export type Edge = {
    source: string;
    target: string;
    type: EdgeType;
    properties: Record<string, unknown>;
};  


export type KnowledgeGraph = {
    nodes: KnowledgeNode[];
    edges: Edge[];
}