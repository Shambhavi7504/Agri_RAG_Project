"""
Test Knowledge Graph Integration
Tests Neo4j connection, sample data creation, and query routing
"""

print("🧪 Testing Knowledge Graph Integration...\n")

# Test 1: Neo4j Connection
print("=" * 60)
print("Test 1: Neo4j Connection")
print("=" * 60)

try:
    from modules.neo4j_connection import test_neo4j_connection, get_database_stats, create_sample_agriculture_graph
    
    if test_neo4j_connection():
        print("✅ Neo4j connection successful!\n")
        
        # Get database stats
        stats = get_database_stats()
        if stats:
            print("📊 Database Statistics:")
            print(f"   Total Nodes: {stats.get('total_nodes', 0)}")
            print(f"   Total Relationships: {stats.get('total_relationships', 0)}")
            
            if stats.get('total_nodes', 0) == 0:
                print("\n📦 Database is empty. Creating sample data...")
                create_sample_agriculture_graph()
                stats = get_database_stats()
                print(f"\n✅ Sample data created!")
                print(f"   Total Nodes: {stats.get('total_nodes', 0)}")
                print(f"   Total Relationships: {stats.get('total_relationships', 0)}")
    else:
        print("❌ Neo4j connection failed!")
        print("   Make sure Neo4j is running and credentials in .env are correct")
        exit(1)
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print()

# Test 2: Knowledge Graph Queries
print("=" * 60)
print("Test 2: Knowledge Graph Queries")
print("=" * 60)

try:
    from modules.kg_handler import query_neo4j, get_related_schemes
    
    # Test basic query
    print("\n🔍 Query: 'rice'")
    result = query_neo4j("rice")
    print(result)
    
    print("\n🔍 Query: 'PM-KISAN'")
    result = query_neo4j("PM-KISAN")
    print(result)
    
    # Test specific functions
    print("\n🔍 Getting schemes for 'Rice':")
    schemes = get_related_schemes("Rice")
    if schemes:
        for scheme in schemes:
            print(f"   • {scheme['scheme_name']}: {scheme.get('benefit', 'N/A')}")
    else:
        print("   No schemes found")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 3: Query Classification
print("=" * 60)
print("Test 3: Query Classification")
print("=" * 60)

try:
    from modules.query_router import classify_query
    
    test_queries = [
        "What schemes are available for wheat farmers?",
        "How to grow rice organically?",
        "Tell me about PM-KISAN eligibility",
        "Explain crop rotation techniques",
        "Which schemes are available in Punjab?",
    ]
    
    for query in test_queries:
        query_type = classify_query(query)
        print(f"   Query: '{query}'")
        print(f"   Type: {query_type.upper()}\n")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 4: Full Integration with RAG
print("=" * 60)
print("Test 4: Full RAG + KG Integration")
print("=" * 60)

try:
    from modules.rag_pipeline import build_hybrid_rag
    from modules.query_router import route_query
    
    print("\n🔧 Building RAG pipeline...")
    rag, memory = build_hybrid_rag()
    print("✅ RAG pipeline ready!\n")
    
    test_query = "What schemes are available for rice farmers?"
    print(f"🔍 Query: '{test_query}'\n")
    
    answer = route_query(test_query, rag, use_kg=True)
    
    print("\n🤖 Answer:")
    print("-" * 60)
    print(answer)
    print("-" * 60)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("✅ All tests completed!")
print("=" * 60)