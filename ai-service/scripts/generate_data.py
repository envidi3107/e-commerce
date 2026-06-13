import os
import json
import random
import httpx
import asyncio

PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://localhost:8001")
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
OUTPUT_FILE = os.path.join(DATA_DIR, "user_interactions.json")
PRODUCT_MAPPING_FILE = os.path.join(DATA_DIR, "product_mapping.json")

async def fetch_products():
    products = []
    page = 1
    async with httpx.AsyncClient(timeout=15.0) as client:
        while True:
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
    return products

async def main():
    print("Fetching products from product-service...")
    products = await fetch_products()
    if not products:
        print("No products fetched. Make sure product-service is running. Using mock products instead.")
        products = [{"id": i, "category_name": random.choice(["Laptop", "Phone", "Accessory"])} for i in range(1, 101)]
    
    product_ids = [p["id"] for p in products]
    print(f"Found {len(product_ids)} products.")
    
    # Save product mapping (product_id -> index)
    mapping = {pid: idx for idx, pid in enumerate(product_ids)}
    
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(PRODUCT_MAPPING_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "id_to_idx": mapping,
            "idx_to_id": {idx: pid for pid, idx in mapping.items()}
        }, f)
        
    num_users = 200
    interactions = []
    
    print(f"Generating mock interactions for {num_users} users...")
    for user_id in range(1, num_users + 1):
        # A user interacts with 3 to 15 products
        seq_len = random.randint(3, 15)
        user_seq = []
        for _ in range(seq_len):
            pid = random.choice(product_ids)
            action = random.choices(["VIEW", "BUY"], weights=[0.8, 0.2])[0]
            user_seq.append({"product_id": pid, "action": action})
        
        interactions.append({
            "user_id": user_id,
            "interactions": user_seq
        })
        
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(interactions, f, indent=2)
        
    print(f"Successfully generated data at {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(main())
