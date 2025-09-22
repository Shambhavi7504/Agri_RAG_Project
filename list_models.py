import google.generativeai as genai

genai.configure(api_key="AIzaSyC8y3S8AteF8JCTHzlgHep27cAlb_2tWUY")

models = genai.list_models()
for m in models:
    print(m.name)
