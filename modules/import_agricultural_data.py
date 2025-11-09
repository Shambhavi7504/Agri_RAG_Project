"""
Import Agricultural Data CSV to Neo4j Knowledge Graph (Fixed Version)
Handles encoding issues with column names
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
        print("   Make sure the CSV file is in the current directory")
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
        with open(csv_file, 'r', encoding='utf-8-sig') as f:  # utf-8-sig removes BOM
            reader = csv.DictReader(f)
            
            # Debug: Print column names
            columns = reader.fieldnames
            print(f"\n🔍 Found columns: {columns}\n")
            
            with driver.session() as session:
                for idx, row in enumerate(reader, 1):
                    try:
                        # Get commodity name
                        commodity_name = None
                        for key in row.keys():
                            if 'Commodity Name' in key:
                                commodity_name = row[key].strip()
                                break
                        
                        if not commodity_name:
                            print(f"⚠️  Row {idx}: No commodity name found")
                            continue
                        
                        # Get price (try different column name variations)
                        price = None
                        price_key = None
                        for key in row.keys():
                            if 'Price' in key:
                                price_key = key
                                try:
                                    price = float(row[key].strip())
                                    break
                                except:
                                    continue
                        
                        if price is None:
                            print(f"⚠️  Row {idx} ({commodity_name}): Could not parse price")
                            continue
                        
                        # Get other fields
                        trend = ''
                        forecast = ''
                        scheme = ''
                        policy = ''
                        subsidy = ''
                        year = 0
                        
                        for key, value in row.items():
                            if 'Supply-Demand' in key or 'Trend' in key:
                                trend = value.strip()
                            elif 'Forecast' in key:
                                forecast = value.strip()
                            elif 'Financial Program' in key:
                                scheme = value.strip()
                            elif 'Government Policy' in key and 'Year' not in key:
                                policy = value.strip()
                            elif 'Subsidy' in key:
                                subsidy = value.strip()
                            elif 'Published Year' in key or 'Year' in key:
                                try:
                                    year = int(value.strip())
                                except:
                                    year = 0
                        
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
                            print(f"   Processed {idx} rows...")
                        
                    except Exception as e:
                        print(f"⚠️  Row {idx} error: {e}")
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
    """
    Add additional useful metadata and relationships
    """
    driver = get_neo4j_driver()
    
    print("\n🔧 Adding additional metadata...")
    
    try:
        with driver.session() as session:
            # Categorize commodities
            cereals = ['Wheat', 'Rice', 'Maize', 'Barley', 'Bajra', 'Jowar', 'Ragi', 'Corn', 'Millets', 'Sorghum']
            pulses = ['Pulses', 'Lentils', 'Chickpeas', 'Peas']
            oilseeds = ['Mustard', 'Soybean', 'Groundnut', 'Sunflower', 'Sesame', 'Linseed', 
                       'Castor Seed', 'Flaxseed', 'Canola', 'Sesame Seeds', 'Palm Oil']
            spices = ['Turmeric', 'Black Pepper', 'Cardamom', 'Coriander', 'Cumin', 'Chili',
                     'Nutmeg', 'Cloves', 'Vanilla', 'Saffron']
            vegetables = ['Onion', 'Potato', 'Tomato', 'Brinjal', 'Carrot', 'Cabbage', 
                         'Cauliflower', 'Spinach', 'Lettuce', 'Pumpkin', 'Okra', 'Green Beans',
                         'Broccoli', 'Celery', 'Parsley', 'Basil', 'Bitter Gourd', 'Bottle Gourd',
                         'Ash Gourd', 'Zucchini', 'Beetroot', 'Sweet Potato', 'Radish', 'Turnip']
            fruits = ['Mango', 'Banana', 'Apple', 'Grapes', 'Pomegranate', 'Papaya', 'Guava',
                     'Pineapple', 'Watermelon', 'Peach', 'Plum', 'Strawberry', 'Kiwi', 
                     'Dragon Fruit', 'Jackfruit', 'Lychee', 'Date Palm', 'Gooseberry']
            cash_crops = ['Cotton', 'Sugar', 'Coffee', 'Tea', 'Rubber', 'Jute', 'Tobacco']
            
            categories = {
                'Cereal': cereals,
                'Pulse': pulses,
                'Oilseed': oilseeds,
                'Spice': spices,
                'Vegetable': vegetables,
                'Fruit': fruits,
                'Cash Crop': cash_crops
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