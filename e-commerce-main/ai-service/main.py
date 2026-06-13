"""
AI Service - FastAPI
=====================
Implementation for:
  - Product Search (full-text)
  - Product Recommendations (content-based)
  - Trending Products
  - User-based Recommendations (collaborative filtering)
  - Hybrid AI Recommendations (LSTM, Neo4j, FAISS)
  - AI Chatbot
"""

import asyncio
import csv
import os
from datetime import datetime
from typing import List, Optional

import httpx
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from models.lstm_model import LSTMRecommendationEngine
from models.graph_model import Neo4jGraphModel
from models.rag_model import RAGModel
from models.hybrid_model import HybridRecommendationEngine

# Global model instances
lstm_engine = None
graph_engine = None
rag_engine = None
hybrid_engine = None

all_products = [] # Cache of real products

# ─────────────────────────────────────────────
PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://localhost:8001")
REDIS_URL           = os.getenv("REDIS_URL", "redis://localhost:6379/1")
USER_INTERACTIONS_CSV = os.path.join(os.path.dirname(__file__), "user_interactions.csv")

app = FastAPI(
    title="AI Service",
    description="Search & Recommendation Engine for E-Commerce platform",
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────
# Startup: load models and product catalog
# ─────────────────────────────────────────────
async def load_product_catalog():
    """Fetch all products from product-service and ingest into Neo4j and FAISS."""
    global all_products
    products = []
    page = 1
    max_pages = 20  # safety limit

    print("Fetching real products from product-service...")
    async with httpx.AsyncClient(timeout=15.0) as client:
        while page <= max_pages:
            try:
                resp = await client.get(
                    f"{PRODUCT_SERVICE_URL}/api/products/",
                    params={"page": page, "page_size": 100, "status": "active"},
                    headers={"Host": "localhost"},
                )
                if resp.status_code != 200:
                    break
                data = resp.json()
                results = data.get("results", [])
                if not results:
                    break
                products.extend(results)
                if not data.get("next"):
                    break
                page += 1
            except Exception as e:
                print(f"Error fetching products page {page}: {e}")
                break

    if products:
        all_products = products
        # Feed into models
        if graph_engine:
            graph_engine.ingest_products(products)
            # Load and ingest interactions if available
            interactions_path = os.path.join(os.path.dirname(__file__), "data", "user_interactions.json")
            if os.path.exists(interactions_path):
                import json
                try:
                    with open(interactions_path, "r", encoding="utf-8") as f:
                        interactions_data = json.load(f)
                        graph_engine.ingest_interactions(interactions_data)
                except Exception as e:
                    print(f"Error loading interactions data: {e}")
        if rag_engine:
            rag_engine.add_products(products)
        print(f"✅ Ingested {len(products)} products into AI Models")
    else:
        print("⚠️ No products loaded — AI models will be empty until products are available")


@app.on_event("startup")
async def startup_event():
    global lstm_engine, graph_engine, rag_engine, hybrid_engine
    
    print("Initializing Advanced ML Models...")
    lstm_engine = LSTMRecommendationEngine()
    
    # Needs Neo4j DB
    graph_engine = Neo4jGraphModel()
    rag_engine = RAGModel()
    
    # Fetch real products from product-service
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{PRODUCT_SERVICE_URL}/api/products/", params={"page_size": 100})
            if resp.status_code == 200:
                data = resp.json()
                products = data.get("results", [])
                
                # Add to RAG
                if hasattr(rag_engine, 'add_products'):
                    rag_engine.add_products(products)
                
                # Add to Neo4j
                for p in products:
                    graph_engine.add_product(p)
                print(f"Loaded {len(products)} products from product-service.")
            else:
                print(f"Failed to load products. Status: {resp.status_code}")
    except Exception as e:
        print(f"Could not connect to product-service on startup: {e}")
    
    hybrid_engine = HybridRecommendationEngine(
        lstm_model=lstm_engine,
        graph_model=graph_engine,
        rag_model=rag_engine
    )
    print("ML Models Initialized.")

    try:
        await load_product_catalog()
    except Exception as e:
        print(f"⚠️ Initial product load failed ({e}), will retry in background...")
        asyncio.create_task(retry_load_catalog())


async def retry_load_catalog():
    """Retry loading product catalog every 10s until successful."""
    for attempt in range(30):  # try for 5 minutes
        await asyncio.sleep(10)
        try:
            await load_product_catalog()
            if len(all_products) > 0:
                print("✅ Product catalog loaded successfully on retry")
                return
        except Exception:
            pass
    print("❌ Failed to load product catalog after all retries")


# ─────────────────────────────────────────────
# Health Check
# ─────────────────────────────────────────────
@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "ai-service",
        "version": "3.0.0",
        "products_indexed": len(all_products),
    }


