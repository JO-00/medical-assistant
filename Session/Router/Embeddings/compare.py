from Router.Embeddings import load_embeddings
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from LLM_API import call_ollama
import logging
logger = logging.getLogger()

conversational_embeddings, database_embeddings = load_embeddings.load()

def compare(prompt: str) -> dict:
    """Return similarity scores for a prompt against conversational and database samples"""
    
    prompt_embedding = load_embeddings.model.encode([prompt])
    
    conv_similarities = cosine_similarity(prompt_embedding, conversational_embeddings)
    conv_score = np.max(conv_similarities)
    
    db_similarities = cosine_similarity(prompt_embedding, database_embeddings)
    db_score = np.max(db_similarities)
    
    return {
        "conversational": float(conv_score),
        "database": float(db_score)
    }




#EXTERNAL API IT CLASSIFIES FRENCH OR ENGLISH INPUT TO DATABASE QUERY PROMPT OR CONVERSATIONAL PROMPT
def infer(prompt : str) -> str:
    print('I WAS CALLED')
    # returns "conversational" or "database" either deterministically (fast) or if small margin call llm
    
    scores = compare(prompt)
    print(scores)
    margin = abs(scores["conversational"] - scores["database"])
    
    if margin >= 0.15:
        return "conversational" if scores["conversational"] > scores["database"] else "database"
    
    # Uncertain - call LLM
    system_prompt = """
        You are a classifier. Classify the user's message as either:
        - "conversational" - casual chat, greetings, thanks, small talk, general questions not about patient data
        - "database" - queries about patients, appointments, medical records, CRUD operations on patient data

        Respond with ONLY one word: conversational|database
    """
    response = call_ollama(user_message = prompt, system_prompt = system_prompt).strip().lower().replace('"','')
    logger.critical(response)
    assert response in ["conversational" , "database"]
    print(response)
    return response



if __name__ == "__main__":
    while True:
        result = infer(input("Enter = "))
        print(result) 



