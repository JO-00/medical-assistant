from Router.Embeddings.compare import infer







def get_contexts() -> dict:
    BASE_DIR = "Router/Contexts/"
    files = {
        "conversational": {
            "en": f"{BASE_DIR}conversational/en.txt",
            "fr": f"{BASE_DIR}conversational/fr.txt"
        },
        "database": f"{BASE_DIR}database.txt",
        "time_detection": {
            "en": f"{BASE_DIR}time_detection/en.txt",
            "fr": f"{BASE_DIR}time_detection/fr.txt"
        }
    }
    """
    returns exactly like the dict above
    exccept instead of filenames as values gives contexts
    """
    
    # Read all files and return their contents
    result = {}
    
    for key, value in files.items():
        if isinstance(value, dict):
            result[key] = {}
            for lang, path in value.items():
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        result[key][lang] = f.read()
                except FileNotFoundError:
                    result[key][lang] = ""
        else:
            try:
                with open(value, 'r', encoding='utf-8') as f:
                    result[key] = f.read()
            except FileNotFoundError:
                result[key] = ""
    
    return result



CONTEXTS = get_contexts()

def inject_dynamic_context(prompt: str, detected_language: str) -> str:
    print("inject_dynamic_content called")
    domain = infer(prompt)
    
    # If database, return the string directly
    if domain == "database":
        return CONTEXTS["database"] , "database"
    
    # For conversational and time_detection, use language
    if detected_language and detected_language != "en":
        if domain in CONTEXTS and detected_language in CONTEXTS[domain]:
            return CONTEXTS[domain][detected_language] , domain
    
    # Default to English
    return CONTEXTS[domain]["en"] , domain



