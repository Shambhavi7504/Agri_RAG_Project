import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load .env file
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("❌ GOOGLE_API_KEY missing in .env file!")

# Configure API
genai.configure(api_key=api_key)

# List available models
print("✅ Available Gemini models:")
for model in genai.list_models():
    print("-", model.name)
