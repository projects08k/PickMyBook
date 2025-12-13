"""
Unified Metadata Service
Combines Google Books, Open Library, and Gemini AI with automatic fallback.
"""

from typing import Optional, Dict, List, Any
from .google_books import GoogleBooksClient, get_google_books_client
from .open_library import OpenLibraryClient, get_open_library_client
from .gemini_metadata import get_gemini_metadata


class MetadataService:
    """
    Unified service for fetching book metadata.
    Uses multiple sources with fallback:
    1. Google Books (if API key available)
    2. Open Library (free, no key needed)
    3. Gemini AI (generates metadata when others fail)
    """
    
    def __init__(self):
        """Initialize metadata service with all clients."""
        self.open_library = get_open_library_client()
        self.google_books = get_google_books_client()
        self.gemini = get_gemini_metadata()
        self._cache: Dict[str, dict] = {}
    
    def get_book_metadata(self, title: str, author: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a book, trying multiple sources.
        
        Strategy:
        1. Try Google Books if API key available (richer data)
        2. Fall back to Open Library (always available)
        3. Fall back to Gemini AI (generates metadata)
        
        Args:
            title: Book title
            author: Optional author name
            
        Returns:
            Book metadata dictionary or None if not found
        """
        cache_key = f"{title}|{author or ''}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        metadata = None
        
        # Try Google Books first if available
        if self.google_books.is_available:
            metadata = self.google_books.search_book(title, author)
        
        # Try Open Library (primary free source)
        open_library_data = self.open_library.search_book(title, author)
        
        if metadata and open_library_data:
            # Merge data - prefer Google for most fields, but use Open Library for missing data
            metadata = self._merge_metadata(metadata, open_library_data)
        elif open_library_data:
            metadata = open_library_data
        
        # If still no metadata, try Gemini AI as fallback
        if not metadata and self.gemini.is_available():
            metadata = self.gemini.get_book_metadata(title, author)
            if metadata:
                metadata['source'] = 'gemini_ai'
        
        if metadata:
            self._cache[cache_key] = metadata
        
        return metadata
    
    def _merge_metadata(self, primary: dict, secondary: dict) -> dict:
        """
        Merge metadata from two sources.
        
        Args:
            primary: Primary metadata (Google Books)
            secondary: Secondary metadata (Open Library)
            
        Returns:
            Merged metadata dictionary
        """
        merged = primary.copy()
        
        # Fill in missing fields from secondary
        if not merged.get('description') and secondary.get('description'):
            merged['description'] = secondary['description']
        
        if not merged.get('cover_image') and secondary.get('cover_image'):
            merged['cover_image'] = secondary['cover_image']
        
        if not merged.get('page_count') and secondary.get('page_count'):
            merged['page_count'] = secondary['page_count']
        
        if not merged.get('rating') and secondary.get('rating'):
            merged['rating'] = secondary['rating']
        
        # Merge genres
        primary_genres = set(merged.get('genres', []))
        secondary_genres = set(secondary.get('genres', []))
        merged['genres'] = list(primary_genres | secondary_genres)
        
        merged['sources'] = ['google_books', 'open_library']
        
        return merged
    
    def get_multiple_books(self, titles: List[Dict[str, Optional[str]]]) -> List[Dict[str, Any]]:
        """
        Get metadata for multiple books.
        
        Args:
            titles: List of dicts with 'title' and optional 'author' keys
            
        Returns:
            List of metadata dictionaries
        """
        results = []
        
        for book in titles:
            title = book.get('title', '')
            author = book.get('author')
            
            if title:
                metadata = self.get_book_metadata(title, author)
                if metadata:
                    results.append(metadata)
                else:
                    # Add placeholder with original detected info (shouldn't happen with Gemini fallback)
                    results.append({
                        'title': title,
                        'author': author or 'Unknown Author',
                        'authors': [author] if author else ['Unknown Author'],
                        'description': 'A book waiting to be discovered.',
                        'genres': ['Fiction'],
                        'genre': 'Fiction',
                        'page_count': 0,
                        'rating': 0,
                        'cover_image': None,
                        'source': 'detected'
                    })
        
        return results
    
    def clear_cache(self):
        """Clear the metadata cache."""
        self._cache.clear()
        self.open_library._cache.clear()
        self.google_books._cache.clear()


# Singleton instance
_service: Optional[MetadataService] = None

def get_metadata_service() -> MetadataService:
    """Get or create the metadata service singleton."""
    global _service
    if _service is None:
        _service = MetadataService()
    return _service

