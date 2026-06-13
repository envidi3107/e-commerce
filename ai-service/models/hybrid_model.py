from collections import defaultdict

class HybridRecommendationEngine:
    def __init__(self, lstm_model, graph_model, rag_model, w1=0.4, w2=0.4, w3=0.2):
        """
        w1: LSTM weight
        w2: Graph weight
        w3: RAG (semantic) weight
        """
        self.lstm = lstm_model
        self.graph = graph_model
        self.rag = rag_model
        self.w1 = w1
        self.w2 = w2
        self.w3 = w3

    def recommend(self, user_id, user_sequence=None, query=None, limit=5):
        scores = defaultdict(float)

        # 1. LSTM Predictions (Sequence based)
        if self.lstm and user_sequence:
            lstm_preds = self.lstm.predict_next_products(user_sequence, top_k=limit*2)
            # Assign scores based on rank: highest rank = highest score
            for i, p_id in enumerate(lstm_preds):
                scores[p_id] += self.w1 * (1.0 / (i + 1))

        # 2. Graph Predictions (Relationship based)
        if self.graph:
            graph_preds = self.graph.get_recommendations(user_id, limit=limit*2)
            # Graph preds are already sorted by score/count
            for i, p_id in enumerate(graph_preds):
                scores[p_id] += self.w2 * (1.0 / (i + 1))

        # 3. RAG / Semantic Predictions (Content/Query based)
        if self.rag and query:
            rag_preds = self.rag.search(query, top_k=limit*2)
            for i, product in enumerate(rag_preds):
                p_id = product.get('id')
                if p_id:
                    scores[p_id] += self.w3 * (1.0 / (i + 1))

        # Sort and return top K
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        final_recommendations = [item[0] for item in sorted_scores[:limit]]
        
        return final_recommendations
