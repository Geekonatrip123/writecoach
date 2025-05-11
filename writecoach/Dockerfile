FROM python:3.11-slim

WORKDIR /app

# Copy requirements first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create NLTK data directory and download required data
RUN mkdir -p /root/nltk_data && \
    python -c "import nltk; \
    nltk.download('punkt', download_dir='/root/nltk_data'); \
    nltk.download('averaged_perceptron_tagger', download_dir='/root/nltk_data'); \
    nltk.download('punkt_tab', download_dir='/root/nltk_data')"

# Set NLTK data path
ENV NLTK_DATA=/root/nltk_data

# Copy application files
COPY . .

EXPOSE 8000 8501

CMD ["python", "api.py"]