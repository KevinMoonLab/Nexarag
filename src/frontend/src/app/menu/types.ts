export type PartialAuthor = {
    name: string;
    authorId: string;
}

export type PaperRelevanceResult = {
    title: string;
    year: number;
    paperId: string;
    authors: PartialAuthor[];
}