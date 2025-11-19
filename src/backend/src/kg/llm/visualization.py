from llm.paper_similarity import Neo4jPaperVectorStore
import numpy as np
import matplotlib.colors as mcolors
import pandas as pd
from sklearn.decomposition import PCA
from kg.db.util import load_default_kg
from kg.llm.chat import NomicEmbeddingAdapter
from kg.db.util import load_default_kg
from kg.llm.adapter import NomicEmbeddingAdapter
        
def process_color_vector(raw_color_data, mode, date_format="%Y-%m-%d", compute_norm=False, **kwargs):
    if mode == 'categorical':
        # Simply convert to list (or np.array) of labels.
        processed = list(raw_color_data)
        norm = None

    elif mode == 'continuous':
        # Convert to a float array.
        processed = np.array(raw_color_data, dtype=float)
        norm = None

    elif mode == 'date':
        dates_series = pd.to_datetime(pd.Series(raw_color_data), format=date_format, errors='coerce')
        date_ints = dates_series.astype('int64')
        date_ints = date_ints.where(date_ints != np.iinfo('int64').min)
        processed = date_ints / 1e9
        norm = None
        if compute_norm:
            valid_mask = ~dates_series.isna()
            if valid_mask.any():
                vmin = processed[valid_mask].min()
                vmax = processed[valid_mask].max()
                norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
    else:
        raise ValueError("Invalid mode. Choose 'categorical', 'continuous', or 'date'.")

    return processed, norm
    

def create_plot(model_id, queries, color_var, labels=None, n_docs=10, n_components=0.95):
    if labels is None:
        labels = queries

    kg = load_default_kg()
    nomic_adapter = NomicEmbeddingAdapter(model_id=model_id)

    # Our tiny custom vector store
    vector_store = Neo4jPaperVectorStore(kg, nomic_adapter)

    return generate_plot_from_query(
        queries,
        vector_store,
        color_var,
        n_docs=n_docs,
        n_components=n_components,
        labels=labels
    )



def generate_plot_from_query(
    query,
    vector_store,
    color_var,
    n_docs=10,
    n_components=.95,
    labels=None
):
    query = ["search_query: " + q for q in query]
    if labels is not None:
        full_labels = []
        for l in labels:
            full_labels.extend([l] * n_docs)
        labels = full_labels
    
    all_embeddings = []
    all_citation_counts = []
    all_dates = []
    all_paper_ids = []
    
    for q in query:
        retrieved_docs = vector_store.similarity_search_with_score(q, k=n_docs)
        
        embeddings = np.array([doc.metadata.get("abstract_embedding") for doc, _ in retrieved_docs])
        citation_counts = np.array([doc.metadata.get("citation_count") for doc, _ in retrieved_docs])
        dates = np.array([doc.metadata.get("publication_date") for doc, _ in retrieved_docs])
        paper_ids = np.array([doc.metadata.get("paper_id") for doc, _ in retrieved_docs])
        
        all_embeddings.append(embeddings)
        all_citation_counts.append(citation_counts)
        all_dates.append(dates)
        all_paper_ids.append(paper_ids)
    
    if len(query) > 1:  
        embeddings = np.concatenate(all_embeddings, axis=0)
        citation_counts = np.concatenate(all_citation_counts, axis=0)
        dates = np.concatenate(all_dates, axis=0)
    
    pca = PCA(n_components=n_components)
    reduced_embeddings = pca.fit_transform(embeddings)
    
    if color_var == 'labels' and labels is not None:
        labels, _ = process_color_vector(labels, mode='categorical')
        return reduced_embeddings, labels, all_paper_ids
    elif color_var == 'citationCount':
        citation_counts, _ = process_color_vector(citation_counts, mode='continuous')
        return reduced_embeddings, citation_counts, all_paper_ids
    elif color_var == 'dates':
        dates, norm = process_color_vector(dates, mode='date', date_format="%Y-%m-%d", compute_norm=True)
        return reduced_embeddings, dates, all_paper_ids
    else:
        raise Exception(f'color_var must be one of: labels, citationCount, dates. Current value is {color_var}')





