from modules.rag_pipeline import build_hybrid_rag
from nltk.translate.bleu_score import sentence_bleu
from rouge_score import rouge_scorer
from sentence_transformers import SentenceTransformer, util

# ------------------ Build RAG ------------------
rag, memory = build_hybrid_rag()

# ------------------ Test Data ------------------
test_data = [
    {"query": "What is the PM-Kisan scheme?", "expected": "The PM-Kisan scheme provides income support to farmers under the government initiative."},
    {"query": "How to apply for a crop loan?", "expected": "Farmers can apply for crop loans through their local banks by submitting necessary documents."},
    {"query": "What subsidies are available for wheat farming?", "expected": "Wheat farmers can get subsidies on seeds, fertilizers, and machinery under government schemes."},
]

# ------------------ Initialize Scorers ------------------
rouge = rouge_scorer.RougeScorer(['rouge1', 'rougeL'], use_stemmer=True)
semantic_model = SentenceTransformer("all-MiniLM-L6-v2")

# ------------------ Evaluation ------------------
bleu_scores = []
rouge1_f_scores = []
semantic_sims = []

for item in test_data:
    query = item["query"]
    expected = item["expected"]
    
    predicted = rag(query)  # Call your RAG function
    
    # --- BLEU ---
    reference = [expected.split()]
    candidate = predicted.split()
    bleu_scores.append(sentence_bleu(reference, candidate))
    
    # --- ROUGE ---
    rscore = rouge.score(expected, predicted)
    rouge1_f_scores.append(rscore['rouge1'].fmeasure)
    
    # --- Semantic similarity ---
    emb_expected = semantic_model.encode(expected, convert_to_tensor=True)
    emb_predicted = semantic_model.encode(predicted, convert_to_tensor=True)
    sim = util.pytorch_cos_sim(emb_expected, emb_predicted).item()
    semantic_sims.append(sim)
    
    # --- Print each QA result ---
    print(f"\nQuery: {query}")
    print(f"Expected: {expected}")
    print(f"Predicted: {predicted}")
    #print(f"BLEU: {bleu_scores[-1]:.4f}, ROUGE-1 F1: {rouge1_f_scores[-1]:.4f}, Semantic Sim: {semantic_sims[-1]:.4f}")

# ------------------ Summary ------------------
print("\n========== SUMMARY ==========")
#print(f"Average BLEU score: {sum(bleu_scores)/len(bleu_scores):.4f}")
print(f"Average ROUGE-1 F1: {sum(rouge1_f_scores)/len(rouge1_f_scores):.4f}")
print(f"Average Semantic Similarity: {sum(semantic_sims)/len(semantic_sims):.4f}")
