"""
Book Card Component - Enhanced UI
Premium book cards with animations and visual effects.
"""

import streamlit as st
from typing import Dict, Any


def render_book_card(book: Dict[str, Any], 
                     show_score: bool = False,
                     show_actions: bool = False,
                     compact: bool = False,
                     animation_delay: float = 0) -> None:
    """
    Render a premium glass book card.
    
    Args:
        book: Book metadata dictionary
        show_score: Whether to show recommendation score
        show_actions: Whether to show accept/reject buttons
        compact: Use compact layout
        animation_delay: Animation delay in seconds for staggered reveal
    """
    title = book.get('title', 'Unknown Title')
    author = book.get('author', 'Unknown Author')
    cover_image = book.get('cover_image')
    rating = book.get('rating') or 0
    page_count = book.get('page_count') or 0
    genres = book.get('genres', [])
    if isinstance(genres, str):
        genres = [genres]
    description = book.get('description', '')
    score = book.get('score_percentage') or 0
    
    # Filter valid genres
    valid_genres = [g for g in genres[:3] if g and str(g).strip()]
    genre_html = ''.join([f'<span class="genre-tag">{g}</span>' for g in valid_genres]) if valid_genres else '<span class="genre-tag">Fiction</span>'
    
    # Rating stars
    if rating and float(rating) > 0:
        full_stars = min(int(float(rating)), 5)
        rating_html = f'<span class="rating-stars">{"★" * full_stars}{"☆" * (5 - full_stars)}</span> ({float(rating):.1f})'
    else:
        rating_html = ''
    
    # Score circle for high scores
    score_html = ''
    if show_score and score and score > 0:
        score_html = f'<div class="score-badge">{score:.0f}%</div>'
    
    # Page info
    page_html = f'<span style="color: var(--text-muted); font-size: 0.85rem;">📄 {page_count} pages</span>' if page_count and int(page_count) > 0 else ''
    
    # Cover or placeholder
    if cover_image:
        cover_html = f'<img src="{cover_image}" class="book-cover" style="width: 100%; max-width: 120px; height: auto; border-radius: 8px;">'
    else:
        cover_html = '''
        <div style="width: 100px; height: 140px; background: linear-gradient(135deg, rgba(99,102,241,0.2), rgba(139,92,246,0.2)); 
                    border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 2rem;">
            📚
        </div>
        '''
    
    # Build card HTML
    card_html = f'''
    <div class="book-card" style="animation-delay: {animation_delay}s;">
        <div style="display: flex; gap: 1rem; {'flex-direction: column; align-items: center; text-align: center;' if compact else ''}">
            <div style="flex-shrink: 0;">
                {cover_html}
            </div>
            <div style="flex-grow: 1; min-width: 0;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 0.5rem; margin-bottom: 0.5rem;">
                    <div style="min-width: 0;">
                        <h4 style="margin: 0; font-size: 1rem; font-weight: 600; color: var(--text-primary); 
                                   overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{title}</h4>
                        <p style="margin: 0.25rem 0 0; font-size: 0.875rem; color: var(--text-secondary);">by {author}</p>
                    </div>
                    {score_html}
                </div>
                <div style="margin: 0.5rem 0;">
                    {genre_html}
                </div>
                <div style="display: flex; gap: 1rem; align-items: center; flex-wrap: wrap;">
                    {rating_html}
                    {page_html}
                </div>
            </div>
        </div>
    </div>
    '''
    
    st.markdown(card_html, unsafe_allow_html=True)


def render_book_grid(books: list, 
                    show_scores: bool = False,
                    columns: int = 2) -> None:
    """
    Render books in a grid layout with staggered animations.
    """
    cols = st.columns(columns)
    
    for idx, book in enumerate(books):
        with cols[idx % columns]:
            render_book_card(book, show_score=show_scores, compact=False, animation_delay=idx * 0.1)


