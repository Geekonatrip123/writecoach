# download_nltk_fix.py
import nltk
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Download with retry
max_retries = 3
for i in range(max_retries):
    try:
        nltk.download('punkt')
        nltk.download('punkt_tab')
        nltk.download('averaged_perceptron_tagger')
        print("NLTK data downloaded successfully!")
        break
    except Exception as e:
        print(f"Attempt {i+1} failed: {e}")
        if i < max_retries - 1:
            print("Retrying...")
        else:
            print("Failed to download NLTK data")
