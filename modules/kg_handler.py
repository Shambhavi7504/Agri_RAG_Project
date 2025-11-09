'''from .neo4j_connection import get_neo4j_driver

def query_neo4j(question: str):
    driver = get_neo4j_driver()
    if not driver:
        return "Neo4j connection unavailable."

    # Simple Cypher query example (can be improved later)
    cypher = f"""
    MATCH (n)-[r]->(m)
    WHERE toLower(n.name) CONTAINS toLower('{question}')
       OR toLower(m.name) CONTAINS toLower('{question}')
    RETURN n.name AS Source, type(r) AS Relation, m.name AS Target
    LIMIT 10
    """
    with driver.session() as session:
        results = session.run(cypher)
        data = [record.data() for record in results]

    if not data:
        return "No structured data found in the Knowledge Graph."
    else:
        formatted = "\n".join([f"{d['Source']} --[{d['Relation']}]→ {d['Target']}" for d in data])
        return formatted'''
        
from .neo4j_connection import get_neo4j_driver
import re

def query_neo4j(question: str):
    driver = get_neo4j_driver()
    if not driver:
        return "❌ Neo4j connection unavailable."

    # Normalize and extract main keyword (like 'pmfby', 'pm-kisan', etc.)
    q = question.lower()
    keywords = re.findall(r'pm[- ]?kisan|pmfby|fasal bima|kcc|scheme|subsidy|policy|rice|wheat|maize|cotton', q)

    if keywords:
        keyword = keywords[0]
    else:
        # fallback: take the most significant word
        words = [w for w in re.findall(r'\b[a-z]{3,}\b', q) if w not in ["what", "is", "about", "scheme", "schemes", "for", "the", "a", "of"]]
        keyword = words[0] if words else q

    print(f"🔍 Extracted keyword for KG: {keyword}")

    cypher = f"""
    MATCH (n)-[r]->(m)
    WHERE toLower(n.name) CONTAINS toLower('{keyword}')
       OR toLower(m.name) CONTAINS toLower('{keyword}')
    RETURN n.name AS Source, type(r) AS Relation, m.name AS Target
    LIMIT 10
    """

    with driver.session() as session:
        results = session.run(cypher)
        data = [record.data() for record in results]

    if not data:
        # Try to also find scheme descriptions if no relationships found
        cypher_fallback = f"""
        MATCH (s:Scheme)
        WHERE toLower(s.name) CONTAINS toLower('{keyword}')
        RETURN s.name AS Scheme, s.description AS Description
        LIMIT 3
        """
        with driver.session() as session:
            fallback_results = session.run(cypher_fallback)
            fallback_data = [record.data() for record in fallback_results]

        if fallback_data:
            formatted = "\n".join([f"🏛️ {d['Scheme']}: {d.get('Description', 'No description')}" for d in fallback_data])
            return formatted
        else:
            return "📊 No structured data found in the Knowledge Graph."
    else:
        formatted = "\n".join([f"{d['Source']} --[{d['Relation']}]→ {d['Target']}" for d in data])
        return formatted

