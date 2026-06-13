from neo4j import GraphDatabase
import os

class Neo4jGraphModel:
    def __init__(self, uri=None, user=None, password=None):
        self.uri = uri or os.getenv("NEO4J_URI", "bolt://neo4j:7687")
        self.user = user or os.getenv("NEO4J_USER", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "password")
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
        except Exception as e:
            print(f"Failed to connect to Neo4j: {e}")
            self.driver = None

    def close(self):
        if self.driver:
            self.driver.close()

    def get_recommendations(self, user_id, limit=5):
        """
        MATCH (u:User {id: $user_id})-[:BUY]->(p)-[:SIMILAR]->(rec) 
        RETURN rec.id AS recommended_id, count(rec) AS score
        ORDER BY score DESC LIMIT $limit
        """
        if not self.driver:
            return []

        query = """
        MATCH (u:User {id: $user_id})-[:BUY|VIEW]->(p:Product)-[:SIMILAR]->(rec:Product)
        WHERE NOT (u)-[:BUY]->(rec)
        RETURN rec.id AS recommended_id, count(rec) AS score
        ORDER BY score DESC
        LIMIT $limit
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(query, user_id=user_id, limit=limit)
                recommendations = []
                for record in result:
                    recommendations.append(record["recommended_id"])
                return recommendations
        except Exception as e:
            print(f"Error querying Neo4j: {e}")
            return []

    def add_interaction(self, user_id, product_id, event_type):
        if not self.driver:
            return

        action = str(event_type or "VIEW").upper()
        if action == "ADD_TO_CART":
            action = "ADD_TO_CART"
        elif action not in {"VIEW", "BUY"}:
            action = "VIEW"

        query = f"""
        MERGE (u:User {{id: $user_id}})
        MERGE (p:Product {{id: $product_id}})
        MERGE (u)-[:{action}]->(p)
        """

        try:
            with self.driver.session() as session:
                session.run(query, user_id=user_id, product_id=product_id)
        except Exception as e:
            print(f"Neo4j add_interaction error: {e}")

    def ingest_products(self, products):
        """
        Ingest real products from product-service into Neo4j and create basic SIMILAR relationships based on category.
        """
        if not self.driver or not products:
            return
            
        queries = [
            "MATCH (n) DETACH DELETE n"  # Clear existing for fresh ingest
        ]
        
        # Create product nodes
        for p in products:
            queries.append(f"CREATE (p:Product {{id: {p['id']}, name: '{p['name'].replace(''''''', ''')} ', category: '{p.get('category_name', '')}'}})")
            
        # Create SIMILAR relationships for products in the same category (naive approach for demonstration)
        queries.append("""
            MATCH (p1:Product), (p2:Product)
            WHERE p1.category = p2.category AND p1.id <> p2.id AND p1.category <> ''
            MERGE (p1)-[:SIMILAR]->(p2)
        """)
        
        try:
            with self.driver.session() as session:
                for q in queries:
                    session.run(q)
            print(f"Neo4j: Ingested {len(products)} products and created SIMILAR relationships.")
        except Exception as e:
            print(f"Neo4j Ingestion Error: {e}")

    def ingest_interactions(self, interactions_data):
        """
        interactions_data: list of dicts [{'user_id': 1, 'interactions': [{'product_id': 101, 'action': 'VIEW'}]}]
        """
        if not self.driver or not interactions_data:
            return
            
        queries = [
            "MATCH (u:User) DETACH DELETE u" # Clear old users
        ]
        
        for user in interactions_data:
            uid = user.get("user_id")
            queries.append(f"CREATE (u:User {{id: {uid}}})")
            for inter in user.get("interactions", []):
                pid = inter.get("product_id")
                action = inter.get("action", "VIEW") # VIEW or BUY
                queries.append(f"MATCH (u:User {{id: {uid}}}), (p:Product {{id: {pid}}}) MERGE (u)-[:{action}]->(p)")
                
        try:
            with self.driver.session() as session:
                for q in queries:
                    session.run(q)
            print(f"Neo4j: Ingested interactions for {len(interactions_data)} users.")
        except Exception as e:
            print(f"Neo4j Interaction Ingestion Error: {e}")
