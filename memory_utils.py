import os
import numpy as np
from openai import OpenAI
from typing import List, Dict, Any
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def get_embedding(text: str, model="text-embedding-3-small") -> List[float]:
    text = text.replace("\n", " ")
    try:
        return client.embeddings.create(input=[text], model=model).data[0].embedding
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        return []

def cosine_similarity(a, b):
    if not a or not b:
        return 0.0
    
    a = np.array(a)
    b = np.array(b)
    
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0.0
        
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def search_memories(query: str, memories: List[Dict[str, Any]], top_k: int = 3) -> List[Dict[str, Any]]:
    query_embedding = get_embedding(query)
    if not query_embedding:
        return []

    scored_memories = []
    for mem in memories:
        if "embedding" not in mem or not mem["embedding"]:
            content_text = " ".join([str(v) for k, v in mem.items() if k not in ["embedding", "session_id"]])
            mem["embedding"] = get_embedding(content_text)
        
        score = cosine_similarity(query_embedding, mem["embedding"])
        scored_memories.append((score, mem))
    
    scored_memories.sort(key=lambda x: x[0], reverse=True)
    
    top_results = [m[1] for m in scored_memories[:top_k]]
    
    if top_results:
        summary = top_results[0].get('summary') or top_results[0].get('Current Issue') or top_results[0].get('現在の課題') or "Unknown"
        logger.info(f"RAG Search Hit: {summary} (Score: {scored_memories[0][0]:.4f})")
        
    return top_results