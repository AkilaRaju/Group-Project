# backend/processing.py
"""Processing utilities for the Ticket‑to‑FAQ pipeline.
- clean_text: basic sanitisation
- vectorize: TF‑IDF on issue + resolution
- auto_cluster: silhouette‑based k selection then KMeans
"""
import re
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

def clean_text(text: str) -> str:
    """Lower‑case, strip HTML, keep alphanum, collapse whitespace."""
    text = text.lower()
    text = re.sub(r'<[^>]+>', ' ', text)          # strip HTML tags
    text = re.sub(r'[^a-z0-9\s]', ' ', text)      # keep letters/numbers
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def vectorize(df: pd.DataFrame) -> np.ndarray:
    """Combine issue + resolution, clean, and TF‑IDF vectorise."""
    combined = (df['issue'] + ' ' + df['resolution']).apply(clean_text)
    vect = TfidfVectorizer(stop_words='english')
    return vect.fit_transform(combined)

def auto_cluster(tfidf_matrix, max_k: int = 10):
    """Find the best k (2..max_k) via silhouette score, then return labels and k."""
    n_samples = tfidf_matrix.shape[0]
    
    if n_samples <= 2:
        return np.zeros(n_samples, dtype=int), 1

    best_k, best_score = 2, -1
    # Silhouette score requires n_clusters <= n_samples - 1
    limit = min(max_k, n_samples - 1)
    
    if limit < 2:
        # If we can't search for multiple clusters, just cluster with k=2
        km = KMeans(n_clusters=2, random_state=42, n_init='auto')
        labels = km.fit_predict(tfidf_matrix)
        return labels, 2

    for k in range(2, limit + 1):
        try:
            km = KMeans(n_clusters=k, random_state=42, n_init='auto')
            labels = km.fit_predict(tfidf_matrix)
            score = silhouette_score(tfidf_matrix, labels)
            if score > best_score:
                best_k, best_score = k, score
        except Exception:
            continue
            
    final_km = KMeans(n_clusters=best_k, random_state=42, n_init='auto')
    final_labels = final_km.fit_predict(tfidf_matrix)
    return final_labels, best_k
