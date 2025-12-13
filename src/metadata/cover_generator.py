"""
Dynamic SVG Book Cover Generator
Creates stylized text-based book covers with genre-specific colors.
Fast, reliable, no API calls needed.
"""

import hashlib
from typing import Optional
import html


# Genre-based color schemes (gradient start, gradient end, text color)
GENRE_COLORS = {
    'fiction': ('#3B82F6', '#1D4ED8', '#FFFFFF'),
    'non-fiction': ('#10B981', '#059669', '#FFFFFF'),
    'mystery': ('#6366F1', '#4338CA', '#FFFFFF'),
    'thriller': ('#EF4444', '#B91C1C', '#FFFFFF'),
    'romance': ('#EC4899', '#BE185D', '#FFFFFF'),
    'fantasy': ('#8B5CF6', '#6D28D9', '#FFFFFF'),
    'science fiction': ('#06B6D4', '#0284C7', '#FFFFFF'),
    'horror': ('#1F2937', '#111827', '#F9FAFB'),
    'adventure': ('#F59E0B', '#D97706', '#1F2937'),
    'biography': ('#6B7280', '#4B5563', '#FFFFFF'),
    'history': ('#92400E', '#78350F', '#FEF3C7'),
    'philosophy': ('#7C3AED', '#5B21B6', '#FFFFFF'),
    'psychology': ('#14B8A6', '#0D9488', '#FFFFFF'),
    'self-help': ('#F97316', '#EA580C', '#FFFFFF'),
    'poetry': ('#A855F7', '#7C3AED', '#FFFFFF'),
    'classic literature': ('#78716C', '#57534E', '#FAFAF9'),
    'young adult': ('#FB7185', '#E11D48', '#FFFFFF'),
    'general': ('#64748B', '#475569', '#FFFFFF'),
}


def _get_genre_colors(genre: str) -> tuple:
    """Get colors for a genre."""
    genre_lower = genre.lower().strip()
    
    # Try exact match
    if genre_lower in GENRE_COLORS:
        return GENRE_COLORS[genre_lower]
    
    # Try partial match
    for key in GENRE_COLORS:
        if key in genre_lower or genre_lower in key:
            return GENRE_COLORS[key]
    
    return GENRE_COLORS['general']


def _truncate_text(text: str, max_chars: int) -> str:
    """Truncate text to fit in cover."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars-1] + "…"


def _wrap_text(text: str, max_chars_per_line: int = 12) -> list:
    """Wrap text into multiple lines."""
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        if len(current_line + " " + word) <= max_chars_per_line:
            current_line = (current_line + " " + word).strip()
        else:
            if current_line:
                lines.append(current_line)
            current_line = word[:max_chars_per_line]  # Truncate long words
    
    if current_line:
        lines.append(current_line)
    
    return lines[:3]  # Max 3 lines


def generate_cover_svg(title: str, author: str = "Unknown", genre: str = "Fiction", 
                       width: int = 100, height: int = 145) -> str:
    """
    Generate a dynamic SVG book cover.
    
    Args:
        title: Book title
        author: Author name
        genre: Book genre for color scheme
        width: SVG width
        height: SVG height
        
    Returns:
        SVG string
    """
    color1, color2, text_color = _get_genre_colors(genre)
    
    # Escape HTML entities
    title_escaped = html.escape(title)
    author_escaped = html.escape(author)
    
    # Wrap title for display
    title_lines = _wrap_text(title, max_chars_per_line=10)
    
    # Calculate positions
    title_y_start = 35
    line_height = 14
    
    # Build title text elements
    title_elements = ""
    for i, line in enumerate(title_lines):
        y = title_y_start + (i * line_height)
        title_elements += f'<text x="{width//2}" y="{y}" text-anchor="middle" font-size="11" font-weight="600" fill="{text_color}" font-family="Georgia, serif">{html.escape(line)}</text>\n'
    
    # Author (truncated)
    author_display = _truncate_text(author, 14)
    author_y = height - 25
    
    # Genre badge
    genre_display = _truncate_text(genre, 12)
    
    svg = f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <linearGradient id="grad_{hash(title)}" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:{color1};stop-opacity:1" />
            <stop offset="100%" style="stop-color:{color2};stop-opacity:1" />
        </linearGradient>
        <filter id="shadow_{hash(title)}" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="2" stdDeviation="2" flood-opacity="0.3"/>
        </filter>
    </defs>
    
    <!-- Background -->
    <rect x="0" y="0" width="{width}" height="{height}" rx="4" fill="url(#grad_{hash(title)})"/>
    
    <!-- Decorative spine -->
    <rect x="0" y="0" width="6" height="{height}" fill="rgba(0,0,0,0.2)" rx="4 0 0 4"/>
    
    <!-- Top decorative line -->
    <rect x="15" y="15" width="{width-30}" height="2" fill="rgba(255,255,255,0.3)" rx="1"/>
    
    <!-- Title -->
    {title_elements}
    
    <!-- Divider -->
    <rect x="20" y="{author_y - 15}" width="{width-40}" height="1" fill="rgba(255,255,255,0.2)"/>
    
    <!-- Author -->
    <text x="{width//2}" y="{author_y}" text-anchor="middle" font-size="8" fill="{text_color}" font-family="Arial, sans-serif" opacity="0.9">{html.escape(author_display)}</text>
    
    <!-- Genre badge -->
    <rect x="10" y="{height-18}" width="{min(len(genre_display)*5 + 10, width-20)}" height="12" rx="2" fill="rgba(255,255,255,0.15)"/>
    <text x="15" y="{height-9}" font-size="6" fill="{text_color}" font-family="Arial, sans-serif" opacity="0.8">{html.escape(genre_display)}</text>
    
    <!-- Bottom decorative line -->
    <rect x="15" y="{height-5}" width="{width-30}" height="2" fill="rgba(255,255,255,0.3)" rx="1"/>
</svg>'''
    
    return svg


def generate_cover_data_url(title: str, author: str = "Unknown", genre: str = "Fiction",
                            width: int = 100, height: int = 145) -> str:
    """
    Generate a data URL for embedding in HTML.
    
    Returns:
        Data URL string
    """
    import base64
    svg = generate_cover_svg(title, author, genre, width, height)
    encoded = base64.b64encode(svg.encode()).decode()
    return f"data:image/svg+xml;base64,{encoded}"


class CoverGenerator:
    """Generates dynamic SVG book covers."""
    
    def __init__(self):
        """Initialize the cover generator."""
        self._cache = {}
    
    def get_cover(self, title: str, author: str = "Unknown", genre: str = "Fiction") -> str:
        """
        Get a cover SVG for a book.
        
        Args:
            title: Book title
            author: Author name
            genre: Book genre for styling
            
        Returns:
            SVG string
        """
        cache_key = f"{title}|{author}|{genre}"
        if cache_key not in self._cache:
            self._cache[cache_key] = generate_cover_svg(title, author, genre)
        return self._cache[cache_key]
    
    def get_cover_url(self, title: str, author: str = "Unknown", genre: str = "Fiction",
                      width: int = 100, height: int = 145) -> str:
        """
        Get a data URL for a book cover.
        
        Returns:
            Data URL string
        """
        return generate_cover_data_url(title, author, genre, width, height)
    
    def is_available(self) -> bool:
        """Always available - no external dependencies."""
        return True


# Singleton instance
_generator: Optional[CoverGenerator] = None

def get_cover_generator() -> CoverGenerator:
    """Get or create the cover generator singleton."""
    global _generator
    if _generator is None:
        _generator = CoverGenerator()
    return _generator
