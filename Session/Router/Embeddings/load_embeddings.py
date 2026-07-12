import json
import pickle,torch
from pathlib import Path
from sentence_transformers import SentenceTransformer

CACHE_DIR = Path("Router/Embeddings")
CACHE_DIR.mkdir(exist_ok=True)

CONVERSATIONAL_CACHE = CACHE_DIR / "conversational_embeddings.pkl"
DATABASE_CACHE = CACHE_DIR / "database_embeddings.pkl"

device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = SentenceTransformer('all-MiniLM-L6-v2', device=device)

def load(samples_path: str = "Router/Embeddings/samples.json"):
    """Load embeddings from cache if exists, otherwise compute and save"""
    
    if CONVERSATIONAL_CACHE.exists() and DATABASE_CACHE.exists():
        print("Loading embeddings from cache...")
        with open(CONVERSATIONAL_CACHE, 'rb') as f:
            conversational_embeddings = pickle.load(f)
        with open(DATABASE_CACHE, 'rb') as f:
            database_embeddings = pickle.load(f)
        return conversational_embeddings, database_embeddings
    
    print("Computing embeddings from samples...")
    
    with open(samples_path, 'r', encoding='utf-8') as f:
        samples = json.load(f)
    
    # Get all sample texts from conversational -> en and fr
    conversational_samples = []
    for lang, texts in samples.get("conversational", {}).items():
        conversational_samples.extend(texts)  # texts is the list for en or fr
    
    # Get all sample texts from database -> en and fr
    database_samples = []
    for lang, texts in samples.get("database", {}).items():
        database_samples.extend(texts)  # texts is the list for en or fr
    
    # Compute embeddings
    conversational_embeddings = model.encode(conversational_samples)
    database_embeddings = model.encode(database_samples)
    
    # Save to cache
    with open(CONVERSATIONAL_CACHE, 'wb') as f:
        pickle.dump(conversational_embeddings, f)
    with open(DATABASE_CACHE, 'wb') as f:
        pickle.dump(database_embeddings, f)
    
    print(f"Saved embeddings: conversational={len(conversational_embeddings)}, database={len(database_embeddings)}")
    
    return conversational_embeddings, database_embeddings

























