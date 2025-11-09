"""
Query Router
Intelligently routes queries to KG, RAG, or both based on query type
"""

import re
from typing import Tuple, Literal


# Keywords that indicate a structured query (use KG)
KG_KEYWORDS = [
    'scheme', 'schemes', 'policy', 'policies', 'subsidy', 'subsidies',
    'eligibility', 'eligible', 'benefit', 'benefits', 'government',
    'state', 'available in', 'grown in', 'relationship', 'related to',
    'pm-kisan', 'pmfby', 'fasal bima', 'kisan credit', 'kcc',
    'crop insurance', 'what schemes', 'which schemes', 'list schemes'
]

# Keywords that indicate a document/context query (use RAG)
RAG_KEYWORDS = [
    'how to', 'what is', 'explain', 'describe', 'tell me about',
    'guide', 'process', 'step', 'method', 'technique', 'practice',
    'example', 'detail', 'information', 'learn', 'understand'
]


def classify_query(query: str) -> Literal['kg', 'rag', 'hybrid']:
    """
    Classify query type to determine routing strategy
    
    Args:
        query: User's question
        
    Returns:
        'kg': Use Knowledge Graph only
        'rag': Use RAG pipeline only
        'hybrid': Use both KG and RAG
    """
    query_lower = query.lower()
    
    # Count keyword matches
    kg_score = sum(1 for kw in KG_KEYWORDS if kw in query_lower)
    rag_score = sum(1 for kw in RAG_KEYWORDS if kw in query_lower)
    
    # Specific patterns for KG
    kg_patterns = [
        r'\bscheme[s]?\b.*\bfor\b',  # "schemes for wheat"
        r'\beligible\b.*\bfor\b',     # "eligible for subsidy"
        r'\bavailable\b.*\bin\b',     # "available in Punjab"
        r'\brelation.*\bbetween\b',   # "relation between crop and scheme"
        r'\blist\b.*\bscheme[s]?\b',  # "list schemes"
    ]
    
    for pattern in kg_patterns:
        if re.search(pattern, query_lower):
            kg_score += 2
    
    # Specific patterns for RAG
    rag_patterns = [
        r'\bhow\s+to\b',              # "how to grow rice"
        r'\bwhat\s+is\b',             # "what is sustainable farming"
        r'\bexplain\b',               # "explain crop rotation"
        r'\bstep[s]?\b',              # "steps for irrigation"
    ]
    
    for pattern in rag_patterns:
        if re.search(pattern, query_lower):
            rag_score += 2
    
    # Decision logic
    if kg_score > 0 and rag_score > 0:
        return 'hybrid'  # Both approaches might be useful
    elif kg_score > rag_score:
        return 'kg'
    elif rag_score > kg_score:
        return 'rag'
    else:
        return 'hybrid'  # Default to hybrid if uncertain


def route_query(query: str, rag_function, use_kg: bool = True) -> str:
    """
    Route query to appropriate backend(s) and combine results
    
    Args:
        query: User's question
        rag_function: RAG pipeline function
        use_kg: Whether to use Knowledge Graph (set False if KG unavailable)
        
    Returns:
        Combined answer string
    """
    
    # Classify the query
    query_type = classify_query(query)
    
    print(f"🔀 Query type: {query_type.upper()}")
    
    combined_answer = ""
    
    # Route based on classification
    if query_type == 'kg' and use_kg:
        # KG only
        try:
            from modules.kg_handler import query_neo4j
            kg_result = query_neo4j(query)
            
            if kg_result and not kg_result.startswith("❌"):
                combined_answer = f"{kg_result}\n\n"
                
                # Add context from RAG if KG found something
                print("📚 Enhancing with RAG context...")
                try:
                    rag_result = rag_function(query)
                    if rag_result and not rag_result.startswith("❌"):
                        combined_answer += f"\n📖 Additional Context:\n{rag_result}"
                except Exception as e:
                    print(f"⚠️ RAG enhancement failed: {e}")
            else:
                # KG found nothing, fall back to RAG
                print("⚠️ KG found nothing, using RAG...")
                combined_answer = rag_function(query)
                
        except Exception as e:
            print(f"❌ KG error: {e}")
            combined_answer = rag_function(query)
    
    elif query_type == 'rag':
        # RAG only
        combined_answer = rag_function(query)
    
    else:  # hybrid or KG unavailable
        # Try both
        kg_answer = ""
        
        if use_kg:
            try:
                from modules.kg_handler import query_neo4j
                kg_result = query_neo4j(query)
                
                if kg_result and not kg_result.startswith("❌") and not kg_result.startswith("📊 No"):
                    kg_answer = kg_result
            except Exception as e:
                print(f"⚠️ KG unavailable: {e}")
        
        # Always get RAG answer
        rag_answer = rag_function(query)
        
        # Combine results
        if kg_answer and rag_answer:
            combined_answer = f"{kg_answer}\n\n{rag_answer}"
        elif kg_answer:
            combined_answer = kg_answer
        else:
            combined_answer = rag_answer
    
    return combined_answer if combined_answer else "❌ No answer found."


def extract_entities(query: str) -> dict:
    """
    Extract potential entities from query (simple pattern matching)
    
    Args:
        query: User's question
        
    Returns:
        Dictionary with extracted entities
    """
    entities = {
        'crops': [],
        'schemes': [],
        'states': [],
    }
    
    # Common crop names
    crops = ['rice', 'wheat', 'cotton', 'sugarcane', 'maize', 'barley', 'soybean', 'mustard']
    # Common schemes
    schemes = ['pm-kisan', 'pmfby', 'fasal bima', 'kisan credit card', 'kcc']
    # Common states
    states = ['punjab', 'haryana', 'uttar pradesh', 'up', 'maharashtra', 'karnataka', 'tamil nadu']
    
    query_lower = query.lower()
    
    for crop in crops:
        if crop in query_lower:
            entities['crops'].append(crop.title())
    
    for scheme in schemes:
        if scheme in query_lower:
            entities['schemes'].append(scheme.upper() if scheme in ['kcc', 'up'] else scheme.title())
    
    for state in states:
        if state in query_lower:
            entities['states'].append(state.title())
    
    return entities