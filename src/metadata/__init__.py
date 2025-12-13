"""
Metadata module initialization.
"""
from .google_books import GoogleBooksClient, get_google_books_client
from .open_library import OpenLibraryClient, get_open_library_client
from .gemini_metadata import GeminiMetadata, get_gemini_metadata
from .cover_generator import CoverGenerator, get_cover_generator
from .metadata_service import MetadataService, get_metadata_service

__all__ = [
    'GoogleBooksClient',
    'get_google_books_client',
    'OpenLibraryClient',
    'get_open_library_client',
    'GeminiMetadata',
    'get_gemini_metadata',
    'CoverGenerator',
    'get_cover_generator',
    'MetadataService',
    'get_metadata_service'
]


