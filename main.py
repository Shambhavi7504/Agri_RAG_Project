"""
Agriculture Gemini Hybrid RAG + Knowledge Graph Chatbot
Main entry point with intelligent query routing
"""

print("🚀 Starting Agriculture RAG + KG Chatbot...\n")

try:
    from modules.rag_pipeline import build_hybrid_rag
    from modules.query_router import route_query
    from modules.neo4j_connection import test_neo4j_connection, create_sample_agriculture_graph, get_database_stats
    print("✅ Modules imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    exit(1)


def main():
    """Main chatbot loop with KG integration"""
    
    print("\n🔧 Initializing systems...")
    
    # Initialize RAG pipeline
    try:
        rag, memory = build_hybrid_rag()
        print("✅ RAG pipeline initialized!")
    except Exception as e:
        print(f"❌ Failed to initialize RAG pipeline: {e}")
        return
    
    # Check Neo4j connection
    kg_available = False
    try:
        print("\n🔗 Checking Neo4j Knowledge Graph...")
        if test_neo4j_connection():
            kg_available = True
            print("✅ Knowledge Graph connected!")
            
            # Check if database has data
            stats = get_database_stats()
            if stats.get('total_nodes', 0) == 0:
                print("\n📦 Creating sample agriculture data...")
                create_sample_agriculture_graph()
                print("✅ Sample data ready!")
            else:
                print(f"   Nodes: {stats.get('total_nodes', 0)}, Relationships: {stats.get('total_relationships', 0)}")
        else:
            print("⚠️ Knowledge Graph unavailable - continuing with RAG only")
            print("   (To enable KG: Install Neo4j and configure NEO4J_* in .env)")
    except Exception as e:
        print(f"⚠️ Knowledge Graph unavailable: {e}")
        print("   Continuing with RAG only...")

    print("\n" + "=" * 70)
    print("🌾 Agriculture Gemini Hybrid RAG + Knowledge Graph Chatbot")
    print("=" * 70)
    print("💡 Features:")
    if kg_available:
        print("   ✅ PDF Document Search")
        print("   ✅ Web Search (SerpAPI)")
        print("   ✅ Knowledge Graph (Neo4j)")
        print("   ✅ Intelligent Query Routing")
    else:
        print("   ✅ PDF Document Search")
        print("   ✅ Web Search (SerpAPI)")
        print("   ⚠️  Knowledge Graph (Disabled)")
    print("\n💬 Commands:")
    print("   'exit' or 'quit' - Exit the chatbot")
    print("   'history' - View conversation history")
    if kg_available:
        print("   'stats' - View Knowledge Graph statistics")
    print("=" * 70)
    print()

    while True:
        try:
            query = input("You: ").strip()
            
            if not query:
                continue
                
            if query.lower() in ["exit", "quit"]:
                print("\n👋 Goodbye! Thanks for using the chatbot!")
                break
            
            if query.lower() == "history":
                print("\n📚 Conversation History:")
                print("=" * 60)
                history = memory.get_history()
                if not history:
                    print("No conversation history yet.")
                else:
                    for idx, item in enumerate(history, 1):
                        print(f"\n{idx}. Q: {item['input']}")
                        print(f"   A: {item['output'][:200]}...")
                print("=" * 60)
                print()
                continue
            
            if query.lower() == "stats" and kg_available:
                print("\n📊 Knowledge Graph Statistics:")
                print("=" * 60)
                stats = get_database_stats()
                
                print(f"Total Nodes: {stats.get('total_nodes', 0)}")
                print(f"Total Relationships: {stats.get('total_relationships', 0)}")
                
                if stats.get('nodes'):
                    print("\nNodes by Type:")
                    for label, count in stats['nodes'].items():
                        print(f"   {label}: {count}")
                
                if stats.get('relationships'):
                    print("\nRelationships by Type:")
                    for rel_type, count in stats['relationships'].items():
                        print(f"   {rel_type}: {count}")
                
                print("=" * 60)
                print()
                continue

            # Process query with intelligent routing
            print("\n💭 Processing...\n")
            
            if kg_available:
                # Use intelligent routing
                answer = route_query(query, rag, use_kg=True)
            else:
                # RAG only
                answer = rag(query)

            # Display the answer
            print("\n🤖 Answer:")
            print("-" * 60)
            print(answer)
            print("-" * 60)
            print()

        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            print()


if __name__ == "__main__":
    main()