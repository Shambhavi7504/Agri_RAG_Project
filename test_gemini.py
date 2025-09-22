import google.generativeai as genai

genai.configure(api_key="AIzaSyC8y3S8AteF8JCTHzlgHep27cAlb_2tWUY")  # or use os.getenv if using dotenv

model = genai.GenerativeModel("models/gemini-1.5-pro")
response = model.generate_content("Tell me about agriculture policies in India.")

print(response.text)
