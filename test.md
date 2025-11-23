"""
Quick test script to verify backend components.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required imports work."""
    print("Testing imports...")
    
    try:
        import fastapi
        print("✓ FastAPI imported")
        
        import uvicorn
        print("✓ Uvicorn imported")
        
        from sentence_transformers import SentenceTransformer
        print("✓ Sentence-Transformers imported")
        
        from pinecone import Pinecone
        print("✓ Pinecone imported")
        
        from PyPDF2 import PdfReader
        print("✓ PyPDF2 imported")
        
        print("\n✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Import failed: {str(e)}")
        return False


def test_config():
    """Test configuration loading."""
    print("\nTesting configuration...")
    
    try:
        import config
        print(f"✓ Pinecone Index: {config.PINECONE_INDEX_NAME}")
        print(f"✓ Embedding Model: {config.EMBEDDING_MODEL_NAME}")
        print(f"✓ Chunk Size: {config.CHUNK_SIZE}")
        print(f"✓ Upload Dir: {config.UPLOAD_DIR}")
        
        print("\n✅ Configuration loaded successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Configuration failed: {str(e)}")
        return False


def test_database():
    """Test database initialization."""
    print("\nTesting database...")
    
    try:
        from database.db import get_database
        db = get_database()
        print("✓ Database initialized")
        
        print("\n✅ Database test successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Database test failed: {str(e)}")
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("🧪 Backend Component Testing")
    print("=" * 50)
    
    all_passed = True
    
    all_passed &= test_imports()
    all_passed &= test_config()
    all_passed &= test_database()
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    print("=" * 50)
