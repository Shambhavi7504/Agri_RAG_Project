"""
Import Agricultural Data CSV to Neo4j Knowledge Graph (FINAL WORKING VERSION)
"""

import csv
import os
from modules.neo4j_connection import get_neo4j_driver, test_neo4j_connection


def clear_database():
    """Clear all existing data from the database"""
    driver = get_neo4j_driver()
    
    if not driver:
        print("❌ Cannot connect to Neo4j")
        return False
    
    response = input("⚠️  This will DELETE ALL data in Neo4j. Continue? (yes/no): ")
    if response.lower() != 'yes':
        print("Cancelled.")
        return False
    
    try:
        with driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("✅ Database cleared")
            return True
    except Exception as e:
        print(f"❌ Error clearing database: {e}")
        return False


def import_agricultural_data(csv_file="Updated_Agricultural_Data.csv"):
    """
    Import data from Updated_Agricultural_Data.csv
    Creates: Commodity, Scheme, Policy, Subsidy nodes and relationships
    """
    driver = get_neo4j_driver()
    
    if not driver:
        print("❌ Cannot connect to Neo4j")
        return False
    
    if not os.path.exists(csv_file):
        print(f"❌ File not found: {csv_file}")
        return False
    
    print(f"\n📊 Importing data from {csv_file}...")
    
    commodities_created = 0
    schemes_created = 0
    policies_created = 0
    subsidies_created = 0
    relationships_created = 0
    
    # Track unique schemes, policies, and subsidies
    unique_schemes = set()
    unique_policies = set()
    unique_subsidies = set()
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            with driver.session() as session:
                for idx, row in enumerate(reader, 1):
                    try:
                        # Extract data using exact column names
                        commodity_name = row['Commodity Name'].strip()
                        price = float(row['Commodity Price (₹/kg)'].strip())
                        trend = row['Supply-Demand Trend'].strip()
                        forecast = row['Market Forecast'].strip()
                        scheme = row['Financial Program'].strip()
                        policy = row['Government Policy'].strip()
                        subsidy = row['Government Subsidy'].strip()
                        year = int(row['Government Policy Published Year'].strip())
                        
                        # Create Commodity node
                        session.run("""
                            MERGE (c:Commodity {name: $name})
                            SET c.price = $price,
                                c.trend = $trend,
                                c.forecast = $forecast
                        """, name=commodity_name, price=price, trend=trend, forecast=forecast)
                        commodities_created += 1
                        
                        # Create Scheme node (unique)
                        if scheme and scheme not in unique_schemes:
                            session.run("""
                                MERGE (s:Scheme {name: $name})
                                SET s.year = $year
                            """, name=scheme, year=year)
                            unique_schemes.add(scheme)
                            schemes_created += 1
                        
                        # Create Policy node (unique)
                        if policy and policy not in unique_policies:
                            session.run("""
                                MERGE (p:Policy {name: $name})
                                SET p.year = $year
                            """, name=policy, year=year)
                            unique_policies.add(policy)
                            policies_created += 1
                        
                        # Create Subsidy node (unique)
                        if subsidy and subsidy not in unique_subsidies:
                            session.run("""
                                MERGE (sub:Subsidy {name: $name})
                            """, name=subsidy)
                            unique_subsidies.add(subsidy)
                            subsidies_created += 1
                        
                        # Create relationships
                        if scheme:
                            session.run("""
                                MATCH (c:Commodity {name: $commodity})
                                MATCH (s:Scheme {name: $scheme})
                                MERGE (c)-[:COVERED_BY]->(s)
                            """, commodity=commodity_name, scheme=scheme)
                            relationships_created += 1
                        
                        if policy:
                            session.run("""
                                MATCH (c:Commodity {name: $commodity})
                                MATCH (p:Policy {name: $policy})
                                MERGE (c)-[:REGULATED_BY]->(p)
                            """, commodity=commodity_name, policy=policy)
                            relationships_created += 1
                        
                        if subsidy:
                            session.run("""
                                MATCH (c:Commodity {name: $commodity})
                                MATCH (sub:Subsidy {name: $subsidy})
                                MERGE (c)-[:RECEIVES]->(sub)
                            """, commodity=commodity_name, subsidy=subsidy)
                            relationships_created += 1
                        
                        # Link scheme to policy
                        if scheme and policy:
                            session.run("""
                                MATCH (s:Scheme {name: $scheme})
                                MATCH (p:Policy {name: $policy})
                                MERGE (s)-[:IMPLEMENTS]->(p)
                            """, scheme=scheme, policy=policy)
                            relationships_created += 1
                        
                        # Link scheme to subsidy
                        if scheme and subsidy:
                            session.run("""
                                MATCH (s:Scheme {name: $scheme})
                                MATCH (sub:Subsidy {name: $subsidy})
                                MERGE (s)-[:PROVIDES]->(sub)
                            """, scheme=scheme, subsidy=subsidy)
                            relationships_created += 1
                        
                        # Progress indicator
                        if idx % 20 == 0:
                            print(f"   ✅ Processed {idx} commodities...")
                        
                    except Exception as e:
                        print(f"⚠️  Row {idx} ({commodity_name}): {e}")
                        continue
        
        print(f"\n✅ Import completed successfully!")
        print(f"\n📊 Created:")
        print(f"   • Commodities: {commodities_created}")
        print(f"   • Schemes: {schemes_created}")
        print(f"   • Policies: {policies_created}")
        print(f"   • Subsidies: {subsidies_created}")
        print(f"   • Relationships: {relationships_created}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error importing data: {e}")
        import traceback
        traceback.print_exc()
        return False


