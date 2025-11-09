"""
Neo4j Connection Manager
Handles Neo4j database connections for the Knowledge Graph
Uses Google Gemini embeddings for vector similarity
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Global driver instance (singleton pattern)
_neo4j_driver = None
_embeddings_model = None


def get_neo4j_driver():
    """
    Get or create Neo4j driver instance (singleton)
    
    Returns:
        Neo4j driver instance or None if connection fails
    """
    global _neo4j_driver
    
    if _neo4j_driver is not None:
        return _neo4j_driver
    
    try:
        from neo4j import GraphDatabase
        
        # Get credentials from environment
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        username = os.getenv("NEO4J_USERNAME", "neo4j")
        password = os.getenv("NEO4J_PASSWORD")
        
        if not password:
            print("⚠️ NEO4J_PASSWORD not set in .env file")
            return None
        
        # Create driver
        _neo4j_driver = GraphDatabase.driver(uri, auth=(username, password))
        
        # Test connection
        with _neo4j_driver.session() as session:
            result = session.run("RETURN 1 AS test")
            result.single()
        
        print(f"✅ Connected to Neo4j at {uri}")
        return _neo4j_driver
        
    except ImportError:
        print("❌ neo4j package not installed. Run: pip install neo4j")
        return None
    except Exception as e:
        print(f"❌ Failed to connect to Neo4j: {e}")
        print(f"   URI: {uri}")
        print(f"   Username: {username}")
        print("   Check your NEO4J_* environment variables in .env")
        return None


def close_neo4j_driver():
    """
    Close the Neo4j driver connection
    """
    global _neo4j_driver
    
    if _neo4j_driver is not None:
        try:
            _neo4j_driver.close()
            print("✅ Neo4j connection closed")
        except Exception as e:
            print(f"⚠️ Error closing Neo4j connection: {e}")
        finally:
            _neo4j_driver = None


def test_neo4j_connection() -> bool:
    """
    Test if Neo4j connection is working
    
    Returns:
        True if connection successful, False otherwise
    """
    driver = get_neo4j_driver()
    
    if not driver:
        return False
    
    try:
        with driver.session() as session:
            result = session.run("RETURN 1 AS test")
            result.single()
        print("✅ Neo4j connection test passed")
        return True
    except Exception as e:
        print(f"❌ Neo4j connection test failed: {e}")
        return False


def get_database_stats() -> dict:
    """
    Get statistics about the Neo4j database
    
    Returns:
        Dictionary with node counts, relationship counts, etc.
    """
    driver = get_neo4j_driver()
    
    if not driver:
        return {}
    
    stats = {}
    
    try:
        with driver.session() as session:
            # Count nodes by label
            result = session.run("""
                MATCH (n)
                RETURN labels(n) AS labels, count(n) AS count
            """)
            
            node_counts = {}
            for record in result:
                label = record['labels'][0] if record['labels'] else 'Unlabeled'
                node_counts[label] = record['count']
            
            stats['nodes'] = node_counts
            
            # Count relationships by type
            result = session.run("""
                MATCH ()-[r]->()
                RETURN type(r) AS type, count(r) AS count
            """)
            
            rel_counts = {}
            for record in result:
                rel_counts[record['type']] = record['count']
            
            stats['relationships'] = rel_counts
            
            # Total counts
            total_nodes = session.run("MATCH (n) RETURN count(n) AS count").single()['count']
            total_rels = session.run("MATCH ()-[r]->() RETURN count(r) AS count").single()['count']
            
            stats['total_nodes'] = total_nodes
            stats['total_relationships'] = total_rels
            
    except Exception as e:
        print(f"❌ Error getting database stats: {e}")
    
    return stats


def create_sample_agriculture_graph():
    """
    Create a sample agriculture knowledge graph if the database is empty
    This populates the KG with crops, schemes, and relationships
    """
    driver = get_neo4j_driver()
    
    if not driver:
        print("❌ Cannot create sample graph - no driver available")
        return False
    
    try:
        with driver.session() as session:
            # Check if data already exists
            result = session.run("MATCH (n) RETURN count(n) AS count")
            count = result.single()['count']
            
            if count > 0:
                print(f"ℹ️ Database already contains {count} nodes. Skipping sample data creation.")
                return True
            
            print("📊 Creating sample agriculture knowledge graph...")
            
            # Create crops
            session.run("""
                CREATE (rice:Crop {name: 'Rice', category: 'Cereal', season: 'Kharif'})
                CREATE (wheat:Crop {name: 'Wheat', category: 'Cereal', season: 'Rabi'})
                CREATE (cotton:Crop {name: 'Cotton', category: 'Cash Crop', season: 'Kharif'})
                CREATE (sugarcane:Crop {name: 'Sugarcane', category: 'Cash Crop', season: 'Year-round'})
                
                CREATE (pmkisan:Scheme {
                    name: 'PM-KISAN', 
                    description: 'Income support to farmer families',
                    benefit: '₹6000 per year in three installments',
                    type: 'Central'
                })
                
                CREATE (fasal:Scheme {
                    name: 'Pradhan Mantri Fasal Bima Yojana',
                    description: 'Crop insurance scheme',
                    benefit: 'Insurance coverage for crop loss',
                    type: 'Central'
                })
                
                CREATE (kcc:Scheme {
                    name: 'Kisan Credit Card',
                    description: 'Credit facility for farmers',
                    benefit: 'Easy credit access at low interest',
                    type: 'Central'
                })
                
                CREATE (punjab:State {name: 'Punjab', region: 'North'})
                CREATE (up:State {name: 'Uttar Pradesh', region: 'North'})
                CREATE (maharashtra:State {name: 'Maharashtra', region: 'West'})
                
                CREATE (rice)-[:ELIGIBLE_FOR]->(pmkisan)
                CREATE (wheat)-[:ELIGIBLE_FOR]->(pmkisan)
                CREATE (cotton)-[:ELIGIBLE_FOR]->(pmkisan)
                CREATE (sugarcane)-[:ELIGIBLE_FOR]->(pmkisan)
                
                CREATE (rice)-[:COVERED_BY]->(fasal)
                CREATE (wheat)-[:COVERED_BY]->(fasal)
                CREATE (cotton)-[:COVERED_BY]->(fasal)
                
                CREATE (rice)-[:GROWN_IN]->(punjab)
                CREATE (wheat)-[:GROWN_IN]->(punjab)
                CREATE (wheat)-[:GROWN_IN]->(up)
                CREATE (cotton)-[:GROWN_IN]->(maharashtra)
                CREATE (sugarcane)-[:GROWN_IN]->(up)
                CREATE (sugarcane)-[:GROWN_IN]->(maharashtra)
                
                CREATE (pmkisan)-[:AVAILABLE_IN]->(punjab)
                CREATE (pmkisan)-[:AVAILABLE_IN]->(up)
                CREATE (pmkisan)-[:AVAILABLE_IN]->(maharashtra)
                CREATE (fasal)-[:AVAILABLE_IN]->(punjab)
                CREATE (fasal)-[:AVAILABLE_IN]->(up)
                CREATE (fasal)-[:AVAILABLE_IN]->(maharashtra)
                CREATE (kcc)-[:AVAILABLE_IN]->(punjab)
                CREATE (kcc)-[:AVAILABLE_IN]->(up)
                CREATE (kcc)-[:AVAILABLE_IN]->(maharashtra)
            """)
            
            print("✅ Sample agriculture knowledge graph created successfully!")
            print("   - 4 Crops (Rice, Wheat, Cotton, Sugarcane)")
            print("   - 3 Schemes (PM-KISAN, PMFBY, KCC)")
            print("   - 3 States (Punjab, UP, Maharashtra)")
            print("   - Multiple relationships")
            
            return True
            
    except Exception as e:
        print(f"❌ Error creating sample graph: {e}")
        return False


# Cleanup on module exit
import atexit
atexit.register(close_neo4j_driver)