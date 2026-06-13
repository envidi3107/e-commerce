import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

class RAGModel:
    def __init__(self, embedding_model="all-MiniLM-L6-v2"):
        try:
            print(f"Loading SentenceTransformer: {embedding_model}...")
            # Note: Downloading the model for the first time may take a few seconds/minutes
            self.encoder = SentenceTransformer(embedding_model)
            self.embedding_dim = self.encoder.get_sentence_embedding_dimension()
            print("SentenceTransformer loaded.")
        except Exception as e:
            print(f"Failed to load sentence transformer: {e}")
            self.encoder = None
            self.embedding_dim = 384 # Default for MiniLM
            
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.products = [] # To map faiss index to product details
        
    def add_products(self, products_list):
        """
        products_list: list of dicts [{'id': 101, 'name': 'Laptop Gaming XYZ', 'desc': '...', 'price': 10000000}]
        """
        if not self.encoder or not products_list:
            return
            
        self.products = products_list
        texts = [f"{p['name']} - {p.get('description', '')} - {p.get('category_name', '')}" for p in products_list]
        
        embeddings = self.encoder.encode(texts)
        # Convert to float32 for faiss
        embeddings = np.array(embeddings).astype("float32")
        
        self.index.reset() # clear old
        self.index.add(embeddings)
        print(f"Added {len(products_list)} products to FAISS index.")

    def search(self, query, top_k=3):
        if not self.encoder or self.index.ntotal == 0:
            return []
            
        query_emb = self.encoder.encode([query]).astype("float32")
        distances, indices = self.index.search(query_emb, top_k)
        
        results = []
        for idx in indices[0]:
            if idx != -1 and idx < len(self.products):
                results.append(self.products[idx])
        return results

    def generate_response(self, query, retrieved_products):
        """
        Mocked LLM Generation. 
        In production, this would call an LLM API (OpenAI, Gemini, Llama)
        with a prompt containing the retrieved products.
        We will return the structured format required by our Chatbot frontend.
        """
        if not retrieved_products:
            return {
                "text": f"Xin lỗi, tôi không tìm thấy sản phẩm nào phù hợp với \"{query}\".",
                "products": []
            }
            
        # Build structured response for the frontend
        text = f"Dựa trên yêu cầu \"{query}\", tôi tìm thấy {len(retrieved_products)} sản phẩm bằng AI Semantic Search:\n\n"
        if len(retrieved_products) > 0:
            text += f"👉 **{retrieved_products[0]['name']}** có vẻ rất phù hợp với bạn."

        product_cards = []
        for p in retrieved_products:
            product_cards.append({
                "id":        p.get("id"),
                "name":      p.get("name"),
                "price":     p.get("price"),
                "thumbnail": p.get("thumbnail"),
                "category":  p.get("category_name", ""),
            })
            
        return {
            "text": text,
            "products": product_cards
        }

    def chatbot_pipeline(self, query):
        # 1. Retrieve
        results = self.search(query, top_k=4)
        # 2. Generate
        response = self.generate_response(query, results)
        return response
