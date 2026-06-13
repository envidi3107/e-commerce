# AI Service Walkthrough

I have successfully implemented the core components for the AI Service recommendation engine and chatbot as per the architectural design. The implementation integrates **LSTM (Sequence Modeling)**, **Neo4j (Knowledge Graph)**, and **FAISS (RAG)** into a unified FastAPI service.

## Components Implemented

### 1. ML Dependencies (`requirements.txt`)
Added the necessary ML stack for processing:
- `torch` for PyTorch-based neural networks (LSTM).
- `neo4j` for connecting to the graph database.
- `faiss-cpu` for the vector database.
- `sentence-transformers` for encoding product descriptions into semantic embeddings.

### 2. LSTM Sequence Model (`models/lstm_model.py`)
Implemented the `LSTMModel` using PyTorch to predict the next product based on user interaction sequences. 
- It accepts sequences of fixed features and outputs probabilities for product indices.
- A wrapper class handles tensor conversions and top-k predictions.

### 3. Knowledge Graph (`models/graph_model.py`)
Implemented the `Neo4jGraphModel` to query relationship-based recommendations.
- Connects to a standard Neo4j instance (`bolt://localhost:7687`).
- Implemented the Cypher query: `MATCH (u:User)-[:BUY|VIEW]->(p)-[:SIMILAR]->(rec)`.
- Contains a helper method to initialize dummy data so you can test it immediately.

### 4. RAG Chatbot Engine (`models/rag_model.py`)
Implemented the `RAGModel` for context-aware chatbot responses.
- Uses `sentence-transformers` (specifically `all-MiniLM-L6-v2`) to encode product metadata.
- Stores these embeddings in a FAISS index for high-speed similarity search.
- Includes a simple text generator (mocked LLM) to construct conversational answers containing the retrieved products.

### 5. Hybrid Recommender (`models/hybrid_model.py`)
Implemented the `HybridRecommendationEngine` to aggregate predictions from LSTM, Graph, and RAG.
- Calculates `final_score = w1 * lstm + w2 * graph + w3 * rag` based on ranking positions to combine the results.
- Provides fallback logic (dummy trending items) if no data is matched.

### 6. API Endpoints (`main.py`)
Updated the FastAPI service entry point:
- **Startup Event**: Automatically initializes the models, loads the Sentence Transformer, and seeds FAISS and Neo4j with dummy products and relationships.
- **`GET /recommend`**: Accepts `user_id` and an optional `query`. Returns an array of suggested product IDs.
- **`POST /chatbot`**: Accepts a JSON body `{"query": "tôi cần laptop giá rẻ"}` and responds with generated natural text containing the closest matching items.

## How to Test

1. **Install dependencies**: `pip install -r requirements.txt` inside the `ai-service` folder.
2. **Start Neo4j**: Ensure a local Neo4j database is running on the default port. If not, the graph predictions will gracefully fail and return empty lists (falling back to LSTM/RAG).
3. **Run the API**: `uvicorn main:app --reload --port 8002` (or whatever port you have configured for AI service).
4. **Test Recommendation**: 
   ```bash
   curl "http://localhost:8002/recommend?user_id=1"
   ```
5. **Test Chatbot**:
   ```bash
   curl -X POST "http://localhost:8002/chatbot" \
   -H "Content-Type: application/json" \
   -d '{"query": "tôi cần mua màn hình chơi game"}'
   ```
