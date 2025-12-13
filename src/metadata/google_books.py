"""
Google Books API Client
Fetches book metadata from Google Books API with rate limiting and caching.
"""

import os
import requests
import time
from typing import Optional, Dict, List, Any
from fuzzywuzzy import fuzz


class GoogleBooksClient:
    """
    Client for Google Books API with rate limiting.
    Used when API key is available.
    """
    
    BASE_URL = "https://www.googleapis.com/books/v1/volumes"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Google Books client.
        
        Args:
            api_key: Google Books API key. Reads from env if not provided.
        """
        self.api_key = api_key or os.getenv("GOOGLE_BOOKS_API_KEY")
        self._cache: Dict[str, dict] = {}
        self._last_request_time = 0
        self._min_request_interval = 0.5  # 500ms between requests
    
    @property
    def is_available(self) -> bool:
        """Check if API key is configured."""
        return bool(self.api_key)
    
    def _wait_for_rate_limit(self):
        """Ensure we don't exceed rate limits."""
        current_time = time.time()
        elapsed = current_time - self._last_request_time
        if elapsed < self._min_request_interval:
            time.sleep(self._min_request_interval - elapsed)
        self._last_request_time = time.time()
    
    def search_book(self, title: str, author: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Search for a book by title and optionally author.
        
        Args:
            title: Book title to search
            author: Optional author name
            
        Returns:
            Book metadata dictionary or None if not found
        """
        if not self.is_available:
            return None
        
        # Check cache
        cache_key = f"{title}|{author or ''}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        self._wait_for_rate_limit()
        
        try:
            # Build query
            query = f'intitle:{title}'
            if author:
                query += f'+inauthor:{author}'
            
            params = {
                'q': query,
                'key': self.api_key,
                'maxResults': 5,  # Get a few results to find best match
                'printType': 'books'
            }
            
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'items' not in data or not data['items']:
                return None
            
            # Find best matching result using fuzzy matching
            best_match = self._find_best_match(title, author, data['items'])
            
            if best_match:
                metadata = self._parse_volume(best_match)
                self._cache[cache_key] = metadata
                return metadata
            
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"Google Books API error: {e}")
            return None
    
    def _find_best_match(self, title: str, author: Optional[str], items: List[dict]) -> Optional[dict]:
        """
        Find the best matching book from search results.
        
        Args:
            title: Original search title
            author: Original search author
            items: List of API result items
            
        Returns:
            Best matching item or None
        """
        best_score = 0
        best_item = None
        
        for item in items:
            volume_info = item.get('volumeInfo', {})
            result_title = volume_info.get('title', '')
            result_authors = volume_info.get('authors', [])
            
            # Calculate title similarity
            title_score = fuzz.ratio(title.lower(), result_title.lower())
            
            # Bonus for author match
            author_score = 0
            if author and result_authors:
                for result_author in result_authors:
                    author_score = max(author_score, fuzz.ratio(author.lower(), result_author.lower()))
            
            # Combined score (title weighted more heavily)
            total_score = (title_score * 0.7) + (author_score * 0.3) if author else title_score
            
            if total_score > best_score and title_score >= 50:  # Minimum 50% title match
                best_score = total_score
                best_item = item
        
        return best_item
    
    def _parse_volume(self, item: dict) -> Dict[str, Any]:
        """
        Parse volume data into clean metadata format.
        
        Args:
            item: Raw API response item
            
        Returns:
            Cleaned metadata dictionary
        """
        volume_info = item.get('volumeInfo', {})
        
        # Get cover image (prefer larger images)
        image_links = volume_info.get('imageLinks', {})
        cover_image = (
            image_links.get('large') or
            image_links.get('medium') or
            image_links.get('thumbnail') or
            image_links.get('smallThumbnail')
        )
        
        # Convert HTTP to HTTPS for cover images
        if cover_image and cover_image.startswith('http://'):
            cover_image = cover_image.replace('http://', 'https://')
        
        # Extract categories/genres
        categories = volume_info.get('categories', [])
        
        return {
            'title': volume_info.get('title', 'Unknown Title'),
            'authors': volume_info.get('authors', ['Unknown Author']),
            'author': ', '.join(volume_info.get('authors', ['Unknown Author'])),
            'description': volume_info.get('description', ''),
            'genres': categories,
            'genre': categories[0] if categories else 'Unknown',
            'page_count': volume_info.get('pageCount', 0),
            'rating': volume_info.get('averageRating', 0),
            'ratings_count': volume_info.get('ratingsCount', 0),
            'cover_image': cover_image,
            'published_date': volume_info.get('publishedDate', ''),
            'publisher': volume_info.get('publisher', ''),
            'isbn': self._extract_isbn(volume_info),
            'language': volume_info.get('language', 'en'),
            'preview_link': volume_info.get('previewLink', ''),
            'source': 'google_books'
        }
    
    def _extract_isbn(self, volume_info: dict) -> Optional[str]:
        """Extract ISBN from industry identifiers."""
        identifiers = volume_info.get('industryIdentifiers', [])
        for identifier in identifiers:
            if identifier.get('type') in ['ISBN_13', 'ISBN_10']:
                return identifier.get('identifier')
        return None


# Singleton instance
_client: Optional[GoogleBooksClient] = None

def get_google_books_client() -> GoogleBooksClient:
    """Get or create the Google Books client singleton."""
    global _client
    if _client is None:
        _client = GoogleBooksClient()
    return _client
