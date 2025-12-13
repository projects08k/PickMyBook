"""
Styles module
"""
from .theme import (
    get_theme_css,
    apply_theme,
    render_score_ring,
    render_progress_bar,
    render_tags,
    normalize_author,
    normalize_genre,
    BOOK_PLACEHOLDER_SVG,
    BOOK_PLACEHOLDER_SMALL,
    BOOK_PLACEHOLDER_LARGE
)

__all__ = [
    'get_theme_css',
    'apply_theme',
    'render_score_ring',
    'render_progress_bar',
    'render_tags',
    'normalize_author',
    'normalize_genre',
    'BOOK_PLACEHOLDER_SVG',
    'BOOK_PLACEHOLDER_SMALL',
    'BOOK_PLACEHOLDER_LARGE'
]
