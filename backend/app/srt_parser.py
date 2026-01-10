import pysrt
from typing import Optional, Dict, Any

class SRTManager:
    def __init__(self):
        self.subs = None
        self.filename = None

    def load_file(self, content_str: str):
        """
        Parses SRT content string.
        """
        try:
            self.subs = pysrt.from_string(content_str)
            print(f"Loaded {len(self.subs)} subtitles.")
        except Exception as e:
            print(f"Error parsing SRT: {e}")
            self.subs = []

    def load_from_path(self, path: str):
        try:
            self.subs = pysrt.open(path)
            self.filename = path
            print(f"Loaded {len(self.subs)} subtitles from {path}.")
        except Exception as e:
            print(f"Error loading SRT file: {e}")
            self.subs = []

    def get_subtitle_at_time(self, seconds: float) -> Optional[Dict[str, Any]]:
        """
        Returns the subtitle active at the given timestamp (in seconds).
        Returns None if no subtitle is active.
        """
        if not self.subs:
            return None

        # Convert seconds to pysrt SubRipTime-like comparison
        # pysrt uses hours, minutes, seconds, milliseconds
        # Simplest way is 
        
        # Linear search for now (optimization: binary search or index)
        # Standard SRT files are ordered.
        
        target_index = None
        
        # Optimization: Start from last known index if we were tracking state, 
        # but for stateless API we search.
        # pysrt objects behave like list.
        
        # We need to construct a time object to compare, or just check standard seconds
        # pysrt.SubRipTime(0, 0, 10, 500)
        
        for sub in self.subs:
            start_seconds = sub.start.ordinal / 1000.0
            end_seconds = sub.end.ordinal / 1000.0
            
            if start_seconds <= seconds <= end_seconds:
                return {
                    "text": sub.text,
                    "start": start_seconds,
                    "end": end_seconds,
                    "index": sub.index
                }
                
        return None
