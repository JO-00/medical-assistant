import ollama

client = ollama.Client(host="http://localhost:11434")

def call_ollama(user_message: str, system_prompt: str = None, model: str = "qwen2.5:3b") -> str:
    messages = []
    
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    
    messages.append({"role": "user", "content": user_message})
    
    response = client.chat(
        model=model,
        messages=messages
    )
    return response["message"]["content"]