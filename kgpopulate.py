from neo4j import GraphDatabase

# --- Connection details ---
URI = "neo4j://127.0.0.1:7687"
USERNAME = "neo4j"
PASSWORD = "Capstone1234"  # replace with your actual Neo4j password

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

# --- Function to populate Knowledge Graph ---
def populate_knowledge_graph():
    data = [
        {
            "crop": "Rice",
            "policy": "PM-Kisan",
            "eligibility": "All small and marginal farmers owning up to 2 hectares of land",
            "benefit": "₹6000 per year in 3 installments directly to bank account"
        },
        {
            "crop": "Wheat",
            "policy": "Pradhan Mantri Fasal Bima Yojana",
            "eligibility": "All farmers growing notified crops in notified areas",
            "benefit": "Insurance coverage for crop loss due to natural calamities"
        },
        {
            "crop": "Sugarcane",
            "policy": "National Food Security Mission",
            "eligibility": "Farmers engaged in cultivation of identified crops",
            "benefit": "Financial and technical support to improve productivity"
        },
    ]

    with driver.session() as session:
        for item in data:
            session.run("""
                MERGE (c:Crop {name: $crop})
                MERGE (p:Policy {name: $policy})
                MERGE (e:Eligibility {criteria: $eligibility})
                MERGE (b:Benefit {description: $benefit})
                MERGE (c)-[:HAS_POLICY]->(p)
                MERGE (p)-[:HAS_ELIGIBILITY]->(e)
                MERGE (p)-[:PROVIDES_BENEFIT]->(b)
            """, parameters=item)

    print("✅ Knowledge Graph successfully populated with sample agricultural data!")

# --- Run the population script ---
if __name__ == "__main__":
    populate_knowledge_graph()
    driver.close()
