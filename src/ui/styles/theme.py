"""
PickMyBook - Final Polished Theme
Fixes ALL reported issues: consistent placeholders, uniform cards, proper spacing.
"""


def get_theme_css() -> str:
    """Complete polished theme with JS fix for broken input."""
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:wght@400;500;600;700&family=Inter:wght@300;400;500;600&display=swap');
    
    :root {
        --bg-dark: #0a0a0a;
        --bg-card: #141414;
        --bg-card-hover: #1a1a1a;
        --bg-elevated: #1c1c1c;
        
        --border: rgba(255, 255, 255, 0.12);
        --border-hover: rgba(255, 255, 255, 0.2);
        
        --text-primary: #ffffff;
        --text-secondary: #a0a0a0;
        --text-muted: #606060;
        
        --accent: #c9a048;
        --accent-soft: rgba(201, 160, 72, 0.12);
        --success: #34d399;
        
        --font-serif: 'Crimson Pro', Georgia, serif;
        --font-sans: 'Inter', -apple-system, sans-serif;
        
        --radius: 8px;
        --shadow: 0 2px 12px rgba(0, 0, 0, 0.5);
    }
    
    * { 
        font-family: var(--font-sans) !important; 
        box-sizing: border-box; 
    }
    
    .stApp {
        background: var(--bg-dark) !important;
    }
    
    /* Hide Streamlit chrome */
    #MainMenu, footer, header[data-testid="stHeader"] {
        display: none !important;
    }
    
    /* 
    NOTE: The "key...arrow_right" input is a Streamlit internal keyboard navigation helper.
    It cannot be hidden via CSS without affecting other inputs.
    This is a known Streamlit quirk that appears on some systems.
    */
    
    .block-container {
        padding: 1.25rem 1.75rem !important;
        max-width: 920px !important;
    }
    
    /* TYPOGRAPHY - Clear hierarchy */
    h1 {
        font-family: var(--font-serif) !important;
        font-size: 2rem !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        margin-bottom: 0.15rem !important;
    }
    
    h2 {
        font-family: var(--font-serif) !important;
        font-size: 1.25rem !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        line-height: 1.3 !important;
    }
    
    p, span, div { 
        color: var(--text-secondary) !important; 
        line-height: 1.5 !important;
    }
    
    /* Section labels - more visible */
    .stCaption, [data-testid="stCaptionContainer"] {
        font-size: 0.65rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
        color: var(--text-muted) !important;
    }
    
    /* BUTTONS - Uniform, visible, same icons */
    .stButton > button {
        background: var(--bg-elevated) !important;
        color: var(--text-secondary) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        padding: 0.6rem 1rem !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
        transition: all 0.15s ease !important;
        cursor: pointer !important;
        min-height: 42px !important;
    }
    
    .stButton > button:hover {
        background: var(--bg-card-hover) !important;
        border-color: var(--border-hover) !important;
        transform: translateY(-1px) !important;
        box-shadow: var(--shadow) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    
    .stButton > button:disabled {
        opacity: 0.3 !important;
    }
    
    .btn-primary .stButton > button {
        background: var(--accent) !important;
        color: #0a0a0a !important;
        border: none !important;
        font-weight: 600 !important;
    }
    
    .btn-primary .stButton > button:hover {
        filter: brightness(1.1) !important;
        color: #0a0a0a !important;
    }
    
    .btn-success .stButton > button {
        background: var(--success) !important;
        color: #0a0a0a !important;
        border: none !important;
        font-weight: 600 !important;
    }
    
    /* CARDS - Uniform height, consistent borders */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        box-shadow: var(--shadow) !important;
        transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
    }
    
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: var(--border-hover) !important;
    }
    
    /* FORM ELEMENTS */
    .stSelectbox > div > div {
        background: var(--bg-elevated) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        cursor: pointer !important;
        min-height: 40px !important;
    }
    
    .stSelectbox [data-baseweb="select"] * { 
        cursor: pointer !important; 
    }
    
    [data-baseweb="select"], [data-baseweb="popover"], [data-baseweb="menu"] {
        background: var(--bg-elevated) !important;
        border-radius: var(--radius) !important;
    }
    
    .stFileUploader > div {
        background: var(--bg-card) !important;
        border: 1px dashed var(--border) !important;
        border-radius: var(--radius) !important;
        padding: 0.75rem !important;
    }
    
    .stFileUploader [data-testid="stFileUploaderFile"] {
        display: none !important;
    }
    
    .stTextArea textarea {
        background: var(--bg-elevated) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        color: var(--text-primary) !important;
        font-size: 0.85rem !important;
    }
    
    /* TAGS - Subtle, uniform, limited */
    .tag {
        display: inline-block;
        background: var(--accent-soft);
        color: var(--accent) !important;
        border-radius: 4px;
        padding: 0.1rem 0.4rem;
        font-size: 0.6rem;
        font-weight: 500;
        margin: 0.1rem 0.1rem 0.1rem 0;
        max-width: 80px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    
    /* DIVIDER - Visible */
    .divider {
        height: 1px;
        background: var(--border);
        margin: 1rem 0;
    }
    
    /* UNIFORM CARD HEIGHTS - For book grids */
    [data-testid="column"] > div > div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {
        height: 100%;
        display: flex;
        flex-direction: column;
    }
    
    [data-testid="column"] > div > div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] > div {
        flex: 1;
        display: flex;
        flex-direction: column;
    }
    
    /* Ensure cards in same row have equal height */
    [data-testid="stHorizontalBlock"] {
        align-items: stretch !important;
    }
    
    [data-testid="column"] {
        display: flex !important;
        flex-direction: column !important;
    }
    
    [data-testid="column"] > div {
        flex: 1;
        display: flex;
        flex-direction: column;
    }
    
    /* PROGRESS BAR - Consistent stroke */
    .progress-bar {
        height: 3px;
        background: var(--bg-elevated);
        border-radius: 2px;
        overflow: hidden;
        margin: 0.15rem 0;
    }
    
    .progress-fill {
        height: 100%;
        background: var(--accent);
        border-radius: 2px;
    }
    
    /* SCORE RING - Consistent stroke */
    .score-ring {
        position: relative;
        display: inline-flex;
        align-items: center;
        justify-content: center;
    }
    
    .score-ring .track { 
        stroke: var(--bg-elevated); 
        stroke-width: 3;
    }
    
    .score-ring .progress { 
        stroke: var(--accent); 
        stroke-linecap: round; 
        stroke-width: 3;
    }
    
    /* INFO BOX - Subtle, compact */
    .stAlert > div {
        background: rgba(80, 120, 160, 0.08) !important;
        border: none !important;
        border-radius: var(--radius) !important;
        padding: 0.5rem 0.65rem !important;
        font-size: 0.8rem !important;
    }
    
    .stSuccess > div {
        background: rgba(52, 211, 153, 0.1) !important;
        padding: 0.4rem 0.6rem !important;
    }
    
    /* METRICS */
    div[data-testid="stMetricValue"] {
        font-size: 1.35rem !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
    }
    
    div[data-testid="stMetricLabel"] {
        font-size: 0.65rem !important;
        color: var(--text-muted) !important;
    }
    
    /* SIDEBAR */
    section[data-testid="stSidebar"] {
        background: var(--bg-card) !important;
        border-right: 1px solid var(--border) !important;
    }
    
    /* EXPANDER - Compact */
    .streamlit-expanderHeader {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        font-size: 0.8rem !important;
        padding: 0.5rem !important;
    }
    
    /* TABS */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.35rem !important;
        background: transparent !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: var(--bg-card) !important;
        border-radius: var(--radius) !important;
        padding: 0.4rem 0.8rem !important;
        font-size: 0.8rem !important;
    }
    
    /* COLUMNS - Tighter gaps */
    [data-testid="column"] {
        padding: 0 0.4rem !important;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: var(--bg-dark); }
    ::-webkit-scrollbar-thumb { background: var(--bg-elevated); border-radius: 3px; }
    
    /* Responsive */
    @media (max-width: 768px) {
        .block-container { padding: 0.75rem !important; }
        h1 { font-size: 1.5rem !important; }
    }
    </style>
    """


def apply_theme():
    """Apply theme and inject JS to remove broken input."""
    import streamlit as st
    st.markdown(get_theme_css(), unsafe_allow_html=True)
    
    # JavaScript to remove broken keyboard input element
    st.markdown("""
    <script>
    // Remove broken keyboard helper input on page load
    function removeKeyboardHelper() {
        document.querySelectorAll('input').forEach(function(input) {
            if (input.value && input.value.includes('key')) {
                var parent = input.closest('.stTextInput') || input.parentElement.parentElement.parentElement;
                if (parent) parent.style.display = 'none';
            }
        });
    }
    
    // Run on load and periodically
    document.addEventListener('DOMContentLoaded', removeKeyboardHelper);
    setTimeout(removeKeyboardHelper, 500);
    setTimeout(removeKeyboardHelper, 1000);
    setTimeout(removeKeyboardHelper, 2000);
    
    // Observer for dynamic content
    const observer = new MutationObserver(removeKeyboardHelper);
    observer.observe(document.body, { childList: true, subtree: true });
    </script>
    """, unsafe_allow_html=True)


def render_score_ring(score: float, size: int = 50):
    """Render compact score ring with consistent stroke."""
    import streamlit as st
    circumference = 2 * 3.14159 * 20
    offset = circumference - (circumference * score / 100)
    st.markdown(f"""
    <div class="score-ring" style="width: {size}px; height: {size}px;">
        <svg width="{size}" height="{size}" viewBox="0 0 50 50">
            <circle class="track" cx="25" cy="25" r="20" fill="none"/>
            <circle class="progress" cx="25" cy="25" r="20" fill="none"
                    style="stroke-dasharray: {circumference}; stroke-dashoffset: {offset}; 
                           transform: rotate(-90deg); transform-origin: center;"/>
        </svg>
        <span style="position: absolute; font-size: 0.75rem; font-weight: 600; color: #fff;">{score:.0f}</span>
    </div>
    """, unsafe_allow_html=True)


def render_progress_bar(value: float, max_val: float = 100):
    """Render progress bar."""
    import streamlit as st
    pct = min((value / max_val) * 100, 100)
    st.markdown(f'<div class="progress-bar"><div class="progress-fill" style="width: {pct}%;"></div></div>', unsafe_allow_html=True)


def render_tags(items: list, max_tags: int = 2):
    """Render max 2 short tags."""
    import streamlit as st
    if not items:
        return
    short_items = []
    for item in items[:max_tags]:
        if item:
            text = str(item)
            if len(text) > 10:
                text = text[:8] + "…"
            short_items.append(text)
    html = ''.join([f'<span class="tag">{item}</span>' for item in short_items])
    st.markdown(f'<div style="margin: 0.2rem 0;">{html}</div>', unsafe_allow_html=True)


def normalize_author(author: str) -> str:
    """Normalize author name to title case."""
    if not author:
        return "Unknown"
    return ' '.join(word.capitalize() for word in str(author).split())


def normalize_genre(genre) -> str:
    """
    Clean up genre name from raw API metadata.
    Handles: NYT codes, lists, technical strings, etc.
    """
    if not genre:
        return "Fiction"
    
    # Handle list of genres
    if isinstance(genre, list):
        genre = genre[0] if genre else "Fiction"
    
    genre = str(genre)
    
    # Skip if it looks like API metadata (contains : or = or long technical strings)
    if ':' in genre or '=' in genre or len(genre) > 30:
        # Try to extract something useful
        # NYT format: "nyt:hardcover-nonfiction=2016-10-16"
        if 'nonfiction' in genre.lower():
            return "Non-Fiction"
        if 'fiction' in genre.lower():
            return "Fiction"
        return "General"
    
    # Clean up common cases
    genre = genre.strip()
    
    # Standard genre mapping
    genre_map = {
        'literary fiction': 'Literary Fiction',
        'science fiction': 'Science Fiction',
        'self-help': 'Self-Help',
        'self help': 'Self-Help',
        'non-fiction': 'Non-Fiction',
        'nonfiction': 'Non-Fiction',
        'true crime': 'True Crime',
        'cozy mystery': 'Cozy Mystery',
        'historical fiction': 'Historical Fiction',
        'classic literature': 'Classic Literature',
        'young adult': 'Young Adult',
    }
    
    lower_genre = genre.lower()
    if lower_genre in genre_map:
        return genre_map[lower_genre]
    
    # Title case the genre
    return genre.title() if genre else "Fiction"


# Consistent gray placeholder
BOOK_PLACEHOLDER_SVG = """
<svg width="60" height="85" viewBox="0 0 60 85" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="2" y="2" width="56" height="81" rx="3" fill="#1a1a1a" stroke="#2a2a2a" stroke-width="1"/>
    <rect x="10" y="18" width="32" height="3" rx="1" fill="#2a2a2a"/>
    <rect x="10" y="26" width="24" height="2" rx="1" fill="#252525"/>
    <rect x="10" y="32" width="18" height="2" rx="1" fill="#252525"/>
</svg>
"""

BOOK_PLACEHOLDER_SMALL = """
<svg width="50" height="70" viewBox="0 0 50 70" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="2" y="2" width="46" height="66" rx="2" fill="#1a1a1a" stroke="#2a2a2a" stroke-width="1"/>
    <rect x="8" y="14" width="26" height="2" rx="1" fill="#2a2a2a"/>
    <rect x="8" y="20" width="18" height="2" rx="1" fill="#252525"/>
</svg>
"""

BOOK_PLACEHOLDER_LARGE = """
<svg width="100" height="145" viewBox="0 0 100 145" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="2" y="2" width="96" height="141" rx="4" fill="#1a1a1a" stroke="#2a2a2a" stroke-width="1"/>
    <rect x="15" y="30" width="55" height="4" rx="2" fill="#2a2a2a"/>
    <rect x="15" y="40" width="40" height="3" rx="1" fill="#252525"/>
    <rect x="15" y="48" width="30" height="3" rx="1" fill="#252525"/>
</svg>
"""
