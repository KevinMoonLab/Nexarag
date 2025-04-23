import numpy as np
import matplotlib.colors as mcolors
import pandas as pd
from sklearn.decomposition import PCA
        
def process_color_vector(raw_color_data, mode, date_format="%Y-%m-%d", compute_norm=False, **kwargs):
    """
    Processes raw color data into a format suitable for plotting in one of three modes:
      - 'categorical': expects labels (e.g., ['DM', 'GAN', ...])
      - 'continuous': expects numerical values (e.g., citation counts)
      - 'date': expects date strings which will be converted to Unix timestamps
    
    Parameters:
    -----------
    raw_color_data : array-like
        The raw data extracted from document metadata.
    mode : str
        One of 'categorical', 'continuous', or 'date'.
    date_format : str, optional
        The format to use when parsing dates (default: "%Y-%m-%d").
    compute_norm : bool, optional
        For mode 'date': if True, computes and returns a matplotlib Normalize instance 
        based on valid date values (default: False).
    **kwargs:
        Any additional keyword arguments for further customization.
    
    Returns:
    --------
    processed : np.array or list
        The processed color vector.
    norm : matplotlib.colors.Normalize or None
        For mode 'date': returns a Normalize instance if compute_norm is True, otherwise None.
        For other modes, always returns None.
    """
    if mode == 'categorical':
        # Simply convert to list (or np.array) of labels.
        processed = list(raw_color_data)
        norm = None

    elif mode == 'continuous':
        # Convert to a float array.
        processed = np.array(raw_color_data, dtype=float)
        norm = None

    elif mode == 'date':
        # Convert the raw data to a pandas Series and then to datetime.
        dates_series = pd.to_datetime(pd.Series(raw_color_data), format=date_format, errors='coerce')
        # Convert datetime values to Unix timestamp (seconds)
        # Note: dates_series.astype('int64') converts to nanoseconds.
        date_ints = dates_series.astype('int64')
        # Some NaT values turn into the minimum int64; replace those with NaN.
        date_ints = date_ints.where(date_ints != np.iinfo('int64').min)
        # Convert from nanoseconds to seconds.
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

def generate_plot_from_query(
    query,
    vector_store,
    color_var,
    x_axis_comp=0,
    y_axis_comp=1,
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
    
    for q in query:
        retrieved_docs = vector_store.similarity_search_with_score(q, k=n_docs)
        
        embeddings = np.array([doc.metadata.get("abstractEmbedding") for doc, _ in retrieved_docs])
        citation_counts = np.array([doc.metadata.get("citationCount") for doc, _ in retrieved_docs])
        dates = np.array([doc.metadata.get("publicationDate") for doc, _ in retrieved_docs])
        
        all_embeddings.append(embeddings)
        all_citation_counts.append(citation_counts)
        all_dates.append(dates)
    
    if len(query) > 1:  
        embeddings = np.concatenate(all_embeddings, axis=0)
        citation_counts = np.concatenate(all_citation_counts, axis=0)
        dates = np.concatenate(all_dates, axis=0)
    
    pca = PCA(n_components=n_components)
    reduced_embeddings = pca.fit_transform(embeddings)
    
    if color_var == 'labels' and labels is not None:
        labels, _ = process_color_vector(labels, mode='categorical')
        plot_pca_embeddings(reduced_embeddings[:,x_axis_comp], reduced_embeddings[:,y_axis_comp], labels, is_categorical=True, return_fig=False)
    elif color_var == 'citationCount':
        citation_counts, _ = process_color_vector(citation_counts, mode='continuous')
        plot_pca_embeddings(reduced_embeddings[:,x_axis_comp], reduced_embeddings[:,y_axis_comp], citation_counts, is_categorical=False, return_fig=False)
    elif color_var == 'dates':
        dates, norm = process_color_vector(dates, mode='date', date_format="%Y-%m-%d", compute_norm=True)
        plot_pca_embeddings(reduced_embeddings[:,x_axis_comp], reduced_embeddings[:,y_axis_comp], dates, is_date=True, norm=norm, cmap='viridis', return_fig=False)
    else:
        raise Exception(f'color_var must be one of: labels, citationCount, dates. Current value is {color_var}')