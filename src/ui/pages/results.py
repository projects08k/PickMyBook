"""
Results Page - Uniform Cards
Fixed: consistent placeholders, uniform card height, proper spacing, centered buttons.
"""

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.vision import GeminiBookDetector
from src.metadata import get_metadata_service
from src.sentiment import get_mood_classifier
from src.ui.styles import render_tags, normalize_author, BOOK_PLACEHOLDER_SVG


def render_results_page():
    """Render results with uniform book cards."""
    
    if st.session_state.get('analyzing', False):
        _render_analyzing()
        return
    
    books = st.session_state.get('detected_books', [])
    mood = st.session_state.get('mood_classification', {})
    
    if not books:
        st.markdown("## No Books Detected")
        st.caption("Upload a bookshelf photo to get started.")
        if st.button("← Home"):
            st.session_state['page'] = 'home'
            st.rerun()
        return
    
    # Header
    primary_mood = mood.get('primary_mood', 'curious').capitalize()
    st.markdown("# Your Books")
    st.caption(f"{len(books)} detected · {primary_mood} mood")
    
    # Book grid - uniform cards
    for i in range(0, len(books), 2):
        cols = st.columns(2, gap="small")
        for j, col in enumerate(cols):
            idx = i + j
            if idx < len(books):
                with col:
                    _render_book_card(books[idx])
    
    # Action buttons - side by side, same height
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    
    # Use HTML for perfectly aligned buttons
    st.markdown("""
    <div style="display: flex; gap: 0.75rem; justify-content: center; margin-top: 0.5rem;">
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns(2, gap="small")
    with c1:
        if st.button("← Back", use_container_width=True, key="back_btn"):
            st.session_state['page'] = 'home'
            st.rerun()
    with c2:
        if st.button("Get Recommendations →", use_container_width=True, key="rec_btn", type="primary"):
            st.session_state['page'] = 'recommendation'
            st.session_state['generating_recommendations'] = True
            st.rerun()



def _render_book_card(book: dict):
    """Render uniform book card."""
    title = book.get('title', 'Unknown')
    author = normalize_author(book.get('author'))
    cover = book.get('cover_image')
    genres = book.get('genres', [])
    if isinstance(genres, str):
        genres = [genres]
    
    # Smart truncation at word boundary
    if len(title) > 30:
        words = title[:30].rsplit(' ', 1)
        title = words[0] + "…" if len(words) > 1 else title[:27] + "…"
    
    with st.container(border=True):
        c1, c2 = st.columns([1, 4], gap="small")
        
        with c1:
            if cover and cover.startswith('http'):
                st.image(cover, width=55)
            else:
                st.markdown(BOOK_PLACEHOLDER_SVG, unsafe_allow_html=True)
        
        with c2:
            st.markdown(f"**{title}**")
            st.caption(f"by {author}")
            render_tags(genres, max_tags=2)


def _render_analyzing():
    """Render analyzing state."""
    st.markdown("## Analyzing Your Bookshelf")
    st.caption("Detecting books and fetching details...")
    
    progress = st.progress(0)
    status = st.empty()
    
    try:
        status.caption("🔍 Detecting books...")
        progress.progress(20)
        
        image_data = st.session_state.get('uploaded_image')
        if not image_data:
            st.error("No image uploaded")
            st.session_state['analyzing'] = False
            return
        
        detector = GeminiBookDetector()
        detected = detector.detect_books_with_details(image_data)
        progress.progress(45)
        
        if not detected:
            st.warning("No books detected. Try a clearer photo.")
            st.session_state['analyzing'] = False
            if st.button("← Try Again"):
                st.session_state['page'] = 'home'
                st.rerun()
            return
        
        st.session_state['raw_titles'] = detected
        status.caption(f"📚 Found {len(detected)} books...")
        
        metadata_service = get_metadata_service()
        books = metadata_service.get_multiple_books(detected)
        progress.progress(75)
        
        status.caption("💭 Classifying mood...")
        
        mood_text = st.session_state.get('mood_text', '')
        classifier = get_mood_classifier()
        mood_result = classifier.classify(mood_text)
        progress.progress(100)
        
        st.session_state['detected_books'] = books
        st.session_state['mood_classification'] = mood_result
        st.session_state['analyzing'] = False
        
        import time
        time.sleep(0.2)
        st.rerun()
        
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.session_state['analyzing'] = False
