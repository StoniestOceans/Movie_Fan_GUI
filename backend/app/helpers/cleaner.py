import re

class DataCleanerAgent:
    """
    Helper agent to sanitize text data before vectorization to improve quality.
    """
    def __init__(self):
        # Regex for HTML tags like <i>, </b>
        self.html_cleaner = re.compile('<.*?>')
        # Regex for bracketed sound effects like [Explosion], (Music plays)
        self.bracket_cleaner = re.compile('\[.*?\]|\(.*?\)')

    def clean_text(self, text: str) -> str:
        if not text:
            return ""
            
        # 1. Remove HTML tags
        clean = re.sub(self.html_cleaner, '', text)
        
        # 2. Remove Sound Effects (optional, but good for pure dialogue search)
        clean = re.sub(self.bracket_cleaner, '', clean)
        
        # 3. Normalize whitespace
        clean = " ".join(clean.split())
        
        return clean
