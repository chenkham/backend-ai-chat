"""
Quick test script to verify Cohere API connection
"""
import os
from dotenv import load_dotenv
import cohere

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv("COHERE_API_KEY")

if not api_key:
    print("❌ COHERE_API_KEY not found in .env file")
    exit(1)

print("✅ COHERE_API_KEY found in .env")

# Test connection
try:
    client = cohere.Client(api_key)
    print("✅ Cohere client initialized")
    
    # Test embedding generation
    response = client.embed(
        texts=["Hello, this is a test"],
        model="embed-english-light-v3.0",
        input_type="search_document"
    )
    
    embedding = response.embeddings[0]
    print(f"✅ Embedding generated successfully!")
    print(f"   Dimension: {len(embedding)}")
    print(f"   First 5 values: {embedding[:5]}")
    print("\n🎉 Cohere API is working perfectly!")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    exit(1)
