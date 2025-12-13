"""
Gemini AI Metadata Fallback
Uses Gemini to generate book metadata when other sources fail.
"""

import os
import json
import re
from typing import Dict, Any, Optional

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class GeminiMetadata:
    """Fallback metadata source using Gemini AI."""
    
    def __init__(self):
        self.model = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Gemini client."""
        if not GEMINI_AVAILABLE:
            return
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            return
        
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        except Exception as e:
            print(f"Gemini metadata init error: {e}")
    
    def get_book_metadata(self, title: str, author: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get book metadata from Gemini AI.
        
        Args:
            title: Book title
            author: Optional author name
            
        Returns:
            Book metadata dict or None
        """
        if not self.model:
            return None
        
        try:
            # Build the prompt
            query = f'"{title}"'
            if author and author.lower() != 'unknown':
                query += f' by {author}'
            
            prompt = f"""You are a book metadata expert. Provide information about this book: {query}

Return ONLY a valid JSON object with these fields (no markdown, no explanation):
{{
    "title": "exact book title",
    "author": "author name",
    "genre": "primary genre (e.g., Fiction, Non-Fiction, Mystery, Romance, etc.)",
    "description": "brief 1-2 sentence description",
    "page_count": estimated page count as integer,
    "published_year": publication year as integer,
    "rating": average rating 1-5 as float
}}

If you don't know specific details, provide reasonable estimates. Always return valid JSON."""

            response = self.model.generate_content(prompt)
            
            if not response.text:
                return None
            
            # Parse JSON from response
            text = response.text.strip()
            
            # Remove markdown code blocks if present
            if text.startswith('```'):
                text = re.sub(r'^```json?\s*', '', text)
                text = re.sub(r'\s*```$', '', text)
            
            data = json.loads(text)
            
            # Format to match our expected structure
            return {
                'title': data.get('title', title),
                'author': data.get('author', 'Unknown'),
                'genre': data.get('genre', 'Fiction'),
                'description': data.get('description', ''),
                'page_count': data.get('page_count', 0),
                'published_year': data.get('published_year'),
                'average_rating': data.get('rating', 0),
                'cover_image': None,  # Gemini can't provide images
                'source': 'gemini_ai'
            }
            
        except json.JSONDecodeError as e:
            print(f"Gemini JSON parse error: {e}")
            return None
        except Exception as e:
            print(f"Gemini metadata error: {e}")
            return None
    
    def is_available(self) -> bool:
        """Check if Gemini is available."""
        return self.model is not None


# Singleton instance
_gemini_metadata: Optional[GeminiMetadata] = None

def get_gemini_metadata() -> GeminiMetadata:
    """Get or create the Gemini metadata singleton."""
    global _gemini_metadata
    if _gemini_metadata is None:
        _gemini_metadata = GeminiMetadata()
    return _gemini_metadata