def render_top_recommendation(book: Dict[str, Any], 
                             explanation: Dict[str, Any] = None) -> None:
    """
    Render the top recommendation with premium styling.
    """
    title = book.get('title', 'Unknown Title')
    author = book.get('author', 'Unknown Author')
    cover_image = book.get('cover_image')
    rating = book.get('rating') or 0
    page_count = book.get('page_count') or 0
    genres = book.get('genres', [])
    if isinstance(genres, str):
        genres = [genres]
    description = book.get('description', '')
    score = book.get('score_percentage') or 0
    
    # Header
    st.markdown("""
    <div style="text-align: center; margin-bottom: 1.5rem; animation: fadeInDown 0.5s ease;">
        <span style="font-size: 0.9rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 3px;">
            🏆 Top Recommendation
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if cover_image:
            st.markdown(f"""
            <div style="text-align: center; animation: fadeInScale 0.5s ease;">
                <img src="{cover_image}" class="book-cover" 
                     style="width: 100%; max-width: 200px; border-radius: 12px; 
                            box-shadow: 0 20px 40px rgba(0,0,0,0.4);">
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="width: 180px; height: 260px; margin: 0 auto;
                        background: linear-gradient(135deg, rgba(99,102,241,0.3), rgba(139,92,246,0.3));
                        border-radius: 12px; display: flex; align-items: center; justify-content: center;
                        font-size: 4rem; box-shadow: 0 20px 40px rgba(0,0,0,0.4);">
                📚
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        # Score circle
        if score and score > 0:
            offset = 283 - (283 * score / 100)
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
                <div style="animation: slideInLeft 0.5s ease;">
                    <h2 style="margin: 0; font-size: 1.75rem; color: var(--text-primary);">{title}</h2>
                    <p style="font-size: 1.1rem; margin: 0.25rem 0; color: var(--text-secondary);">by {author}</p>
                </div>
                <div class="score-circle" style="width: 80px; height: 80px; animation: fadeInScale 0.5s ease 0.2s backwards;">
                    <svg width="80" height="80" viewBox="0 0 100 100" style="transform: rotate(-90deg);">
                        <defs>
                            <linearGradient id="scoreGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" stop-color="#6366f1"/>
                                <stop offset="100%" stop-color="#a855f7"/>
                            </linearGradient>
                        </defs>
                        <circle cx="50" cy="50" r="45" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="8"/>
                        <circle cx="50" cy="50" r="45" fill="none" stroke="url(#scoreGrad)" stroke-width="8" 
                                stroke-linecap="round" stroke-dasharray="283" stroke-dashoffset="{offset}"
                                style="animation: scoreReveal 1.5s ease forwards;"/>
                    </svg>
                    <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
                                font-size: 1.25rem; font-weight: 700; 
                                background: linear-gradient(135deg, #6366f1, #a855f7);
                                -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                        {score:.0f}%
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="animation: slideInLeft 0.5s ease;">
                <h2 style="margin: 0; font-size: 1.75rem; color: var(--text-primary);">{title}</h2>
                <p style="font-size: 1.1rem; margin: 0.25rem 0; color: var(--text-secondary);">by {author}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Genres
        valid_genres = [g for g in genres[:4] if g and str(g).strip()]
        if valid_genres:
            genre_html = ''.join([f'<span class="genre-tag">{g}</span>' for g in valid_genres])
            st.markdown(f'<div style="margin: 1rem 0; animation: fadeIn 0.5s ease 0.3s backwards;">{genre_html}</div>', unsafe_allow_html=True)
        
        # Rating and pages
        info_parts = []
        if rating and float(rating) > 0:
            stars = "★" * min(int(float(rating)), 5) + "☆" * (5 - min(int(float(rating)), 5))
            info_parts.append(f'<span class="rating-stars">{stars}</span> ({float(rating):.1f})')
        if page_count and int(page_count) > 0:
            info_parts.append(f'📄 {page_count} pages')
        
        if info_parts:
            st.markdown(f'''
            <div style="display: flex; gap: 1.5rem; margin: 1rem 0; font-size: 0.95rem; 
                        animation: fadeIn 0.5s ease 0.4s backwards;">
                {" ".join(info_parts)}
            </div>
            ''', unsafe_allow_html=True)
        
        # Description
        if description:
            desc_text = str(description)[:350] + "..." if len(str(description)) > 350 else str(description)
            st.markdown(f'''
            <p style="font-size: 0.95rem; line-height: 1.7; color: var(--text-secondary);
                      animation: fadeIn 0.5s ease 0.5s backwards;">
                {desc_text}
            </p>
            ''', unsafe_allow_html=True)
    
    # Explanation box
    if explanation:
        main_exp = explanation.get('main_explanation', '')
        if main_exp:
            st.markdown(f"""
            <div class="explanation-box" style="animation: slideInLeft 0.5s ease 0.6s backwards;">
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                    <span style="font-size: 1.25rem;">💡</span>
                    <strong style="color: var(--accent-primary);">Why this book?</strong>
                </div>
                <p style="margin: 0; font-size: 0.95rem; color: var(--text-secondary);">{main_exp}</p>
            </div>
            """, unsafe_allow_html=True)