def add_additional_metadata():
    """Add category metadata to commodities"""
    driver = get_neo4j_driver()
    
    print("\n🔧 Adding commodity categories...")
    
    try:
        with driver.session() as session:
            # Categorize commodities
            categories = {
                'Cereal': ['Wheat', 'Rice', 'Maize', 'Barley', 'Bajra', 'Jowar', 'Ragi', 'Corn', 'Millets', 'Sorghum'],
                'Pulse': ['Pulses', 'Lentils', 'Chickpeas', 'Peas'],
                'Oilseed': ['Mustard', 'Soybean', 'Groundnut', 'Sunflower', 'Sesame', 'Linseed', 
                           'Castor Seed', 'Flaxseed', 'Canola', 'Sesame Seeds', 'Palm Oil'],
                'Spice': ['Turmeric', 'Black Pepper', 'Cardamom', 'Coriander', 'Cumin', 'Chili',
                         'Nutmeg', 'Cloves', 'Vanilla', 'Saffron', 'Garlic'],
                'Vegetable': ['Onion', 'Potato', 'Tomato', 'Brinjal', 'Carrot', 'Cabbage', 
                             'Cauliflower', 'Spinach', 'Lettuce', 'Pumpkin', 'Okra', 'Green Beans',
                             'Broccoli', 'Celery', 'Parsley', 'Basil', 'Bitter Gourd', 'Bottle Gourd',
                             'Ash Gourd', 'Zucchini', 'Beetroot', 'Sweet Potato', 'Radish', 'Turnip'],
                'Fruit': ['Mango', 'Banana', 'Apple', 'Grapes', 'Pomegranate', 'Papaya', 'Guava',
                         'Pineapple', 'Watermelon', 'Peach', 'Plum', 'Strawberry', 'Kiwi', 
                         'Dragon Fruit', 'Jackfruit', 'Lychee', 'Date Palm', 'Gooseberry'],
                'Cash Crop': ['Cotton', 'Sugar', 'Coffee', 'Tea', 'Rubber', 'Jute', 'Tobacco'],
                'Nuts': ['Coconut', 'Cashew Nut', 'Arecanut', 'Almond', 'Walnut'],
                'Herbs': ['Mushrooms', 'Bamboo', 'Betel Leaf', 'Aloe Vera', 'Neem', 'Tulsi'],
                'Oil Palm': ['Olives']
            }
            
            for category, commodities in categories.items():
                for commodity in commodities:
                    session.run("""
                        MATCH (c:Commodity {name: $name})
                        SET c.category = $category
                    """, name=commodity, category=category)
            
            print("✅ Added commodity categories")
            
    except Exception as e:
        print(f"⚠️  Error adding metadata: {e}")


def main():
    """Main import function"""
    print("=" * 70)
    print("🌾 Agricultural Data Import to Neo4j Knowledge Graph")
    print("=" * 70)
    print()
    
    # Check connection
    if not test_neo4j_connection():
        print("❌ Cannot connect to Neo4j. Please check:")
        print("   1. Neo4j is running")
        print("   2. NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD in .env")
        return
    
    print("\n📋 Import Options:")
    print("1. Clear database and import fresh")
    print("2. Add to existing data")
    print("3. Cancel")
    
    choice = input("\nYour choice (1/2/3): ").strip()
    
    if choice == '3':
        print("Cancelled.")
        return
    
    if choice == '1':
        if not clear_database():
            return
    
    # Import the data
    if import_agricultural_data():
        # Add metadata
        add_additional_metadata()
        
        # Show final stats
        print("\n" + "=" * 70)
        from modules.neo4j_connection import get_database_stats
        stats = get_database_stats()
        
        print("\n📊 Final Database Statistics:")
        print(f"   Total Nodes: {stats.get('total_nodes', 0)}")
        print(f"   Total Relationships: {stats.get('total_relationships', 0)}")
        
        if stats.get('nodes'):
            print("\n   Nodes by Type:")
            for label, count in sorted(stats['nodes'].items()):
                print(f"      {label}: {count}")
        
        if stats.get('relationships'):
            print("\n   Relationships by Type:")
            for rel_type, count in sorted(stats['relationships'].items()):
                print(f"      {rel_type}: {count}")
        
        print("\n" + "=" * 70)
        print("✅ Knowledge Graph ready!")
        print("🚀 Run: python main.py to start the chatbot")
        print("=" * 70)


if __name__ == "__main__":
    main()