# ─────────────────────────────────────────────
# Search
# ─────────────────────────────────────────────
@app.get("/api/search/", tags=["Search"])
async def search_products(
    q: str = Query(..., description="Search query"),
    category: Optional[str] = Query(None, description="Filter by category code"),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """Search products by querying the Product Service."""
    params = {
        "search":    q,
        "status":    "active",
        "page":      page,
        "page_size": page_size,
    }
    if category:
        params["category"] = category
    if min_price is not None:
        params["min_price"] = min_price
    if max_price is not None:
        params["max_price"] = max_price

    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            resp = await client.get(
                f"{PRODUCT_SERVICE_URL}/api/products/",
                params=params,
                headers={"Host": "localhost"}
            )
            resp.raise_for_status()
            data = resp.json()
            return {
                "query":   q,
                "results": data.get("results", []),
                "count":   data.get("count", 0),
                "page":    page,
            }
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Product service unavailable.")


# ─────────────────────────────────────────────
# Recommendations - Similar Products
# ─────────────────────────────────────────────
@app.get("/api/recommendations/{product_id}/", tags=["Recommendations"])
async def recommend_similar(
    product_id: int,
    limit: int = Query(8, ge=1, le=20),
):
    """
    Get similar products. Uses Hybrid Engine if available,
    otherwise falls back to category-based fetching.
    """
    # 1. Try Hybrid Engine (Graph + LSTM)
    if hybrid_engine and len(all_products) > 0:
        # Mock user sequence and id for demo
        mock_user_sequence = [[0.1]*10, [0.2]*10] 
        try:
            rec_ids = hybrid_engine.recommend(
                user_id=1,
                user_sequence=mock_user_sequence,
                limit=limit
            )
            if rec_ids:
                # Map IDs back to full product dicts
                rec_products = [p for p in all_products if p["id"] in rec_ids and p["id"] != product_id]
                if rec_products:
                    return {
                        "product_id":      product_id,
                        "strategy":        "hybrid-graph-lstm",
                        "recommendations": rec_products[:limit],
                    }
        except Exception as e:
            print(f"Hybrid engine failed: {e}")

    # 2. Fallback to product-service category fetch
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            resp = await client.get(f"{PRODUCT_SERVICE_URL}/api/products/{product_id}/", headers={"Host": "localhost"})
            if resp.status_code == 404:
                raise HTTPException(status_code=404, detail="Product not found.")
            resp.raise_for_status()
            product = resp.json()

            category_code = product.get("category_code") or product.get("category")
            similar_resp = await client.get(
                f"{PRODUCT_SERVICE_URL}/api/products/",
                params={"category": category_code, "status": "active", "page_size": limit + 1},
                headers={"Host": "localhost"}
            )
            similar_resp.raise_for_status()
            similar = similar_resp.json().get("results", [])
            similar = [p for p in similar if p["id"] != product_id][:limit]

            return {
                "product_id":      product_id,
                "product_name":    product.get("name"),
                "strategy":        "category-fallback",
                "recommendations": similar,
            }
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Product service unavailable.")


# ─────────────────────────────────────────────
# Trending Products
# ─────────────────────────────────────────────
@app.get("/api/trending/", tags=["Recommendations"])
async def trending_products(
    limit: int = Query(10, ge=1, le=50),
    category: Optional[str] = Query(None),
):
    params = {
        "status":    "active",
        "ordering":  "-rating_avg",
        "page_size": limit,
    }
    if category:
        params["category"] = category

    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            resp = await client.get(f"{PRODUCT_SERVICE_URL}/api/products/", params=params, headers={"Host": "localhost"})
            resp.raise_for_status()
            data = resp.json()
            return {
                "strategy": "rating-based",
                "results":  data.get("results", []),
            }
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Product service unavailable.")


# ─────────────────────────────────────────────
# AI Chatbot Tư Vấn
# ─────────────────────────────────────────────
class ChatMessage(BaseModel):
    query: str

GREETING_KEYWORDS = {"xin chào", "hello", "hi", "chào", "hey", "alo"}
THANKS_KEYWORDS = {"cảm ơn", "thank", "thanks", "cám ơn"}

@app.post("/api/chatbot/", tags=["AI Chatbot"])
async def chatbot_consultation(request: ChatMessage):
    """
    Chatbot endpoint using RAG (Retrieval-Augmented Generation) with FAISS
    and Sentence-Transformers.
    """
    query = request.query.strip()
    query_lower = query.lower()

    if any(kw in query_lower for kw in GREETING_KEYWORDS):
        return {
            "query": query,
            "text": "Xin chào! 👋 Tôi là trợ lý mua sắm AI của ShopVN (Phiên bản RAG + Sentence Transformers). Bạn cần tìm sản phẩm gì?",
            "products": []
        }
        
    if any(kw in query_lower for kw in THANKS_KEYWORDS):
        return {
            "query": query,
            "text": "Không có gì! 😊 Chúc bạn mua sắm vui vẻ!",
            "products": []
        }

    try:
        if rag_engine and len(all_products) > 0:
            # Use RAG to get formatted response
            response = rag_engine.chatbot_pipeline(query)
            return {"query": query, **response}
        return {
            "query": query,
            "text": "Product catalog is not loaded yet. Please try again later.",
            "products": [],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ─────────────────────────────────────────────
# Hybrid AI Recommendations
# ─────────────────────────────────────────────
@app.get("/recommend", tags=["AI Recommendations"])
async def get_hybrid_recommendations(
    user_id: int, 
    query: Optional[str] = None,
    limit: int = 5
):
    """
    Get product recommendations based on Hybrid model (LSTM + Graph + RAG)
    """
    # Fetch user sequence from CSV
    user_sequence = lstm_engine.extract_user_sequence_from_csv(user_id=user_id)
    
    try:
        recommendations = hybrid_engine.recommend(
            user_id=user_id,
            user_sequence=user_sequence,
            query=query,
            limit=limit
        )
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────
# Admin
# ─────────────────────────────────────────────
class ChatbotRequest(BaseModel):
    query: str

@app.post("/chatbot", tags=["AI Chatbot"])
async def chatbot_consultation(request: ChatbotRequest):
    """
    Chatbot endpoint using RAG (Retrieval-Augmented Generation)
    """
    try:
        response = rag_engine.chatbot_pipeline(request.query)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ─────────────────────────────────────────────
# Webhooks & Tracking
# ─────────────────────────────────────────────
class TrackingEvent(BaseModel):
    user_id: int
    product_id: int
    event_type: str

@app.post("/api/tracking/event", tags=["Tracking"])
async def track_event(event: TrackingEvent):
    """
    Log user interaction to CSV and Neo4j
    """
    try:
        # Write to Neo4j
        if graph_engine:
            graph_engine.add_interaction(event.user_id, event.product_id, event.event_type)
            
        # Write to CSV
        file_exists = os.path.isfile(USER_INTERACTIONS_CSV)
        with open(USER_INTERACTIONS_CSV, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['user_id', 'product_id', 'event_type', 'timestamp'])
            writer.writerow([event.user_id, event.product_id, event.event_type, datetime.now().isoformat()])
            
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ProductWebhook(BaseModel):
    id: int
    name: str
    desc: Optional[str] = ""
    price: Optional[float] = 0.0
    category: Optional[str] = ""

@app.post("/api/webhooks/product-sync", tags=["Webhooks"])
async def product_sync_webhook(product: ProductWebhook):
    """
    Receive product updates from product-service
    """
    try:
        p_dict = product.dict()
        if rag_engine and hasattr(rag_engine, 'add_products'):
            rag_engine.add_products([p_dict])
        if graph_engine:
            graph_engine.add_product(p_dict)
        return {"status": "success", "synced_product_id": product.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
