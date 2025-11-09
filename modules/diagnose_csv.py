"""
Diagnose CSV file format and encoding
"""

import csv

csv_file = "Updated_Agricultural_Data.csv"

print("=" * 70)
print("🔍 CSV File Diagnostic")
print("=" * 70)

# Try different encodings
encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']

for encoding in encodings:
    try:
        print(f"\n📖 Trying encoding: {encoding}")
        print("-" * 70)
        
        with open(csv_file, 'r', encoding=encoding) as f:
            # Read first line to check for BOM
            first_char = f.read(1)
            f.seek(0)
            
            if first_char == '\ufeff':
                print("   ⚠️  BOM detected")
            
            reader = csv.DictReader(f)
            
            # Print column names
            print(f"\n   Column names found:")
            for idx, col in enumerate(reader.fieldnames, 1):
                # Show the actual bytes
                print(f"   {idx}. '{col}' (length: {len(col)})")
                print(f"      Bytes: {col.encode(encoding)[:50]}")
            
            # Read first row
            first_row = next(reader)
            print(f"\n   First row data:")
            for key, value in first_row.items():
                print(f"   {key[:30]}: {value}")
            
            print(f"\n   ✅ Successfully read with {encoding}")
            break
            
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        continue

print("\n" + "=" * 70)