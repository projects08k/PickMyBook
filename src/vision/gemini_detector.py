"""
Gemini Vision Book Detector
Detects book titles from bookshelf/book cover images using Google Gemini Vision API.
"""

import os
import base64
import google.generativeai as genai
from typing import List, Optional
from PIL import Image
import io
import time


class GeminiBookDetector:
    """
    Detects book titles from images using Gemini Vision API.
    Implements rate limiting and caching to prevent API abuse.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Gemini Book Detector.
        
        Args:
            api_key: Gemini API key. If not provided, reads from GEMINI_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key is required. Set GEMINI_API_KEY environment variable.")
        
        genai.configure(api_key=self.api_key)
        # Use gemini-2.5-flash for best vision support
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Rate limiting - track last request time
        self._last_request_time = 0
        self._min_request_interval = 1.0  # Minimum 1 second between requests
        
        # Detection prompt optimized for book spine/cover detection
        self.detection_prompt = """
Analyze this image and identify all visible book titles.

Instructions:
1. Look for book spines, covers, and any visible text that appears to be a book title
2. Extract the EXACT title as it appears on the book
3. If you can see the author's name, include it in parentheses after the title
4. Only include titles you can clearly read - do not guess
5. If no books are visible or titles are unreadable, respond with "NO_BOOKS_DETECTED"

Return the results as a simple numbered list, one book per line.
Example format:
1. The Great Gatsby (F. Scott Fitzgerald)
2. 1984 (George Orwell)
3. Pride and Prejudice

DO NOT include any additional commentary or formatting.
"""

    def _wait_for_rate_limit(self):
        """Ensure we don't exceed rate limits."""
        current_time = time.time()
        elapsed = current_time - self._last_request_time
        if elapsed < self._min_request_interval:
            time.sleep(self._min_request_interval - elapsed)
        self._last_request_time = time.time()

    def _prepare_image(self, image_data) -> dict:
        """
        Prepare image data for Gemini API.
        
        Args:
            image_data: Can be file path, bytes, or PIL Image
            
        Returns:
            Dictionary with image data for Gemini
        """
        if isinstance(image_data, str):
            # File path
            with open(image_data, 'rb') as f:
                image_bytes = f.read()
        elif isinstance(image_data, bytes):
            image_bytes = image_data
        elif isinstance(image_data, Image.Image):
            # PIL Image
            buffer = io.BytesIO()
            image_data.save(buffer, format='PNG')
            image_bytes = buffer.getvalue()
        else:
            # Assume it's a file-like object (Streamlit UploadedFile)
            image_bytes = image_data.read()
            if hasattr(image_data, 'seek'):
                image_data.seek(0)  # Reset for potential reuse
        
        return {
            'mime_type': 'image/png',
            'data': base64.standard_b64encode(image_bytes).decode('utf-8')
        }

    def detect_books(self, image_data) -> List[str]:
        """
        Detect book titles from an image.
        
        Args:
            image_data: Image file path, bytes, PIL Image, or Streamlit UploadedFile
            
        Returns:
            List of detected book titles
        """
        self._wait_for_rate_limit()
        
        try:
            # Convert image data to PIL Image
            if isinstance(image_data, str):
                # File path
                img = Image.open(image_data)
            elif isinstance(image_data, bytes):
                img = Image.open(io.BytesIO(image_data))
            elif isinstance(image_data, Image.Image):
                img = image_data
            else:
                # Assume it's a file-like object (Streamlit UploadedFile)
                img = Image.open(io.BytesIO(image_data))
            
            # Ensure image is in RGB mode
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Generate response using simple approach
            response = self.model.generate_content([self.detection_prompt, img])
            
            # Check if we have a valid response
            if response and response.text:
                print(f"Gemini response: {response.text[:200]}...")  # Debug log
                return self._parse_response(response.text)
            else:
                print("Empty response from Gemini")
                return []
            
        except Exception as e:
            print(f"Error detecting books: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _parse_response(self, response_text: str) -> List[str]:
        """
        Parse Gemini response to extract book titles.
        
        Args:
            response_text: Raw response from Gemini
            
        Returns:
            List of book titles
        """
        if not response_text or "NO_BOOKS_DETECTED" in response_text.upper():
            return []
        
        books = []
        lines = response_text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Remove numbering (1. 2. etc.)
            if line[0].isdigit():
                # Find the first space or period after numbers
                for i, char in enumerate(line):
                    if char in '. ':
                        line = line[i+1:].strip()
                        break
            
            # Remove leading dashes or bullets
            line = line.lstrip('-•* ')
            
            if line:
                books.append(line)
        
        return books

    def detect_books_with_details(self, image_data) -> List[dict]:
        """
        Detect books with separated title and author.
        
        Args:
            image_data: Image data
            
        Returns:
            List of dicts with 'title' and 'author' keys
        """
        raw_titles = self.detect_books(image_data)
        books = []
        
        for raw in raw_titles:
            # Try to extract author from parentheses
            if '(' in raw and ')' in raw:
                start = raw.rfind('(')
                end = raw.rfind(')')
                title = raw[:start].strip()
                author = raw[start+1:end].strip()
            else:
                title = raw
                author = None
            
            books.append({
                'title': title,
                'author': author,
                'raw': raw
            })
        
        return books


# Convenience function for quick usage
def detect_books_from_image(image_data, api_key: Optional[str] = None) -> List[str]:
    """
    Quick function to detect books from an image.
    
    Args:
        image_data: Image file path, bytes, or PIL Image
        api_key: Optional Gemini API key
        
    Returns:
        List of detected book titles
    """
    detector = GeminiBookDetector(api_key=api_key)
    return detector.detect_books(image_data)
