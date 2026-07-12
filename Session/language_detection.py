import pycld2 as cld2

class LanguageDetector:
    def __init__(self):
        self.blob = ""
        self.detected_lang = None
        self.is_reliable = False
        self.confidence = 0
    
    def add_text(self, text):
        if not text or not text.strip():
            return False
            
        self.blob += " " + text
        self.blob = self.blob.strip()
        
        is_reliable, _, details = cld2.detect(self.blob)
        
        if details and details[0][1] != 'un' and is_reliable:
            self.detected_lang = details[0][1]
            self.is_reliable = True
            self.confidence = details[0][2]
            return True
        
        return False
    
    def get_language(self):
        return self.detected_lang
