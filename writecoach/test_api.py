# test_gemini.py
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GOOGLE_API_KEY')
print(f"API key loaded: {'Yes' if api_key else 'No'}")

if api_key:
    genai.configure(api_key=api_key)
    # Use the correct model name
    model = genai.GenerativeModel('gemini-1.5-flash')  # Changed from 'gemini-pro'
    response = model.generate_content("Say hello!")
    print(response.text)