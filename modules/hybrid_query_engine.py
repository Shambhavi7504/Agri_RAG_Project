from modules.neo4j_connection import get_neo4j_driver
from rag_pipeline import load_rag_pipeline

def is_structured_query(query: str) -> bool:
    structured_keywords = ["show", "find", "list", "related to", "connected to", "crop", "disease", "soil", "region"]
    return any(keyword in query.lower() for keyword in structured_keywords)

def run_neo4j_query(driver, query):
    cypher_query = f"""
    MATCH (n)-[r]->(m)
    WHERE toLower(n.name) CONTAINS toLower('{query}')
       OR toLower(m.name) CONTAINS toLower('{query}')
    RETURN n.name AS Source, type(r) AS Relation, m.name AS Target
    """
    with driver.session() as session:
        result = session.run(cypher_query)
        data = [record.data() for record in result]
    return data

def run_hybrid_query(user_query):
    driver = get_neo4j_driver()
    qa = load_rag_pipeline()

    if is_structured_query(user_query):
        print("🧩 Detected Structured Query → Using Neo4j KG")
        result = run_neo4j_query(driver, user_query)
        if not result:
            return "No matching structured data found in the KG."
        return result
    else:
        print("📚 Detected Unstructured Query → Using RAG")
        response = qa.run(user_query)
        return response
