"""
Open Library API Client
Free fallback API for book metadata (no API key required).
"""

import requests
import time
from typing import Optional, Dict, List, Any
from fuzzywuzzy import fuzz


class OpenLibraryClient:
    """
    Client for Open Library API.
    Free API with no key requirement - used as primary/fallback.
    """
    
    SEARCH_URL = "https://openlibrary.org/search.json"
    WORKS_URL = "https://openlibrary.org/works"
    COVERS_URL = "https://covers.openlibrary.org/b"
    
    def __init__(self):
        """Initialize Open Library client."""
        self._cache: Dict[str, dict] = {}
        self._last_request_time = 0
        self._min_request_interval = 0.3  # 300ms between requests
    
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
        # Check cache
        cache_key = f"{title}|{author or ''}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        self._wait_for_rate_limit()
        
        try:
            # Build query
            params = {
                'title': title,
                'limit': 5,
                'fields': 'key,title,author_name,first_publish_year,number_of_pages_median,subject,cover_i,isbn,rating_average,ratings_count'
            }
            
            if author:
                params['author'] = author
            
            response = requests.get(self.SEARCH_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get('docs'):
                return None
            
            # Find best matching result
            best_match = self._find_best_match(title, author, data['docs'])
            
            if best_match:
                metadata = self._parse_doc(best_match)
                # Fetch additional details if available
                metadata = self._enrich_metadata(metadata, best_match)
                self._cache[cache_key] = metadata
                return metadata
            
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"Open Library API error: {e}")
            return None
    
    def _find_best_match(self, title: str, author: Optional[str], docs: List[dict]) -> Optional[dict]:
        """
        Find the best matching book from search results.
        
        Args:
            title: Original search title
            author: Original search author
            docs: List of API result documents
            
        Returns:
            Best matching document or None
        """
        best_score = 0
        best_doc = None
        
        for doc in docs:
            result_title = doc.get('title', '')
            result_authors = doc.get('author_name', [])
            
            # Calculate title similarity
            title_score = fuzz.ratio(title.lower(), result_title.lower())
            
            # Bonus for author match
            author_score = 0
            if author and result_authors:
                for result_author in result_authors:
                    author_score = max(author_score, fuzz.ratio(author.lower(), result_author.lower()))
            
            # Combined score
            total_score = (title_score * 0.7) + (author_score * 0.3) if author else title_score
            
            if total_score > best_score and title_score >= 50:
                best_score = total_score
                best_doc = doc
        
        return best_doc
    
    def _parse_doc(self, doc: dict) -> Dict[str, Any]:
        """
        Parse document data into clean metadata format.
        
        Args:
            doc: Raw API response document
            
        Returns:
            Cleaned metadata dictionary
        """
        authors = doc.get('author_name', ['Unknown Author'])
        subjects = doc.get('subject', [])
        
        # Get cover image URL
        cover_id = doc.get('cover_i')
        cover_image = None
        if cover_id:
            cover_image = f"{self.COVERS_URL}/id/{cover_id}-L.jpg"
        
        # Extract main genres from subjects (first few meaningful ones)
        genres = self._extract_genres(subjects)
        
        # Get ISBN
        isbns = doc.get('isbn', [])
        isbn = isbns[0] if isbns else None
        
        return {
            'title': doc.get('title', 'Unknown Title'),
            'authors': authors,
            'author': ', '.join(authors),
            'description': '',  # Will be enriched later
            'genres': genres,
            'genre': genres[0] if genres else 'Unknown',
            'page_count': doc.get('number_of_pages_median', 0),
            'rating': doc.get('rating_average', 0),
            'ratings_count': doc.get('ratings_count', 0),
            'cover_image': cover_image,
            'published_date': str(doc.get('first_publish_year', '')),
            'publisher': '',
            'isbn': isbn,
            'language': 'en',
            'preview_link': f"https://openlibrary.org{doc.get('key', '')}",
            'source': 'open_library',
            '_work_key': doc.get('key')
        }
    
    def _extract_genres(self, subjects: List[str], max_genres: int = 5) -> List[str]:
        """
        Extract meaningful genres from subjects list.
        
        Args:
            subjects: Raw subjects from API
            max_genres: Maximum number of genres to return
            
        Returns:
            List of genre strings
        """
        if not subjects:
            return ['Unknown']
        
        # Common meaningful genre keywords
        genre_keywords = {
            'fiction', 'non-fiction', 'mystery', 'thriller', 'romance',
            'fantasy', 'science fiction', 'horror', 'adventure', 'drama',
            'biography', 'history', 'philosophy', 'psychology', 'self-help',
            'poetry', 'humor', 'suspense', 'literary', 'classic'
        }
        
        genres = []
        for subject in subjects[:20]:  # Check first 20 subjects
            subject_lower = subject.lower()
            # Check if subject contains a genre keyword
            for keyword in genre_keywords:
                if keyword in subject_lower and subject not in genres:
                    genres.append(subject)
                    break
            if len(genres) >= max_genres:
                break
        
        # If no genres found, use first few subjects
        if not genres:
            genres = subjects[:max_genres]
        
        return genres if genres else ['Unknown']
    
    def _enrich_metadata(self, metadata: dict, doc: dict) -> dict:
        """
        Fetch additional details for a book (description, etc).
        
        Args:
            metadata: Base metadata dictionary
            doc: Original document
            
        Returns:
            Enriched metadata dictionary
        """
        work_key = doc.get('key')
        if not work_key:
            return metadata
        
        self._wait_for_rate_limit()
        
        try:
            # Fetch work details for description
            work_url = f"https://openlibrary.org{work_key}.json"
            response = requests.get(work_url, timeout=10)
            
            if response.status_code == 200:
                work_data = response.json()
                
                # Get description
                description = work_data.get('description', '')
                if isinstance(description, dict):
                    description = description.get('value', '')
                metadata['description'] = description
                
        except requests.exceptions.RequestException:
            pass  # Fail silently for enrichment
        
        return metadata


# Singleton instance
_client: Optional[OpenLibraryClient] = None

def get_open_library_client() -> OpenLibraryClient:
    """Get or create the Open Library client singleton."""
    global _client
    if _client is None:
        _client = OpenLibraryClient()
    return _client
