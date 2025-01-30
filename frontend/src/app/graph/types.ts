export type NodeLabel = 'Author' | 'Paper';

export type AuthorData = {
    name: string;
    authorId: string;
}

export type PaperData = {
    citationCount: number;
    level: number;
    abstract: string;
    title: string;
    publicationDate: Date;
    paperId: string;
}

export type KnowledgeNode = {
    id: string;
    label: NodeLabel;
    properties: AuthorData | PaperData;
}

export type EdgeLabel = 'Authored' | 'Cites';

export type Edge = {
    source: string;
    target: string;
    type: EdgeLabel;
    properties: any;
}

export type KnowledgeGraph = {
    nodes: KnowledgeNode[];
    edges: Edge[];
}