"""
Lightweight product recommendation engine using TF-IDF + cosine similarity.
No heavy ML dependencies (torch, sentence-transformers) required.
"""
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class ProductRecommender:
    """
    Content-based recommender that builds a TF-IDF matrix from product
    text (name + description + category + attributes) and finds similar
    products via cosine similarity.
    """

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words=None,   # keep Vietnamese words
            ngram_range=(1, 2),
        )
        self.tfidf_matrix = None
        self.products = []         # list of product dicts
        self.id_to_idx = {}        # product_id -> index in matrix
        self.ready = False

    # ── Build index from product list ──────────────────────────
    def fit(self, products: list[dict]):
        """
        products: list of dicts from product-service, each with
        id, name, description, category_name, attributes, price, thumbnail …
        """
        if not products:
            return

        self.products = products
        self.id_to_idx = {p["id"]: i for i, p in enumerate(products)}

        corpus = []
        for p in products:
            # Combine text fields for richer TF-IDF
            parts = [
                p.get("name", ""),
                p.get("description", ""),
                p.get("category_name", ""),
            ]
            attrs = p.get("attributes", {})
            if isinstance(attrs, dict):
                parts.extend(str(v) for v in attrs.values())
            corpus.append(" ".join(parts))

        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)
        self.ready = True

    # ── Similar products (for /api/recommendations/{id}/) ──────
    def similar(self, product_id: int, limit: int = 8) -> list[dict]:
        if not self.ready or product_id not in self.id_to_idx:
            return []

        idx = self.id_to_idx[product_id]
        sim_scores = cosine_similarity(
            self.tfidf_matrix[idx : idx + 1], self.tfidf_matrix
        ).flatten()

        # Exclude the product itself, sort by similarity descending
        ranked = np.argsort(sim_scores)[::-1]
        results = []
        for i in ranked:
            if int(i) == idx:
                continue
            results.append(self.products[int(i)])
            if len(results) >= limit:
                break
        return results

    # ── Search by text query (for chatbot) ─────────────────────
    def search(self, query: str, limit: int = 5) -> list[dict]:
        if not self.ready:
            return []

        query_vec = self.vectorizer.transform([query])
        sim_scores = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        ranked = np.argsort(sim_scores)[::-1]

        results = []
        for i in ranked:
            if sim_scores[int(i)] < 0.01:  # relevance threshold
                break
            results.append(self.products[int(i)])
            if len(results) >= limit:
                break
        return results
