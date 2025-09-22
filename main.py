from modules.rag_pipeline import build_hybrid_rag
from modules.scraper import scrape_web_results

def main():
    # Initialize RAG pipeline with PDF + SerpAPI + memory
    rag, memory = build_hybrid_rag()

    print(" Agriculture Gemini Hybrid RAG Chatbot")
    print("Type 'exit' or 'quit' to stop the chatbot.\n")

    while True:
        query = input("You: ")
        if query.lower() in ["exit", "quit"]:
            print("👋 Goodbye!")
            break

        # Get answer from hybrid RAG
        answer = rag(query)

        # Detect source and display cleanly
        if answer.startswith(" From PDFs:"):
            print("\n Answer from PDFs:\n")
            print(answer.replace(" From PDFs:", "").strip())
        elif answer.startswith(" From Web (SerpAPI):"):
            print("\n Answer from Web (SerpAPI):\n")
            print(answer.replace(" From Web (SerpAPI):", "").strip())
        else:
            print("\n No answer found:\n")
            print(answer)

        print("\n" + "-"*60 + "\n")


if __name__ == "__main__":
    main()
