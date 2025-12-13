"""
Recommendation Page - Polished Layout
Fixed: uniform cards, proper button alignment, no broken input, consistent spacing.
"""

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.recommendation import get_book_scorer, get_explainer
from src.rl import get_q_learning_agent, save_agent, load_agent
from src.database import get_supabase_repository
from src.metadata import get_cover_generator
from src.auth import get_current_user, is_authenticated
from src.ui.styles import (
    render_score_ring, render_progress_bar, render_tags, 
    normalize_author, normalize_genre, BOOK_PLACEHOLDER_LARGE, BOOK_PLACEHOLDER_SMALL
)


def render_recommendation_page():
    """Render recommendation with polished layout."""
    
    if st.session_state.get('generating_recommendations', False):
        _render_generating()
        return
    
    recommendations = st.session_state.get('recommendations', [])
    
    if not recommendations:
        st.markdown("## No Recommendations")
        st.caption("Upload books first to get recommendations.")
        if st.button("← Home"):
            st.session_state['page'] = 'home'
            st.rerun()
        return
    
    idx = st.session_state.get('current_recommendation_index', 0)
    if idx >= len(recommendations):
        idx = 0
        st.session_state['current_recommendation_index'] = 0
    
    book = recommendations[idx]
    mood = st.session_state.get('mood_classification', {})
    explainer = get_explainer()
    explanation = explainer.explain(book, mood)
    
    # Section label
    st.caption("YOUR RECOMMENDATION")
    
    # Main card
    with st.container(border=True):
        c1, c2 = st.columns([1, 2], gap="medium")
        
        with c1:
            # Book cover - generate SVG if no cover
            cover = book.get('cover_image')
            cover_url = None
            
            if cover and (cover.startswith('http') or cover.startswith('data:')):
                cover_url = cover
            else:
                # Generate dynamic SVG cover (instant, no API)
                try:
                    generator = get_cover_generator()
                    title = book.get('title', 'Unknown')
                    author = book.get('author', 'Unknown')
                    genre = normalize_genre(book.get('genre', 'Fiction'))
                    cover_url = generator.get_cover_url(title, author, genre, width=110, height=160)
                    book['cover_image'] = cover_url  # Cache it
                except:
                    pass
            
            if cover_url:
                st.markdown(f"""
                <div style="display: flex; justify-content: center;">
                    <img src="{cover_url}" style="width: 110px; height: auto; border-radius: 6px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);" />
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(BOOK_PLACEHOLDER_LARGE, unsafe_allow_html=True)
            
            # Score right below cover
            score = book.get('score_percentage') or 0
            st.markdown("<div style='height: 0.4rem;'></div>", unsafe_allow_html=True)
            render_score_ring(score, 48)
            st.caption("Match")
        
        with c2:
            title = book.get('title', 'Unknown')
            author = normalize_author(book.get('author'))
            genres = book.get('genres', [])
            if isinstance(genres, str):
                genres = [genres]
            desc = book.get('description', '')
            pages = book.get('page_count') or 0
            
            # Title
            st.markdown(f"## {title}")
            st.caption(f"by {author}")
            
            # Tags - max 2
            render_tags(genres, max_tags=2)
            
            if pages and int(pages) > 0:
                st.caption(f"{pages} pages")
            
            # Description - compact
            if desc:
                short = str(desc)[:150] + "…" if len(str(desc)) > 150 else str(desc)
                st.markdown(f"<p style='font-size: 0.8rem; line-height: 1.5; color: #909090; margin: 0.4rem 0; max-width: 380px;'>{short}</p>", unsafe_allow_html=True)
            
            # AI explanation - subtle, compact but readable
            main_exp = explanation.get('main_explanation', '')
            if main_exp:
                # Show more text (200 chars instead of 120)
                display_text = main_exp[:200] + '…' if len(main_exp) > 200 else main_exp
                st.markdown(f"""
                <div style="background: rgba(80,120,160,0.06); border-radius: 6px; 
                            padding: 0.5rem 0.7rem; margin-top: 0.4rem; max-width: 400px;">
                    <span style="font-size: 0.8rem; color: #999; line-height: 1.4;">💭 {display_text}</span>
                </div>
                """, unsafe_allow_html=True)
    
    # Action buttons - equal width, same height (no wrapper divs)
    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
    
    b1, b2, b3 = st.columns(3, gap="small")
    with b1:
        if st.button("⏭ Skip", use_container_width=True, key="skip_btn"):
            _feedback(book, False)
    with b2:
        if st.button("→ Next", use_container_width=True, key="next_btn"):
            _next()
    with b3:
        if st.button("✓ Read This", use_container_width=True, key="read_btn", type="primary"):
            _feedback(book, True)
    
    # Score breakdown - inline, no expander (removes keyboard helper)
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    scores = book.get('scores', {})
    mood_val = scores.get('mood_match', 0) * 100
    genre_val = scores.get('genre_preference', 0) * 100
    pop_val = scores.get('popularity', 0) * 100
    
    st.markdown(f"""
    <div style="display: flex; gap: 1.5rem; font-size: 0.75rem; color: #888;">
        <span>🎭 Mood: {mood_val:.0f}%</span>
        <span>📚 Genre: {genre_val:.0f}%</span>
        <span>⭐ Popular: {pop_val:.0f}%</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Other options - uniform cards
    if len(recommendations) > 1:
        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        st.caption("OTHER OPTIONS")
        
        others = [r for i, r in enumerate(recommendations) if i != idx][:3]
        cols = st.columns(len(others), gap="small")
        
        for i, bk in enumerate(others):
            with cols[i]:
                _render_mini_card(bk, i, recommendations)
    
    # Navigation - centered
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    
    n1, n2 = st.columns(2, gap="small")
    with n1:
        if st.button("← Scan More", use_container_width=True):
            _reset()
            st.session_state['page'] = 'home'
            st.rerun()
    with n2:
        if st.button("📜 History", use_container_width=True):
            st.session_state['page'] = 'history'
            st.rerun()


def _render_mini_card(bk: dict, i: int, recommendations: list):
    """Render uniform mini card with fixed dimensions."""
    with st.container(border=True):
        # Fixed-size cover container
        cover = bk.get('cover_image')
        cover_html = None
        
        if cover and (cover.startswith('http') or cover.startswith('data:')):
            cover_html = f'<img src="{cover}" style="height: 75px; width: auto; object-fit: contain; border-radius: 4px;" />'
        else:
            # Generate dynamic SVG cover (instant)
            try:
                generator = get_cover_generator()
                title = bk.get('title', 'Unknown')
                author = bk.get('author', 'Unknown')
                genre = normalize_genre(bk.get('genre', 'Fiction'))
                svg_cover = generator.get_cover_url(title, author, genre, width=55, height=80)
                cover_html = f'<img src="{svg_cover}" style="height: 75px; width: auto; object-fit: contain; border-radius: 4px;" />'
                bk['cover_image'] = svg_cover  # Cache
            except:
                pass
        
        if cover_html:
            st.markdown(f"""
            <div style="height: 80px; display: flex; align-items: center; justify-content: center; overflow: hidden;">
                {cover_html}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="height: 80px; display: flex; align-items: center; justify-content: center;">
                {BOOK_PLACEHOLDER_SMALL}
            </div>
            """, unsafe_allow_html=True)
        
        # Fixed-height title container
        title = bk.get('title', 'Unknown')
        if len(title) > 14:
            title = title[:11] + "…"
        score = bk.get('score_percentage') or 0
        
        st.markdown(f"""
        <div style="height: 45px; overflow: hidden;">
            <p style="margin: 0; font-weight: 600; font-size: 0.85rem; line-height: 1.3;">{title}</p>
            <p style="margin: 0; font-size: 0.7rem; color: #888;">{score:.0f}% match</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("View", key=f"v_{i}", use_container_width=True):
            for j, r in enumerate(recommendations):
                if r.get('title') == bk.get('title'):
                    st.session_state['current_recommendation_index'] = j
                    break
            st.rerun()



def _render_generating():
    """Render generating state."""
    st.markdown("## Finding Your Perfect Read")
    st.caption("Analyzing preferences...")
    
    progress = st.progress(0)
    
    try:
        books = st.session_state.get('detected_books', [])
        mood = st.session_state.get('mood_classification', {})
        
        if not books:
            st.error("No books to recommend")
            st.session_state['generating_recommendations'] = False
            return
        
        progress.progress(25)
        
        scorer = get_book_scorer()
        
        # Use session state for preferences (cloud-friendly)
        genre_prefs = st.session_state.get('genre_preferences', {})
        history = st.session_state.get('reading_history_titles', [])
        
        scorer.set_user_preferences(genre_preferences=genre_prefs, reading_history=history)
        scored = scorer.score_books(books, mood)
        
        progress.progress(60)
        
        agent = get_q_learning_agent()
        adjusted = agent.adjust_book_scores(scored, mood.get('primary_mood', 'curious'))
        
        progress.progress(100)
        
        st.session_state['recommendations'] = adjusted
        st.session_state['current_recommendation_index'] = 0
        st.session_state['generating_recommendations'] = False
        
        import time
        time.sleep(0.15)
        st.rerun()
        
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.session_state['generating_recommendations'] = False


def _feedback(book: dict, accepted: bool):
    """Record feedback to Supabase for per-user storage."""
    mood = st.session_state.get('mood_classification', {})
    primary_mood = mood.get('primary_mood', 'curious')
    
    # Clean up genre name (handles raw API metadata)
    genre = normalize_genre(book.get('genre', 'Fiction'))
    
    # Save to Supabase for authenticated users
    user = get_current_user()
    if user and not user.get('guest'):
        try:
            supabase_repo = get_supabase_repository()
            
            # Record feedback
            supabase_repo.add_feedback(
                book_title=book.get('title', 'Unknown'),
                genre=genre,
                mood=primary_mood,
                accepted=accepted,
                score=book.get('total_score', 0)
            )
            
            # Add to history if accepted
            if accepted:
                supabase_repo.add_to_history(
                    title=book.get('title', 'Unknown'),
                    author=book.get('author'),
                    genre=genre,
                    mood=primary_mood,
                    score=book.get('total_score', 0),
                    metadata=book
                )
        except Exception as e:
            st.warning(f"Could not save to cloud: {e}")
    
    # Track history in session for RL learning
    if 'reading_history_titles' not in st.session_state:
        st.session_state['reading_history_titles'] = []
    if accepted:
        st.session_state['reading_history_titles'].append(book.get('title', 'Unknown'))
    
    if accepted:
        st.balloons()
        st.success("✓ Added to reading list!")
    
    # Update RL agent
    agent = get_q_learning_agent()
    load_agent(agent)
    agent.record_feedback(primary_mood, genre, accepted)
    save_agent(agent)
    
    if not accepted:
        _next()



def _next():
    """Next recommendation."""
    recs = st.session_state.get('recommendations', [])
    idx = st.session_state.get('current_recommendation_index', 0)
    st.session_state['current_recommendation_index'] = (idx + 1) % len(recs)
    st.rerun()


def _reset():
    """Reset session."""
    for k in ['uploaded_image', 'image_name', 'mood_text', 'selected_mood', 
              'detected_books', 'mood_classification', 'recommendations', 
              'current_recommendation_index', 'raw_titles']:
        st.session_state.pop(k, None)
