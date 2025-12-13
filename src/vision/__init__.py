"""
Vision module initialization.
"""
from .gemini_detector import GeminiBookDetector, detect_books_from_image

__all__ = ['GeminiBookDetector', 'detect_books_from_image']
